import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import warnings
import numpy as np

final_names = {
    'unitid' : 'id', 'instnm' : 'name', 
    'addr' : 'address', 'stabbr' : 'state', 'webaddr' : 'webaddress', 'longitud' : 'longitude',
    'codevalue' : 'cipcode'
}

def clean_characteristics(characteristics_dir = 'characteristicsdata'):
    '''cleans institution characteristics data and returns complete characteristics data

    :characteristics_dir:        directory where raw enrollment data is located
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
    sorted_files = sorted(os.listdir(characteristics_dir))

    master_df = pd.DataFrame(columns=['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip', 'webaddr', 'longitud', 'latitude'])

    dtypes = {
        'unitid' : int, 'instnm' : str, 'addr' : str, 'city' : str, 
        'stabbr' : str, 'zip' : str, 'webaddr' : str, 'longitud' : str, 'latitude' : str
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
            filt_col = ['unitid', 'instnm', 'addr', 'city', 'stabbr', 'zip']
        df_filtered = df.loc[:, filt_col]
        
        df_filtered['year'] = int(year_num)
        master_df = pd.concat([master_df, df_filtered], ignore_index=True)
    
    master_df = master_df.rename(columns=final_names)
    return master_df

def clean_admissions(admissions_dir = 'admissionsdata'):
    '''cleans yearly admissions data and returns complete admissions data
    
    :admissions_dir:        directory where raw admissions data is located
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
    sorted_files = sorted(os.listdir(admissions_dir)) # unnecessary, but helps with error checking

    admissions_base_cols = {'unitid' : 'id', 
                'applcnm' : 'men_applied', 'applcnw' : 'women_applied', 
                'admssnm' : 'men_admitted', 'admssnw' : 'women_admitted',
                'satpct' : 'share_submit_sat', 'actpct' : 'share_submit_act',                                      
                'satvr25' : 'sat_rw_25', 'satvr75' : 'sat_rw_50', 
                'satmt25' : 'sat_math_25', 'satmt75' : 'sat_math_75', 
                'actcm25' : 'act_comp_25', 'actcm75' : 'act_comp_75',
                'acten25' : 'act_eng_25', 'acten75' : 'act_eng_75', 
                'actmt25' : 'act_math_25', 'actmt75' : 'act_math_75'}
    admissions_early_cols = {**admissions_base_cols, 'enrlftm' : 'men_ft_enrolled', 'enrlftw' : 'women_ft_enrolled',
                             'enrlptm' : 'men_pt_enrolled', 'enrlptw' : 'women_pt_enrolled'}
    admissions_mid_cols = {**admissions_base_cols,'enrlm' : 'men_enrolled', 'enrlw' : 'women_enrolled'}
    admissions_last_cols = {**admissions_mid_cols, 
                             'applcn' : 'tot_applied', 'admssn' : 'tot_admitted', 'enrlt' : 'tot_enrolled',
                             'acten50' : 'act_eng_50', 'actmt50' : 'act_math_50', 'actcm50' : 'act_comp_50',
                             'satvr50' : 'sat_eng_50', 'satmt50' : 'sat_math_50'}

    master_df = pd.DataFrame()
    
    for file in sorted_files:
        file_path = f'{admissions_dir}/{file}'
        df = pd.read_csv(file_path, low_memory=False) # read in df
        df = df.rename(str.lower, axis='columns') # some df's have all uppercase, some have all lowercase
        df.columns = df.columns.str.strip() # some column names have right spaces
        year_num = re.split(r'_|\.', f'{file}')[1]
        
        if int(year_num) == 2001:
            cols_dict = admissions_early_cols
        elif int(year_num) in [2022,2023]:
            cols_dict = admissions_last_cols
        else:
            cols_dict = admissions_mid_cols
        cols_to_filter = cols_dict.keys()
        df_filtered = df.loc[:, cols_to_filter] # filter cols
        df_filtered = df_filtered.rename(columns=cols_dict) # rename cols

        df_filtered = df_filtered.replace('.', np.nan) # replace missing data with NaN
        for col in df_filtered.columns:
            if col == 'id':
                df_filtered[col] = df_filtered[col].astype(int) # id integer
            else:
                df_filtered[col] = df_filtered[col].astype(float) # all other vars are float

        if int(year_num) == 2001:
            df_filtered['men_enrolled'] = df_filtered['men_ft_enrolled'] + df_filtered['men_pt_enrolled']
            df_filtered['women_enrolled'] = df_filtered['women_ft_enrolled'] + df_filtered['women_pt_enrolled']
        if 'tot_applied' not in df_filtered.columns:
            df_filtered['tot_applied'] = df_filtered['men_applied'] + df_filtered['women_applied']
            df_filtered['tot_admitted'] = df_filtered['men_admitted'] + df_filtered['women_admitted']
            df_filtered['tot_enrolled'] = df_filtered['men_enrolled'] + df_filtered['women_enrolled']

        for i in ['men', 'women']:
            df_filtered[f'accept_rate_{i}'] = np.where(
            df_filtered[f'{i}_applied'] == 0,
            np.nan,
            (df_filtered[f'{i}_admitted'] / df_filtered[f'{i}_applied'] * 100)
            )
    
            df_filtered[f'yield_rate_{i}'] = np.where(
            df_filtered[f'{i}_admitted'] == 0,
            np.nan,
            (df_filtered[f'{i}_enrolled'] / df_filtered[f'{i}_admitted'] * 100)
            )
        
        df_filtered['year'] = int(year_num) # year identifier
        df_filtered['men_applied_share'] = df_filtered['men_applied'] / df_filtered['tot_applied'] * 100
        df_filtered['men_admitted_share'] = df_filtered['men_admitted'] / df_filtered['tot_admitted'] * 100

        master_df = pd.concat([master_df, df_filtered], ignore_index=True)
    
    admissions_df = master_df.drop(columns=['women_applied', 'women_admitted', 'women_enrolled',
                                            'men_ft_enrolled', 'men_pt_enrolled', 'women_ft_enrolled', 'women_pt_enrolled'])

    return admissions_df


