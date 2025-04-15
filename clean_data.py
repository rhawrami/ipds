import os
import pandas as pd
import numpy as np
import re


def clean_enrollment(enroll_dir = 'enrolldata', by_race = False):
    '''cleans yearly enrollment data and returns complete undergraduate enrollment data

    :enroll_dir:        directory where raw enrollment data is
    :by_race:           boolean set to True if pulling data by race  
    '''
    sorted_files = sorted(os.listdir(enroll_dir)) # unnecessary, but helps with error checking
    
    if by_race:
        master_df = pd.DataFrame(columns=['unitid', 'men', 'women', # total
                                                    'wt_men', 'wt_women', # white
                                                    'bk_men', 'bk_women', # black
                                                    'hsp_men', 'hsp_women', # hispanic
                                                    'asn_men', 'asn_women', # asian
                                                    'male_share', 'year'])
    else:
        master_df = pd.DataFrame(columns=['unitid', 'men', 'women', 'male_share', 'year']) # attributes for overall enrollment

    for file in sorted_files:
        file_path = f'{enroll_dir}/{file}'
        df = pd.read_csv(file_path) # read in df
        df = df.rename(str.lower, axis='columns') # some df's have all uppercase, some have all lowercase
        year_num = re.split(r'_|\.', f'{file}')[1]

        if int(year_num) < 2008:
            df_filtered = df.loc[:, ['unitid', 'line', 'efrace15', 'efrace16']]
            df_filtered = df_filtered.rename(columns={'efrace15' : 'men', 'efrace16' : 'women'})
        else:
            df_filtered = df.loc[:, ['unitid', 'line', 'eftotlm', 'eftotlw']]
            df_filtered = df_filtered.rename(columns={'eftotlm' : 'men', 'eftotlw' : 'women'})
        
        if int(year_num) < 1986:
            undergrad_query = 'line == 1 or line == 15' # captures total full-time and total part-time undergrads, respectively
        else:
            undergrad_query = 'line == 8 or line == 22' # captures total full-time and total part-time undergrads, respectively

        undergrads = df_filtered.query(undergrad_query) # filter data to total undergraduates
        undergrads_by_inst = undergrads.groupby('unitid')[['men', 'women']].sum() # sum full-time and part-time students by school
        undergrads_by_inst = undergrads_by_inst.eval('male_share = men / (men + women) * 100').reset_index() # male undergrad share
        undergrads_by_inst['year'] = int(year_num) # get year marker for each set
        master_df = pd.concat([master_df, undergrads_by_inst], ignore_index=True)
    
        

    


if __name__ == '__main__':
    clean_enrollment()