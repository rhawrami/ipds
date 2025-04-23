import concurrent.futures
import time
import random
import requests
import zipfile
import os
import warnings


DATASETS = {

    'characteristics' : {
        'dir' : 'characteristicsdata',
        'file_prefix' : 'characteristics',
        'format_rules' : [
            (lambda y : y <= 1985, 'IC{year}'),
            (lambda y : (1985 < y <= 1989) or (1991 < y <= 1994), 'IC{year}_A'),
            (lambda y : y == 1990,  'IC90HD'), 
            (lambda y : y == 1991,  'IC1991_hdr'),
            (lambda y : 1994 < y < 1997, 'ic{lag0}{lead1}_A'), # check later
            (lambda y : y == 1997, 'ic9798_HDR'), 
            (lambda y : y == 1998, 'IC98hdac'),
            (lambda y : y == 1999, 'IC99_HD'),
            (lambda y : y == 2000 or y == 2001, 'FA{year}HD'),
            (lambda y : y >= 2002, 'HD{year}')
        ]
    },

    'admissions' : {
        'dir' : 'admissionsdata',
        'file_prefix' : 'admissions',
        'format_rules' : [
            (lambda y: 2001 <= y <= 2013, 'IC{year}'),
            (lambda y: 2014 <= y <= 2023, 'ADM{year}'), 
        ]
    },

    'enrollment' : {
        'dir' : 'enrollmentdata',
        'file_prefix' : 'enrollment',
        'format_rules' : [
            (lambda y: y <= 1985, 'EF{year}'),
            (lambda y: (1985 < y < 1990) or (1991 < y < 1994), 'EF{year}_A'),
            (lambda y: y == 1990, 'EF90_A'),
            (lambda y: y == 1991, 'ef1991_A'),
            (lambda y: y == 1994,  'EF{year}_ANR'),
            (lambda y: 1994 < y < 2000, 'EF{lag0}_ANR'),
            (lambda y: y >= 2000, 'EF{year}A')
        ]
    },

    'completion' : {
        'dir' : 'completiondata',
        'file_prefix' : 'completion',
        'format_rules' : [
            (lambda y: y < 1990 or (1991 < y < 1995), 'C{year}_CIP'),
            (lambda y: y == 1990, 'C8990CIP'),
            (lambda y: y == 1991, 'c1991_cip'),
            (lambda y: 1995 <= y < 2000, 'C{lag1}{lag0}_A'),
            (lambda y: y >= 2000, 'C{year}_A')
        ]
    },

    'graduation' : {
        'dir' : 'graduationdata',
        'file_prefix' : 'graduation',
        'format_rules' : [
            (lambda y: y in range(2000,2024), 'GR{year}')
        ]
    },

    'cip' : {
        'dir' : 'cipdata',
        'file_prefix' : 'cip',
        'format_rules' : [
            (lambda y: (y < 1990) or (1991 < y < 1995), 'C{year}_CIP'),
            (lambda y: y == 1990, 'C8990CIP'),
            (lambda y: y == 1991, 'c1991_cip'),
            (lambda y: 1995 <= y < 2000, 'C{lag1}{lag0}_A'),
            (lambda y: y >= 2000, 'C{year}_A')
        ]
    }

}