def clean_enrollment(enrollment_dir = 'enrollmentdata', student_level = 'undergrad'):
    '''cleans yearly enrollment data and returns complete student enrollment data

    :enrollment_dir:        directory where raw enrollment data is located
    :student_level:        level of enrollment; options include ['undergrad', 'grad']
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
    sorted_files = sorted(os.listdir(enrollment_dir)) # unnecessary, but helps with error checking

    grad_rules = [
        (lambda y: y in [1984,1985], 'line in [11,25,10,24]'),
        (lambda y: (y == 1986) or (y in range(1990,1999)), 'line in [14,28,9,10,23,24]'),
        (lambda y: y in [1987,1988,1989], 'line in [14,28]'),
        (lambda y: y == 1999, 'line in [32,52,16]'),
        (lambda y: (y in range(2000,2002)) or (y in range(2004,2009)), 'line in [11,25,9,23]'),
        (lambda y:  y in range(2002,2004), 'line in [12,26]'),
        (lambda y: y in range(2009,2024), 'line in [11,25]')
    ]
    
    master_df = pd.DataFrame(columns=['unitid', 'totmen', 'totwomen', # total
                                        'wtmen', 'wtwomen', # white
                                        'bkmen', 'bkwomen', # black
                                        'hspmen', 'hspwomen', # hispanic
                                        'asnmen', 'asnwomen', # asian
                                        'totmen_share', 'year', 'studentlevel',
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
        file_path = f'{enrollment_dir}/{file}'
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
        
        if student_level == 'undergrad':
            if int(year_num) < 1986:
                student_query = 'line == 1 or line == 15' # captures total full-time and total part-time undergrads, respectively
            else:
                student_query = 'line == 8 or line == 22' 
        elif student_level == 'grad':
            for cond,frmt in grad_rules:
                if cond(int(year_num)):
                    student_query = frmt # captures full-time and part-time graduate and first-professional students
                    break
            else:
                raise ValueError(f'No formatted rule for year {year_num}')
        else:
            ValueError("student_level must be 'undergrad' or 'grad' ")

        students = df_filtered.query(student_query) # filter data to total studentuates
        
        if 'wtmen' not in students.columns:
            cols_to_sum = ['totmen', 'totwomen']
        else:
            cols_to_sum = ['totmen', 'totwomen', 'wtmen', 'wtwomen','bkmen', 'bkwomen','hspmen', 'hspwomen','asnmen', 'asnwomen']
        
        students_by_inst = students.groupby('unitid')[cols_to_sum].sum() # sum full-time and part-time students by school
        students_by_inst = students_by_inst.eval('totmen_share = totmen / (totmen + totwomen) * 100').reset_index() # male student share
        students_by_inst['year'] = int(year_num) # get year marker for each set
        students_by_inst['studentlevel'] = student_level # get student level identifier

        if 'wtmen' in students_by_inst.columns:
            for attr in ['wt', 'bk', 'hsp', 'asn']:
                eval_str = f'tot{attr}_share = ({attr}men + {attr}women) / (totmen + totwomen) * 100' # race share breakdowns
                students_by_inst = students_by_inst.eval(eval_str)

        master_df = pd.concat([master_df, students_by_inst], ignore_index=True)

    master_df = master_df.rename(columns=final_names)
    return master_df


def clean_completion(completion_dir = 'completiondata', level = 'bach'):
    '''cleans yearly completion data and returns complete completions data

    :completion_dir:        directory where raw completion data is located
    :level:                 level of degree, options include ['assc', 'bach', 'mast', 'doct']
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
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
        
    master_df = master_df.rename(columns=final_names)
    return master_df


