import requests
import os
import zipfile 
import time
import random
import warnings
from config import DATASETS

def scrape_ipeds_data(subject = 'characteristics', year_range = None, see_progress=True):
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
    file_template = subject_info['file_template']
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
                
        file_name = file_template.format(yr_format)   # get file name for requests GET

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




def scrape_all(see_progress=True):
    '''downloads NCES IPEDS data for all subject options, for all available years.
    
    downloads data on: 
    - **institutional characteristics** *(1983-2023)*
    - **fall undergraduate enrollment** *(1983-2023)*
    - **completion by subject field** *(1983-2023)*
    - **CIP subject field codes** *(1983-2023)*
    - **graduation** *(2000-2023)*

    :see_progress: boolean that, prints completion statement for successful extraction per year. If False, no messages printed.
    '''
    scrape_ipeds_data('characteristics')
    scrape_ipeds_data('admissions')
    scrape_ipeds_data('enrollment')
    scrape_ipeds_data('completion')
    scrape_ipeds_data('cip')
    scrape_ipeds_data('graduation')


if __name__ == '__main__':
    user_resp = input('''
                 This script returns NCES school-level data from 1984-2023 (but 2000-2023 for Graduation data and 2001-2023 for Admissions data) on the following topics:\n
                 - Characteristics (like school names, addresses, etc.)
                 - Admissions (like number of acceptances)
                 - Fall Undergraduate Enrollment (by race and gender)
                 - Degree Completions (by subject gender, subject field, and degree level)
                 - Codes for degree completions and their corresponding subject fields
                 - Graduation Rates (by gender, race and level)\n
                 You have the option to selectively choose one of the five sections, or download all of them. Please
                 select and return one of the following strings:\n
                 [ALL, CHARACTERISTICS, ADMISSIONS, ENROLLMENT, COMPLETION, CIP, GRADUATION]\n
                 The following data, in CSV format, will be downloaded locally onto a relevant named directory. Thanks!\n
                ENTER RESPONSE:''').lower()
    
    resp_dict = {
        'all' : scrape_all,
        'characteristics' : scrape_ipeds_data,
        'admissions' : scrape_ipeds_data,
        'enrollment' : scrape_ipeds_data,
        'completion' : scrape_ipeds_data,
        'cip' : scrape_ipeds_data,
        'enrollment' : scrape_ipeds_data
    }

    if user_resp not in resp_dict.keys():
        raise ValueError('''Response option is not recognized. Please select from the following option:\n
                         [ALL, CHARACTERISTICS, ADMISSIONS, ENROLLMENT, COMPLETION, CIP, GRADUATION]''')
    else:
        print(f'OPTION SELECTED : {user_resp.upper()}')
        if user_resp == 'all':
            resp_dict[user_resp]()
        else:
            resp_dict[user_resp](user_resp)
        print(f'END DOWNLOAD STREAM. THANK YOU FOR USING ME :)')