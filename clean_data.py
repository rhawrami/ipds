import os
import re
import pandas as pd

def clean_characteristics(characteristics_dir = 'characteristicsdata'):
    '''cleans institution characteristics data and returns complete characteristics data

    :characteristics_dir:        directory where raw enrollment data is located
    '''
    sorted_files = sorted(os.listdir(characteristics_dir))

    master_df = pd.DataFrame(columns=['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip', 'webaddr', 'longitud', 'latitude'])

    dtypes = {
        'unitid' : 'int', 'instnm' : 'str', 'addr' : 'str', 'city' : 'str', 
        'stabbr' : 'str', 'zip' : 'str', 'webaddr' : 'str', 'longitud' : 'str', 'latitude' : 'str'
    }
    for file in sorted_files:
        file_path = f'{characteristics_dir}/{file}'
        df = pd.read_csv(file_path, dtype=dtypes, encoding_errors='replace', low_memory=False)
        df = df.rename(str.lower, axis='columns')
        year_num = re.split(r'_|\.', f'{file}')[1]
        
        if int(year_num) > 1998:
            if int(year_num) > 2008:
                filt_col = ['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip', 'webaddr', 'longitud', 'latitude']
            else:
                filt_col = ['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip', 'webaddr']
        else:
            df_filtered = df.loc[:, ['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip']]
        
        df_filtered['year'] = int(year_num)
        master_df = pd.concat([master_df, df_filtered], ignore_index=True)
    
    return master_df


def clean_enrollment(enroll_dir = 'enrolldata'):
    '''cleans yearly enrollment data and returns complete undergraduate enrollment data

    :enroll_dir:        directory where raw enrollment data is located
    '''
    sorted_files = sorted(os.listdir(enroll_dir)) # unnecessary, but helps with error checking
    
    master_df = pd.DataFrame(columns=['unitid', 'totmen', 'totwomen', # total
                                        'wtmen', 'wtwomen', # white
                                        'bkmen', 'bkwomen', # black
                                        'hspmen', 'hspwomen', # hispanic
                                        'asnmen', 'asnwomen', # asian
                                        'totmen_share', 'year',
                                        'totwt_share', 'totbk_share', 'tothsp_share', 'totasn_share'])
    
    var_rename_dict = {
        'eftotlm' : 'totmen', 'eftotlw' : 'totwomen', 'efwhitm' : 'wtmen', 'efwhitw' : 'wtwomen',
        'efbkaam' : 'bkmen', 'efbkaaw' : 'bkwomen', 'efhispm' : 'hspmen', 'efhispw' : 'hspwomen', 
        'efasiam' : 'asnmen', 'efasiaw' : 'asnwomen', 'eftotlm' : 'totmen', 'eftotlw' : 'totwomen',
        'efrace11' : 'wtmen', 'efrace12' : 'wtwomen', 'efrace03' : 'bkmen', 'efrace04' : 'bkwomen', 
        'efrace09' : 'hspmen', 'efrace10' : 'hspwomen', 'efrace07' : 'asnmen', 'efrace08' : 'asnwomen',
        'efrace15' : 'totmen', 'efrace16' : 'totwomen'
    }

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
            df_filtered = df_filtered.rename(columns=var_rename_dict)
        elif int(year_num) in [2008, 2009]:
            df_filtered = df.loc[:, ['unitid', 'line', 'eftotlm', 'eftotlw',
                                         'efrace11', 'efrace12', # total White men, total White women
                                         'efrace03', 'efrace04', # total Black men, total Black women
                                         'efrace09', 'efrace10', # total Hispanic men, total Hispanic women
                                         'efrace07', 'efrace08']] # total Asian men, total Asian women
            df_filtered = df_filtered.rename(columns=var_rename_dict)
        else:
            df_filtered = df.loc[:, ['unitid', 'line', 'eftotlm', 'eftotlw',
                                         'efwhitm', 'efwhitw', # total White men, total White women
                                         'efbkaam', 'efbkaaw', # total Black men, total Black women
                                         'efhispm', 'efhispw', # total Hispanic men, total Hispanic women
                                         'efasiam', 'efasiaw']] # total Asian men, total Asian women
            df_filtered = df_filtered.rename(columns=var_rename_dict)
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

    characteristics = clean_characteristics()
    merged_df = pd.merge(characteristics, master_df, on=['unitid', 'year'])

    return merged_df