def download_year(year, subject_info, subject, download_year):
    """Download data for a specific year and subject"""
    relevant_dir = subject_info['dir']
    relevant_prefix = subject_info['file_prefix']
    
    lag0, lag1, lead1 = year-1900, year-1901, year-1899  # needed for some years
    
    # Find the correct format rule
    for cond, frmt in subject_info['format_rules']:
        if cond(year):
            yr_format = frmt.format(year=year, 
                                    lag0=str(lag0), 
                                    lag1=str(lag1), 
                                    lead1=str(lead1))
            break
    else:
        raise ValueError(f'No formatted rule for year {year}')
    
    # Use different templates based on subject
    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    file_template_cip = 'https://nces.ed.gov/ipeds/datacenter/data/{}_Dict.zip'  # cip dictionaries
    
    if subject == 'cip':
        file_name = file_template_cip.format(yr_format)
    else:
        file_name = file_template.format(yr_format)  # get file name for requests GET
    
    try:
        r = requests.get(file_name)  # try request
    except requests.HTTPError as er:
        return f"Year {year}: Error - {str(er)}"
        
    if '404 - File or directory not found' in r.text:
        return f"Year {year}: 404 - File not found"
    
    zipped_file = f'{relevant_dir}/{relevant_prefix}_{year}.zip'
    open(zipped_file, 'wb').write(r.content)
    
    with zipfile.ZipFile(zipped_file, 'r') as zfile:
        if subject == 'cip':
            file_to_extract = file_name.split('/')[-1].replace('_Dict.zip', '').lower()
            for ext in ['.html', '.xls', '.xlsx']:  # diff file formats, try each one
                try:
                    zfile.extract(file_to_extract + ext, relevant_dir)
                    os.rename(f'{relevant_dir}/{file_to_extract}{ext}', f'{relevant_dir}/cipcodes_{year}' + ext)
                    os.remove(zipped_file)
                    break
                except KeyError:
                    continue
        else:
            file_to_extract = file_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
            zfile.extract(file_to_extract, relevant_dir)
            # remove & remove zipped file
            os.rename(f'{relevant_dir}/{file_to_extract}', f'{relevant_dir}/{relevant_prefix}_{year}.csv')
            os.remove(zipped_file)
    
    return f"Year {year}: Successfully downloaded and extracted"

def scrape_ipeds_data(subject='characteristics', year_range=None, see_progress=True, max_workers=5):
    '''downloads NCES IPEDS data on specified years for a defined subject with parallel processing.
    
    :subject: string identifying which subject data to download. Available subjects:
      ['characteristics', 'admissions', 'enrollment', 'completion', 'cip', 'graduation']
    
    :year_range: tuple of year integers (range), iterable of year integers, or single year
    
    :see_progress: boolean that, when true, prints completion statement for each year
    
    :max_workers: maximum number of parallel downloads to run simultaneously
    '''
    subject_info = DATASETS[subject]  # get relevant info based on data
    relevant_dir = subject_info['dir']
    os.makedirs(subject_info['dir'], exist_ok=True)  # make dir for downloaded files
    
    # Determine the years to download
    if not year_range:
        if subject == 'graduation':
            start, end = 2000, 2023
            iter_range = range(start, end + 1)  # default for graduation data
        elif subject == 'admissions':
            start, end = 2001, 2023
            iter_range = range(start, end + 1)  # default for admissions data
        else:
            start, end = 1984, 2023
            iter_range = range(start, end + 1)  # default for all other data
    else:
        if isinstance(year_range, tuple):
            start, end = year_range
            iter_range = range(start, end + 1)  # tuple follows regular range
        elif isinstance(year_range, list):
            iter_range = year_range  # list remains list
        elif isinstance(year_range, int):
            start = year_range
            iter_range = [start]  # integer becomes one-element list
        else:
            raise ValueError('Please enter a tuple range, list of integers, or a single integer')
    
    # Use ThreadPoolExecutor for parallel downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit downloads for all years
        future_to_year = {
            executor.submit(download_year, year, subject_info, subject, see_progress): year 
            for year in iter_range
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_year):
            year = future_to_year[future]
            try:
                result = future.result()
                if see_progress:
                    print(result)
                # Adding a small random delay between submissions to avoid overwhelming the server
                time.sleep(random.uniform(0.1, 0.3))
            except Exception as e:
                print(f"Year {year} generated an exception: {e}")


