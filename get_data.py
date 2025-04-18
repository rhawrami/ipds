import requests
import os
import zipfile 
import time

def get_characteristics(dir = 'characteristicsdata'):
    '''downloads IPEDS NCES data on Institutional Characteristics
    
    ## IPEDS Data Center
    
    All data comes from the IPEDS Data Center [here](https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=1984&surveyNumber=1&sid=2e12f11c-398c-4d30-aa9a-266dc84fc6d8&rtid=7). Institutional Characteristics data is available for years 1984-2023.
    
    ### arguments

    :dir:       data directory name (defaults to 'characteristics/')
    '''
    print('START characteristics data download')  # END

    os.makedirs(dir, exist_ok=True)

    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    #different file names
    for i in range(1984, 2024):
        if i <= 1985:
            f_name = file_template.format(f'IC{i}')
        elif (1985 < i <= 1989) or (1991 < i <= 1994):
            f_name = file_template.format(f'IC{i}_A')
        elif i == 1990:
            f_name = file_template.format(f'IC90HD')
        elif i == 1991:
            f_name = file_template.format(f'IC1991_hdr')
        elif 1994 < i <= 1999:
            start_date, end_date = i - 1900, i - 1899
            if i < 1997:
                f_name = file_template.format(f'ic{start_date}{end_date}_A')
            elif i == 1997:
                f_name = file_template.format(f'ic{start_date}{end_date}_HDR')
            elif i == 1998:
                f_name = file_template.format(f'IC{start_date}hdac')
            else:
                f_name = file_template.format(f'IC{start_date}_HD')
        elif i == 2000 or i == 2001:
            f_name = file_template.format(f'FA{i}HD')
        else:
            f_name = file_template.format(f'HD{i}')
        # get zipped file
        try:
            r = requests.get(f_name)
        except requests.HTTPError as er:
            print(er)
            continue
        if '404 - File or directory not found' in r.text:
            continue
        else:
            zipped_file = f'{dir}/characteristics_{i}.zip'
            open(zipped_file, 'wb').write(r.content)
            
        # next, extracting CSV files from each zipped folder
        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            file_to_extract = f_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
            zfile.extract(file_to_extract, dir)
            
        
        # remove & remove zipped file
        os.rename(f'{dir}/{file_to_extract}', f'{dir}/characteristics_{i}.csv')
        os.remove(zipped_file)
        
    print('END characteristics data download')  # END
    

# Fall Enrollment
# link here : https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=1984&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7
# file format : https://nces.ed.gov/ipeds/datacenter/data/[VARIABLE].zip
def get_enrollment(dir = 'enrolldata'):
    '''downloads IPEDS NCES data on Fall Enrollment by institution.
    # School-Level Enrollment Data

    ## IPEDS Data Center
    
    All data comes from the IPEDS Data Center [here](https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?gotoReportId=7&fromIpeds=true&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7). Enrollment data is available for years 1984-2023. This function downloads Fall enrollment data by race/ethnicity, gender, attendance status and level of student.
    
    ### arguments

    :dir:       data directory name (defaults to 'enrolldata/')
    '''
    print('START fall enrollment data download')  # END

    os.makedirs(dir, exist_ok=True)

    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    # so many different file formats
    for i in range(1984, 2024):
        if i <= 1985:
            f_name = file_template.format(f'EF{i}')
        elif (1985 < i < 1990) or (1991 < i < 1994):
            f_name = file_template.format(f'EF{i}_A')
        elif i == 1990:
            f_name = file_template.format(f'EF90_A')
        elif i == 1991:
            f_name = file_template.format(f'ef1991_A')
        elif 1994 <= i < 2000:
            if i == 1994:
                f_name = file_template.format(f'EF{i}_ANR')
            else:
                i_reset = i - 1900
                f_name = file_template.format(f'EF{i_reset}_ANR')
        elif i >= 2000:
            f_name = file_template.format(f'EF{i}A')
        # get zipped file
        try:
            r = requests.get(f_name)
        except requests.HTTPError as er:
            print(er)
            continue
        if '404 - File or directory not found' in r.text:
            continue
        else:
            zipped_file = f'{dir}/enrollment_{i}.zip'
            open(zipped_file, 'wb').write(r.content)
            
        
        # next, extracting CSV files from each zipped folder
        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            file_to_extract = f_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
            zfile.extract(file_to_extract, dir)
            
        
        # remove & remove zipped file
        os.rename(f'{dir}/{file_to_extract}', f'{dir}/fallenroll_{i}.csv')
        os.remove(zipped_file)
        
    print('END fall enrollment data download')  # END
    