def clean_completion(completion_dir = 'completiondata', level = 'bach'):
    '''cleans yearly completion data and returns complete completions data

    :completion_dir:        directory where raw completion data is located
    :level:                 level of degree, options include ['assc', 'bach', 'mast', 'doct']
    '''
    sorted_files = sorted(os.listdir(completion_dir)) # unnecessary, but helps with error checking
    master_df = pd.DataFrame(columns=['unitid', 'cipcode', 
                                      'totmen', 'totwomen', 'totmen_share',
                                      'deglevel', 'year'])

    for file in sorted_files:
        file_path = f'{completion_dir}/{file}'
        df = pd.read_csv(file_path, dtype={'cipcode' : 'str'}) # read in df
        df = df.rename(str.lower, axis='columns') # some df's have all uppercase, some have all lowercase
        year_num = re.split(r'_|\.', f'{file}')[1]
        
        if 'crace15' in df.columns:
            df_filtered = df.loc[:, ['unitid', 'cipcode', 'awlevel', 'crace15', 'crace16']]
            df_filtered = df_filtered.rename(columns={'crace15' : 'totmen', 'crace16' : 'totwomen'})
        else:
            df_filtered = df.loc[:, ['unitid', 'cipcode', 'awlevel', 'ctotalm', 'ctotalw']]
            df_filtered = df_filtered.rename(columns={'ctotalm' : 'totmen', 'ctotalw' : 'totwomen'})
        
        if level == 'assc':
            level_query = f'awlevel == 3'
        elif level == 'bach':
            level_query = f'awlevel == 5'
        elif level == 'mast':
            level_query = f'awlevel == 7'
        elif level == 'doct':
            if int(year_num) < 2010:
                level_query = f'awlevel == 9'
            else:
                level_query = f'awlevel >= 17 and awlevel <= 19'
        else:
            raise  ValueError("level must be 'assc', 'bach', 'mast' or 'doct'")
        
        completions = df_filtered.query(level_query)
        completions = completions.groupby(['unitid', 'cipcode'])[['totmen', 'totwomen']].sum().reset_index()
        completions = completions.eval('totmen_share = totmen / (totmen + totwomen) * 100') # maleshare within each major
        completions['deglevel'] = level # adds level identifier
        completions['year'] = int(year_num) # adds year identifier
        
        master_df = pd.concat([master_df, completions], ignore_index=True)
        
    return master_df