def scrapeOG_ipeds_data(subject = 'characteristics', year_range = None, see_progress=True):
    '''downloads NCES IPEDS data on specified years for a defined subject.
    
    :subject: string identifying which subject data to download. The subjects available are:

    ['characteristics', 'admissions', 'enrollment', 'completion', 'cip', 'graduation']

    - :characteristics: institutional characteristics, like a school's name, address. Certain variables, like a school's longitude and latitude are only available in later years. Available for years 1984-2023.

    - :admissions: Admissions data, like number of applications and acceptances by gender. Available for years 2001-2023.

    - :enrollment: fall enrollment by gender and institutional level (e.g., 4-year undergraduate program), with most years including enrollment by race and gender. Available for years 1984-2023.

    - :completion: completion of degrees by gender, level of degree and subject field (e.g., Bachelor's in Economics), with most years including completion by race and gender. Available for years 1984-2023.

    - :cip: CIP, or Classification of Instructional Programs, are key-value pairs for subject study fields. CIP's vary by year, and are relevant to identify subject field in completion data. Available for years 1984-2023.

    - :graduation: number of cohorts and graduates by gender, institutional level and graduation measure (e.g., students earning a bachelor's degree within 6 years of entering). Available for years 2000-2023.

    :year_range: tuple of year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data for 'characteristics', 'enrollment' and 'completion' are available for years 1984-2023, while 'graduation' is available for years 2000-2023. Defaults to all available years for a subject.

    :see_progress: boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.

    example use:

    `scrape_ipeds_data(subject = 'enrollment', year_range = (1990, 2022))`     # downloads enrollment data from 1990 to 2023
    '''
    subject_info = DATASETS[subject]        # get relevant info based on data
    relevant_dir = subject_info['dir']
    relevant_prefix = subject_info['file_prefix']
    os.makedirs(subject_info['dir'], exist_ok=True)     # make dir for downloaded files

    if not year_range:
        if subject == 'graduation':
            start, end = 2000,2023
            iter_range = range(start, end + 1)      # default for graduation data
        elif subject == 'admissions':
            start, end = 2001,2023
            iter_range = range(start, end + 1)      # default for admissions data
        else:
            start, end = 1984, 2023
            iter_range = range(start, end + 1)      # default for all other data
    else:
        if isinstance(year_range, tuple):
            start, end = year_range             
            iter_range = range(start, end + 1)      # tuple follows regular range
        elif isinstance(year_range, list):
            iter_range = year_range             # list remains list
        elif isinstance(year_range, int):
            start = year_range
            iter_range = [start]        # integer becomes one-element list
        else:
            raise ValueError('Please enter a tuple range, list of integers, or a single integer')
    
    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    file_template_cip = 'https://nces.ed.gov/ipeds/datacenter/data/{}_Dict.zip'     # cip dictionaries

    for year in iter_range:

        lag0, lag1, lead1 = year-1900, year-1901, year-1899     # needed for some years

        for cond,frmt in subject_info['format_rules']:
            if cond(year):
                yr_format = frmt.format(year=year, 
                                        lag0=str(lag0), 
                                        lag1 = str(lag1), 
                                        lead1 = str(lead1))
                break
        else:
            raise ValueError(f'No formatted rule for year {year}')
                
        if subject == 'cip':
            file_name = file_template_cip.format(yr_format)
        else:
            file_name = file_template.format(yr_format)     # get file name for requests GET

        try:
            r = requests.get(file_name)     # try request
        except requests.HTTPError as er:
            print(er)
            continue
        if '404 - File or directory not found' in r.text:
            warnings.warn(f'{year} : 404 - File or directory not found')
            continue
        else:
            zipped_file = f'{relevant_dir}/{relevant_prefix}_{year}.zip'
            open(zipped_file, 'wb').write(r.content)

        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            if subject == 'cip':
                file_to_extract = file_name.split('/')[-1].replace('_Dict.zip', '').lower()
                for ext in ['.html', '.xls', '.xlsx']:  # diff file formats, try each one, most of the early years have .html
                    try:
                        zfile.extract(file_to_extract + ext, relevant_dir)
                        os.rename(f'{relevant_dir}/{file_to_extract}{ext}', f'{relevant_dir}/cipcodes_{year}' + ext)
                        os.remove(zipped_file)
                        break
                    except KeyError:
                        continue
            else:
                file_to_extract = file_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
                zfile.extract(file_to_extract, relevant_dir)
                # remove & remove zipped file
                os.rename(f'{relevant_dir}/{file_to_extract}', f'{relevant_dir}/{relevant_prefix}_{year}.csv')
                os.remove(zipped_file)
        
        if see_progress:
            print(f'IPEDS {relevant_prefix.title()} ({year}) pulled and extracted')
        time.sleep(random.uniform(.1,.3))       # give gov. servers a short break, sorry NCES!


if __name__ == '__main__':
    time1 = time.time()
    scrape_ipeds_data('enrollment', (1984,2023), True, 5)
    scrape_ipeds_data('graduation', (1984,2023), True, 5)
    #scrapeOG_ipeds_data('enrollment', (1984,2023), True)
    time2 = time.time()
    print(f'time alloted: {time2 - time1}')