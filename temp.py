import requests
import os
import zipfile 
import re
import pandas as pd
from bs4 import BeautifulSoup

def get_cip_codes(dir = 'cip_codes'):
    
    os.makedirs(dir, exist_ok=True)

    file_template = 'https://nces.ed.gov/ipeds/datacenter/data/{}_Dict.zip'
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
            
        with zipfile.ZipFile(zipped_file, 'r') as zfile:
            file_to_extract = f_name.split('/')[-1].replace('_Dict.zip', '').lower()
            for ext in ['.html', '.xls', '.xlsx']:  # diff file formats, try each one, most of the early years have .html
                try:
                    zfile.extract(file_to_extract + ext, dir)
                    os.rename(f'{dir}/{file_to_extract}{ext}', f'{dir}/cipcodes_{i}' + ext)
                    os.remove(zipped_file)
                    break
                except KeyError:
                    continue


def clean_cip_html(file_path):
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


def clean_cip_codes(cip_codes_dir = 'cip_codes'):
    
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
    