from genpeds import scrape_ipeds_data
import os
import shutil
import pytest

@pytest.mark.parametrize('subject, year_range_char', [
    ('characteristics', (1990,2003)),
    ('characteristics', [2002,2004,2006,2008]),
    ('characteristics', 2023)
])
def test_subject_downloads(subject, year_range_char):
    '''test IPEDS variable-subject data scraping'''
    download_dir = f'{subject}data'
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)

    scrape_ipeds_data(subject=subject, year_range=year_range_char)
    
    assert os.path.exists(download_dir), f'{subject.title()} directory not found.'

    # tuple range
    if isinstance(year_range_char, tuple):
        start,end = year_range_char
        for yr in range(start, end + 1):
            f_name = f'{subject}_{yr}.csv'
            assert f_name in os.listdir(download_dir), f'File {f_name} not found.'
    # list range
    elif isinstance(year_range_char, list):
        for yr in year_range_char:
             f_name = f'{subject}_{yr}.csv'
             assert f_name in os.listdir(download_dir), f'File {f_name} not found.'
    # single year
    else:
        f_name = f'{subject}_{year_range_char}.csv'
        assert f_name in os.listdir(download_dir), f'File {f_name} not found.'
    shutil.rmtree(download_dir)