def clean_cip_html(file_path):
    '''returns dict of CIP subject code:label pairs for a given year's CIP dictionary html.
    
    :file_path: string path to CIP data dictionary html
    '''
    with open(file_path) as filehandle:
        soup = BeautifulSoup(filehandle, 'html.parser')
        rows = soup.find_all('tr', attrs={'bgcolor': ['White', 'Silver']})
        dat_rows = rows[1:]
        label_dict = {}
        for row in dat_rows:
            cells = row.find_all('td')
            if len(cells) > 1:
                label = cells[0].text.strip()
                val = cells[1].text.strip()
                if label == 'Totals':
                    break # end of relevant table
                else:
                    label_dict[val] = label
        return label_dict


def clean_cip_data(cip_codes_dir = 'cipdata'):
    '''cleans yearly CIP data and returns full dataframe

    :cip_codes_dir: directory where raw CIP data is located
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    sorted_files = sorted(os.listdir(cip_codes_dir))
    master_df = pd.DataFrame(columns=['codevalue', 'valuelabel', 'year'])

    for file in sorted_files:
        file_path = f'{cip_codes_dir}/{file}'
        year_num = re.split(r'_|\.', f'{file}')[1]
        ext = re.split(r'_|\.', f'{file}')[2]
        if ext == 'html':
            html_dict = clean_cip_html(file_path=file_path)
            df = pd.DataFrame({'valuelabel' : html_dict.values(),
                               'codevalue' : html_dict.keys()})
            df['year'] = int(year_num)
        else:
            df = pd.read_excel(file_path, sheet_name='Frequencies', dtype={'codevalue' : 'str'})
            df = df.query('varname == "CIPCODE" or varname == "Cipcode"').loc[:, ['codevalue', 'valuelabel']]
            df['year'] = int(year_num)
        
        master_df = pd.concat([master_df, df], ignore_index=True)
        master_df['valuelabel'] = master_df['valuelabel'].str.replace(r'^(\d+)\s-\s', '', regex=True)
    
    master_df = master_df.rename(columns=final_names)
    return master_df


def clean_graduation(graduation_dir = 'graduationdata', deg_level='bach'):
    '''cleans yearly graduation data and returns complete graduation data

    :graduation_dir:        directory where raw completion data is located
    :deg_level:        degree level; options include ['assc', 'bach']
    '''
    warnings.filterwarnings('ignore', category=FutureWarning)
    sorted_files = sorted(os.listdir(graduation_dir)) # unnecessary, but helps with error checking
    master_df = pd.DataFrame(columns=['unitid', 'totmen', 'totmen_graduated', 'totwomen','totwomen_graduated', 
                                      'wtmen', 'wtmen_graduated', 'wtwomen', 'wtwomen_graduated', 
                                      'bkmen', 'bkmen_graduated', 'bkwomen', 'bkwomen_graduated', 
                                      'hspmen', 'hspmen_graduated', 'hspwomen', 'hspwomen_graduated', 
                                      'asnmen', 'asnmen_graduated', 'asnwomen', 'asnwomen_graduated', 
                                      'gradrate_totmen', 'gradrate_totwomen',
                                      'gradrate_wtmen', 'gradrate_wtwomen', 'gradrate_bkmen',
                                      'gradrate_bkwomen', 'gradrate_hspmen', 'gradrate_hspwomen',
                                      'gradrate_asnmen', 'gradrate_asnwomen', 'year', 'deglevel'])

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
        if deg_level == 'bach':
            deg_query = '(8 <= grtype <= 9) and (12 <= chrtstat <= 13) and section == 2'
            denom = 8
            num = 9
        elif deg_level == 'assc':
            deg_query = '(29 <= grtype <= 30) and (12 <= chrtstat <= 13) and section == 4'
            denom = 29
            num = 30
        else:
            raise  ValueError("deg_level must be 'assc', 'bach', 'mast' or 'doct'")

        grads = df_filtered.query(deg_query)
        pivoted_grads = grads.pivot(index='unitid', columns='grtype', values=['totmen', 'totwomen', # get cohort and grads
                                                                                        'wtmen', 'wtwomen',
                                                                                        'bkmen', 'bkwomen',
                                                                                        'hspmen', 'hspwomen',
                                                                                        'asnmen', 'asnwomen'])
        for i in ['tot', 'wt', 'bk', 'hsp', 'asn']:
            pivoted_grads[f'gradrate_{i}men'] = (pivoted_grads[f'{i}men'][num] /    # grad rates
                                                     pivoted_grads[f'{i}men'][denom] * 100)
            pivoted_grads[f'gradrate_{i}women'] = (pivoted_grads[f'{i}women'][num] / 
                                                     pivoted_grads[f'{i}women'][denom] * 100)
        pivoted_grads = pivoted_grads.reset_index()

        rnm_columns = pivoted_grads.columns.droplevel(1).tolist() # renaming columns
        for i in range(len(rnm_columns)):
            if rnm_columns[i] == rnm_columns[i - 1]:
                rnm_columns[i] = f'{rnm_columns[i]}_graduated'
        pivoted_grads.columns = rnm_columns
        
        pivoted_grads['year'] = int(year_num) # get year identifiers
        pivoted_grads['deglevel'] = deg_level

        master_df = pd.concat([master_df, pivoted_grads], ignore_index=True)
    
    master_df = master_df.rename(columns=final_names)
    return master_df
        
CLEANERS = {
    'characteristics' : clean_characteristics,
    'admissions' : clean_admissions,
    'enrollment' : clean_enrollment,
    'completion' : clean_completion,
    'cip' : clean_cip_data,
    'graduation' : clean_graduation
}


if __name__ == '__main__':
    df = clean_admissions()
    print(df.loc[:, ['yield_rate_men', 'yield_rate_women']].describe())
    print(df.loc[:, ['accept_rate_men', 'accept_rate_women']].describe())
    #print(df.loc[df['accept_rate_men']==np.max(df['accept_rate_men'])])
    #print(df.loc[(df['id'] == 110404)])
    print(f'\n{df.groupby('year')['yield_rate_men'].describe()}')
    print(df.columns)