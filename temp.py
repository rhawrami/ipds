import os
import re
import pandas as pd
from bs4 import BeautifulSoup


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
            df = df.query('varname == "CIPCODE"').loc[:, ['codevalue', 'valuelabel']]
            df['year'] = int(year_num)
        
        master_df = pd.concat([master_df, df], ignore_index=True)
        master_df['valuelabel'] = master_df['valuelabel'].str.replace(r'^(\d+)\s-\s', '', regex=True)
    
    return master_df





if __name__ == '__main__':
    #get_cip_codes()
    df = clean_cip_codes()
    print(df.head(20))
    