# Completions
# link here : https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=2023&surveyNumber=3&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7
# file format : https://nces.ed.gov/ipeds/datacenter/data/[VARIABLE].zip
def get_completion(dir = 'completiondata'):
    '''downloads IPEDS NCES data on Completions by institution.
    # School-Level Completions Data

    ## IPEDS Data Center
    
    All data comes from the IPEDS Data Center [here](https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=2023&surveyNumber=3&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7). Completion data is available for years 1984-2023. This function downloads completions data by subject field, race/ethnicity, gender, attendance status and level of student.
    
    ### arguments

    :dir:       data directory name (defaults to 'completiondata/')
    '''
    print('START completion data download')  # END

    os.makedirs(dir, exist_ok=True)

    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    # different file names
    for i in range(1984, 2024):
        if i < 1990 or (1991 < i < 1995):
            f_name = file_template.format(f'C{i}_CIP')
        elif i == 1990:
            f_name = file_template.format(f'C8990CIP')
        elif i == 1991:
            f_name = file_template.format(f'c1991_cip')
        elif 1995 <= i < 2000:
            start_date = i - 1901
            end_date = i - 1900
            f_name = file_template.format(f'C{start_date}{end_date}_A')
        elif i >= 2000:
            f_name = file_template.format(f'C{i}_A')
        print(f_name)
        # get zipped file
        try:
            r = requests.get(f_name)
        except requests.HTTPError as er:
            print(er)
            continue
        if '404 - File or directory not found' in r.text:
            print(f'{i} Error: File not found')
            continue
        else:
            zipped_file = f'{dir}/completion_{i}.zip'
            open(zipped_file, 'wb').write(r.content)
            

        # next, extracting CSV files from each zipped folder
        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            file_to_extract = f_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
            zfile.extract(file_to_extract, dir)
            
        
        # remove & remove zipped file
        os.rename(f'{dir}/{file_to_extract}', f'{dir}/completion_{i}.csv')
        os.remove(zipped_file)
        
    print('END completion data download')  # END
    


# Graduation (ONLY USING 2000-2023 FOR THIS)
# link here : https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=2023&surveyNumber=3&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7
# file format : https://nces.ed.gov/ipeds/datacenter/data/[VARIABLE].zip
def get_graduation(dir = 'graduationdata'):
    '''downloads IPEDS NCES data on Graduations by institution.
    # School-Level Graduation Data

    ## IPEDS Data Center
    
    All data comes from the IPEDS Data Center [here](https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=2000&surveyNumber=8&sid=ad9c8701-e0d0-43f6-a6a2-c93f26982912&rtid=7). Graduation data is available for years 1999-2023, but we'll round to 2000. This function downloads graduation data.
    
    ### arguments

    :dir:       data directory name (defaults to 'completiondata/')
    '''
    print('START graduation data download')  # END

    os.makedirs(dir, exist_ok=True)
    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}.zip'
    for i in range(2000,2024):
        f_name = file_template.format(f'GR{i}')
        print(f_name)
        # get zipped file
        try:
            r = requests.get(f_name)
        except requests.HTTPError as er:
            print(er)
            continue
        if '404 - File or directory not found' in r.text:
            print(f'{i} Error: File not found')
            continue
        else:
            zipped_file = f'{dir}/graduation_{i}.zip'
            open(zipped_file, 'wb').write(r.content)
            
        
        # next, extracting CSV files from each zipped folder
        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            file_to_extract = f_name.split('/')[-1].replace('.zip', '').lower() + '.csv'
            zfile.extract(file_to_extract, dir)
            
        # remove & remove zipped file
        os.rename(f'{dir}/{file_to_extract}', f'{dir}/graduation_{i}.csv')
        os.remove(zipped_file)
        
    print('END graduation data download')  # END
    


if __name__ == '__main__':

    user_resp = input('''
                 This script returns NCES school-level data from 1984-2023 (but 2000-2024 for Graduation data) on the following topics:\n
                 - Characteristics (like school names, addresses, etc.)
                 - Fall Undergraduate Enrollment (by race and gender)
                 - Degree Completions (by subject gender, subject field, and degree level)
                 - Graduation Rates (by gender, race and level)\n
                 You have the option to selectively choose one of the four sections, or download all of them. Please
                 select and return one of the following strings:\n
                 [ALL, CHARACTERISTICS, ENROLLMENT, COMPLETION, GRADUATION]\n
                 The following data, in CSV format, will be downloaded locally onto a relevant named directory. Thanks!\n
                ENTER RESPONSE:''').lower()
    
    def get_all():
        '''returns all available data, you glutton'''
        print('\n----------STARTING *CHARACTERISTICS* DOWNLOAD----------\n')
        get_characteristics()
        print('\n----------END *CHARACTERISTICS* DOWNLOAD----------\n')
        print('\n----------STARTING *ENROLLMENT* DOWNLOAD----------\n')
        get_enrollment()
        print('\n----------END *ENROLLMENT* DOWNLOAD----------\n')
        print('\n----------STARTING *COMPLETION* DOWNLOAD----------\n')
        get_completion()
        print('\n----------END *COMPLETION* DOWNLOAD----------\n')
        print('\n----------STARTING *GRADUATION* DOWNLOAD----------\n')
        get_graduation()
        print('\n----------END *GRADUATION* DOWNLOAD----------\n')
    
    resp_dict = {
        'all' : get_all, 
        'characteristics' : get_characteristics,
        'enrollment' : get_enrollment,
        'completion' : get_completion,
        'graduation' : get_graduation
    }

    if user_resp not in resp_dict.keys():
        raise ValueError('''Response option is not recognized. Please select from the following option:\n
                         [ALL, CHARACTERISTICS, ENROLLMENT, COMPLETION, GRADUATION]''')
    else:
        resp_dict[user_resp]()