def clean_graduation(graduation_dir = 'graduationdata'):
    '''cleans yearly graduation data and returns complete graduation data

    :graduation_dir:        directory where raw completion data is located
    '''
    sorted_files = sorted(os.listdir(graduation_dir)) # unnecessary, but helps with error checking
    master_df = pd.DataFrame(columns=['unitid', 'totmen', 'totmen_graduated', 'totwomen','totwomen_graduated', 
                                      'wtmen', 'wtmen_graduated', 'wtwomen', 'wtwomen_graduated', 
                                      'bkmen', 'bkmen_graduated', 'bkwomen', 'bkwomen_graduated', 
                                      'hspmen', 'hspmen_graduated', 'hspwomen', 'hspwomen_graduated', 
                                      'asnmen', 'asnmen_graduated', 'asnwomen', 'asnwomen_graduated', 
                                      'gradrate_totmen', 'gradrate_totwomen',
                                      'gradrate_wtmen', 'gradrate_wtwomen', 'gradrate_bkmen',
                                      'gradrate_bkwomen', 'gradrate_hspmen', 'gradrate_hspwomen',
                                      'gradrate_asnmen', 'gradrate_asnwomen' 'year'])

    var_rename_dict = {
        'grrace15' : 'totmen', 'grrace16' : 'totwomen',
        'grtotlm' : 'totmen', 'grtotlw' : 'totwomen', 'grwhitm' : 'wtmen', 'grwhitw' : 'wtwomen',
        'grbkaam' : 'bkmen', 'grbkaaw' : 'bkwomen', 'grhispm' : 'hspmen', 'grhispw' : 'hspwomen', 
        'grasiam' : 'asnmen', 'grasiaw' : 'asnwomen', 'grtotlm' : 'totmen', 'grtotlw' : 'totwomen',
        'grrace11' : 'wtmen', 'grrace12' : 'wtwomen', 'grrace03' : 'bkmen', 'grrace04' : 'bkwomen', 
        'grrace09' : 'hspmen', 'grrace10' : 'hspwomen', 'grrace07' : 'asnmen', 'grrace08' : 'asnwomen'
    }

    for file in sorted_files:
        file_path = f'{graduation_dir}/{file}'
        df = pd.read_csv(file_path) # read in df
        df = df.rename(str.lower, axis='columns') # some df's have all uppercase, some have all lowercase
        year_num = re.split(r'_|\.', f'{file}')[1]

        if int(year_num) < 2008:
            filt_col = ['unitid', 'grtype', 'chrtstat', 'section', 'cohort', 
                        'grrace15', 'grrace16',
                        'grrace11', 'grrace12',  
                        'grrace03', 'grrace04', 
                        'grrace09', 'grrace10', 
                        'grrace07', 'grrace08']
        else:
            filt_col = ['unitid', 'grtype', 'chrtstat', 'section', 'cohort', 
                        'grtotlm', 'grtotlw',
                        'grwhitm', 'grwhitw', 
                        'grbkaam', 'grbkaaw', 
                        'grhispm', 'grhispw', 
                        'grasiam', 'grasiaw']
        
        df_filtered = df.loc[:, filt_col].rename(columns=var_rename_dict)

        grads_bach = df_filtered.query('(8 <= grtype <= 9) and (12 <= chrtstat <= 13) and section == 2')
        pivoted_grads_bach = grads_bach.pivot(index='unitid', columns='grtype', values=['totmen', 'totwomen', # get cohort and grads
                                                                                        'wtmen', 'wtwomen',
                                                                                        'bkmen', 'bkwomen',
                                                                                        'hspmen', 'hspwomen',
                                                                                        'asnmen', 'asnwomen'])
        for i in ['tot', 'wt', 'bk', 'hsp', 'asn']:
            pivoted_grads_bach[f'gradrate_{i}men'] = (pivoted_grads_bach[f'{i}men'][9] /    # grad rates
                                                     pivoted_grads_bach[f'{i}men'][8] * 100)
            pivoted_grads_bach[f'gradrate_{i}women'] = (pivoted_grads_bach[f'{i}women'][9] / 
                                                     pivoted_grads_bach[f'{i}women'][8] * 100)
        pivoted_grads_bach = pivoted_grads_bach.reset_index()

        rnm_columns = pivoted_grads_bach.columns.droplevel(1).tolist() # renaming columns
        for i in range(len(rnm_columns)):
            if rnm_columns[i] == rnm_columns[i - 1]:
                rnm_columns[i] = f'{rnm_columns[i]}_graduated'
        pivoted_grads_bach.columns = rnm_columns
        
        pivoted_grads_bach['year'] = int(year_num) # get year identifiers

        master_df = pd.concat([master_df, pivoted_grads_bach], ignore_index=True)
    
    return master_df
        



if __name__ == '__main__':
    df = clean_enrollment()
    print(df.head(40))
    
