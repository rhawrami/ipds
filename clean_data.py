import os
import pandas as pd
import numpy as np
import re


def clean_enrollment(enroll_dir = 'enrolldata'):
    '''cleans yearly enrollment data and returns complete undergraduate enrollment data

    :enroll_dir:        directory where raw enrollment data is
    '''
    sorted_files = sorted(os.listdir(enroll_dir)) # unnecessary, but helps with error checking
    

    master_df = pd.DataFrame(columns=['unitid', 'totmen', 'totwomen', # total
                                        'wtmen', 'wtwomen', # white
                                        'bkmen', 'bkwomen', # black
                                        'hspmen', 'hspwomen', # hispanic
                                        'asnmen', 'asnwomen', # asian
                                        'totmen_share', 'year',
                                        'totwt_share', 'totbk_share', 'tothsp_share', 'totasn_share'])

    for file in sorted_files:
        file_path = f'{enroll_dir}/{file}'
        df = pd.read_csv(file_path) # read in df
        df = df.rename(str.lower, axis='columns') # some df's have all uppercase, some have all lowercase
        year_num = re.split(r'_|\.', f'{file}')[1]
        
        if int(year_num) in [1985, 1987, 1989]: # enrollment by race not available in these years
            df_filtered = df.loc[:, ['unitid', 'line', 'efrace15', 'efrace16']]
            df_filtered = df_filtered.rename(columns={'efrace15' : 'totmen', 'efrace16' : 'totwomen'})
        elif int(year_num) < 2008:
            df_filtered = df.loc[:, ['unitid', 'line', 'efrace15', 'efrace16',
                                         'efrace11', 'efrace12', # total White men, total White women
                                         'efrace03', 'efrace04', # total Black men, total Black women
                                         'efrace09', 'efrace10', # total Hispanic men, total Hispanic women
                                         'efrace07', 'efrace08']] # total Asian men, total Asian women
            df_filtered = df_filtered.rename(columns={'efrace15' : 'totmen', 'efrace16' : 'totwomen',
                                                          'efrace11' : 'wtmen', 'efrace12' : 'wtwomen',
                                                          'efrace03' : 'bkmen', 'efrace04' : 'bkwomen', 
                                                          'efrace09' : 'hspmen', 'efrace10' : 'hspwomen',
                                                          'efrace07' : 'asnmen', 'efrace08' : 'asnwomen'})
        elif int(year_num) in [2008, 2009]:
            df_filtered = df.loc[:, ['unitid', 'line', 'eftotlm', 'eftotlw',
                                         'efrace11', 'efrace12', # total White men, total White women
                                         'efrace03', 'efrace04', # total Black men, total Black women
                                         'efrace09', 'efrace10', # total Hispanic men, total Hispanic women
                                         'efrace07', 'efrace08']] # total Asian men, total Asian women
            df_filtered = df_filtered.rename(columns={'eftotlm' : 'totmen', 'eftotlw' : 'totwomen',
                                                          'efrace11' : 'wtmen', 'efrace12' : 'wtwomen',
                                                          'efrace03' : 'bkmen', 'efrace04' : 'bkwomen', 
                                                          'efrace09' : 'hspmen', 'efrace10' : 'hspwomen',
                                                          'efrace07' : 'asnmen', 'efrace08' : 'asnwomen'})
        else:
            df_filtered = df.loc[:, ['unitid', 'line', 'eftotlm', 'eftotlw',
                                         'efwhitm', 'efwhitw', # total White men, total White women
                                         'efbkaam', 'efbkaaw', # total Black men, total Black women
                                         'efhispm', 'efhispw', # total Hispanic men, total Hispanic women
                                         'efasiam', 'efasiaw']] # total Asian men, total Asian women
            
            df_filtered = df_filtered.rename(columns={'eftotlm' : 'totmen', 'eftotlw' : 'totwomen',
                                                          'efwhitm' : 'wtmen', 'efwhitw' : 'wtwomen',
                                                          'efbkaam' : 'bkmen', 'efbkaaw' : 'bkwomen', 
                                                          'efhispm' : 'hspmen', 'efhispw' : 'hspwomen',
                                                          'efasiam' : 'asnmen', 'efasiaw' : 'asnwomen'})
            
        if int(year_num) < 1986:
            undergrad_query = 'line == 1 or line == 15' # captures total full-time and total part-time undergrads, respectively
        else:
            undergrad_query = 'line == 8 or line == 22' # captures total full-time and total part-time undergrads, respectively

        undergrads = df_filtered.query(undergrad_query) # filter data to total undergraduates
        
        if 'wtmen' not in undergrads.columns:
            cols_to_sum = ['totmen', 'totwomen']
        else:
            cols_to_sum = ['totmen', 'totwomen', 'wtmen', 'wtwomen','bkmen', 'bkwomen','hspmen', 'hspwomen','asnmen', 'asnwomen']
        undergrads_by_inst = undergrads.groupby('unitid')[cols_to_sum].sum() # sum full-time and part-time students by school
        undergrads_by_inst = undergrads_by_inst.eval('totmen_share = totmen / (totmen + totwomen) * 100').reset_index() # male undergrad share
        undergrads_by_inst['year'] = int(year_num) # get year marker for each set

        if 'wtmen' in undergrads_by_inst.columns:
            for attr in ['wt', 'bk', 'hsp', 'asn']:
                eval_str = f'tot{attr}_share = ({attr}men + {attr}women) / (totmen + totwomen) * 100' # race share breakdowns
                undergrads_by_inst = undergrads_by_inst.eval(eval_str)


        master_df = pd.concat([master_df, undergrads_by_inst], ignore_index=True)
        print(f'{year_num} : data process complete')
    print(f'''\npreview of rhodes college enrollment data:\n{master_df.query("unitid == 221351").
                                                           sort_values(by='year').
                                                           loc[:, ['year','totmen', 'totwomen', 'totmen_share', 'totwt_share']].
                                                           head(41)}\nEND''')
    
    return master_df
        

    


if __name__ == '__main__':
    clean_enrollment()