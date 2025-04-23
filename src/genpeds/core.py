from getipeds import scrape_ipeds_data, DATASETS
from cleanipeds import CLEANERS
import shutil
from abc import ABC, abstractmethod

class IPDS(ABC):
    subject = None
    
    def __init__(self, year_range=None):
        self.year_range = year_range
    
    def scrape(self, view_progress=False):
        '''downloads NCES IPEDS data, to disk, on specified years for a defined subject.
        
        :view_progress: boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.
        '''
        scrape_ipeds_data(subject=self.subject, year_range=self.year_range, see_progress=view_progress)

    @abstractmethod
    def clean(self):
        '''clean the data'''
        pass

    @abstractmethod
    def run(self):
        '''scrape and clean'''
        pass


class Admissions(IPDS):
    '''IPEDS Admissions'''
    subject = 'admissions'

    def __init__(self, year_range=(2001,2003)):
        '''IPEDS Admissions data object.
        
        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 2001-2023.'''
        super().__init__(year_range)

    def clean(self, admit_dir='admissionsdata', rm_disk=False):
        '''cleans downloaded Admissions data, returns Pandas Dataframe.
        
        :admit_dir: directory where raw admissions data is located; defaults to default download dir name.
        :rm_disk: removes downloaded Admissions data from disk.
        '''
        df = CLEANERS[self.subject](admit_dir)
        if rm_disk:
            shutil.rmtree(admit_dir)
        return df
    
    def run(self, view_progress=False, merge_with_char=False, rm_disk=False):
        '''scrapes and cleans Admissions data; returns Pandas Dataframe.
        
        ## parameters

        - :view_progress: 
        boolean that, when true, prints admissions statement for extraction of each year. If false, no messages printed.

        - :merge_with_char:
        boolean that, when true, scrapes institutional Enrollment data and merges with Admissions data. Admissions data will automatically be removed from disk when the Dataframe is instantiated. (To keep the Characteristics data, create a Characteristics object.)
        
        - :rm_disk: 
        removes downloaded Admissions data from disk.

        --------------
        ## variables returned
        
        :id: six-digit (but not always six-digit) integer institutional identifier. While ID's can vary for an institution over time (due to a school splitting into two or merging), filtering by ID is generally more reliable than instution name. Available for all years.
        :year: survey year integer.

        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk)
        if merge_with_char:
            char_df = Characteristics(year_range=self.year_range).run(view_progress=view_progress, rm_disk=True)
            df = df.merge(char_df, on=['id', 'year'])
        return df
    
    

class Characteristics(IPDS):
    '''IPEDS Characteristics'''
    subject = 'characteristics'

    def __init__(self, year_range=(1984,2023)):
        '''IPEDS Characteristics data object.
        
        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 1984-2023.
        '''
        super().__init__(year_range)

    def clean(self, char_dir='characteristicsdata', rm_disk=False):
        '''cleans downloaded Characteristics data, returns Pandas Dataframe.
        
        :char_dir: directory where raw enrollment data is located; defaults to default download dir name.
        :rm_disk: removes downloaded Characteristics data from disk.
        '''
        df = CLEANERS[self.subject](char_dir)
        if rm_disk:
            shutil.rmtree(char_dir)
        return df
    
    def run(self, view_progress=False, rm_disk=False):
        '''scrapes and cleans IPEDS Characteristics data; returns Pandas Dataframe.
        
        ## parameters

        - :view_progress: 
        boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.
        
        - :clean_disk: 
        removes downloaded Characteristics data from disk.

        --------------
        ## variables returned
        
        :id: six-digit (but not always six-digit) integer institutional identifier . While ID's can vary for an institution over time (due to a school splitting into two or merging), filtering by ID is generally more reliable than instution name. Available for all years.
        :name: institution name string, uppercase by default. Note that attempting to filter by name may not capture an institution over time properly, as institution names can vary over time. Available for all years.
        :address: institution address location string. Available for all years. 
        :city: institution city location string. Available for all years.
        :state: institution state (abbreviation) string. Available for all years.
        :zip: institution zipcode string. Available for all years.
        :webaddresse: institution web address string. Only available for years 1999+.
        :longitude: institution longitude string. Only available for years 2009+.
        :latitude: institution laitude string. Only available for years 2009+.
        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk)
        return df


class Enrollment(IPDS):
    '''IPEDS Enrollment'''
    subject = 'enrollment'

    def __init__(self, year_range=(1984,2023)):
        '''IPEDS Enrollment data object.
        
        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 1984-2023.
        '''
        super().__init__(year_range)

    def clean(self, student_level='undergrad', enroll_dir='enrollmentdata', rm_disk=False):
        '''cleans downloaded undergraduate Fall Enrollment data, returns Pandas Dataframe.
        
        :student_level: level of student enrolled; options include ['undergrad', 'grad'].
        :enroll_dir: directory where raw enrollment data is located; defaults to default download dir name.
        :rm_disk: removes downloaded Enrollment data from disk.
        '''
        df = CLEANERS[self.subject](enroll_dir, student_level)
        if rm_disk:
            shutil.rmtree(enroll_dir)
        return df
    
    def run(self, student_level='undergrad', view_progress=False, merge_with_char=False, rm_disk=False):
        '''scrapes and cleans IPEDS Fall Enrollment data; returns Pandas Dataframe.
        
        ## parameters

        - :student_level: 
        level of student enrolled; options include ['undergrad', 'grad'].

        - :view_progress: 
        boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.

        - :merge_with_char:
        boolean that, when true, scrapes institutional Characteristics data and merges with Enrollment data. Characteristics data will automatically be removed from disk when the Dataframe is instantiated. (To keep the Characteristics data, create a Characteristics object.)
        
        - :rm_disk: 
        removes downloaded Enrollment data from disk.

        --------------
        ## variables returned
        
        :id: six-digit (but not always six-digit) integer institutional identifier. While ID's can vary for an institution over time (due to a school splitting into two or merging), filtering by ID is generally more reliable than instution name. Available for all years.
        :studentlevel: level of student; options include 'undergrad' (full and part-time), and 'grad (full and part-time, also including first-professional).
        :totmen: total (full-time and part-time) undergraduate male enrollment. Available for all years.
        :totwomen: `totmen`, but for women.
        :wtmen: total (full-time and part-time) undergraduate non-Hispanic White male enrollment. Unavailable for years 1985, 1987, and 1989.
        :wtwomen: `wtmen`, but for women.
        :bkmen: total (full-time and part-time) undergraduate non-Hispanic Black male enrollment. Unavailable for years 1985, 1987, and 1989.
        :bkwomen: `bkmen`, but for women.
        :asnmen: total (full-time and part-time) undergraduate non-Hispanic Asian male enrollment. Unavailable for years 1985, 1987, and 1989.
        :asnwomen: `asnmen`, but for women.
        :hspmen: total (full-time and part-time) undergraduate Hispanic male enrollment. Unavailable for years 1985, 1987, and 1989.
        :hspwomen: `hspnmen`, but for women.
        :totwt_share: total (full-time and part-time) White share of undergraduate enrollment. Unavailable for years 1985, 1987, and 1989.
        :totbk_share: `totwt_share`, but for Black men and women.
        :totasn_share: `totwt_share`, but for Asian men and women.
        :tothsp_share: `totwt_share`, but for Hispanic men and women.
        :year: survey year integer.
        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk, student_level=student_level)
        if merge_with_char:
            char_df = Characteristics(year_range=self.year_range).run(view_progress=view_progress, rm_disk=True)
            df = df.merge(char_df, on=['id', 'year'])
        return df


class CipCodes(IPDS):
    '''CIP Codes'''
    subject = 'cip'

    def __init__(self, year_range=(1984,2023)):
        '''IPEDS CIP Codes data object.

        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 1984-2023.

        CIP, or Classification of Instructional Programs, are key-value pairs for subject study fields. CIP's vary by year, and are relevant to identify subject field in completion data. Available for years 1984-2023. CIP data should be used in conjunction with Completion data.
        '''
        super().__init__(year_range)

    def clean(self, cip_dir='cipdata', rm_disk=False):
        '''cleans downloaded CIP data, returns Pandas Dataframe.
        
        :complete_dir: directory where raw CIP data is located; defaults to default download dir name.
        :rm_disk: removes downloaded CIP data from disk.
        '''
        df = CLEANERS[self.subject](cip_dir)
        if rm_disk:
            shutil.rmtree(cip_dir)
        return df
    
    def run(self, view_progress=False, rm_disk=False):
        '''scrapes and cleans IPEDS CIP data; returns Pandas DataFrame.
        
        ## parameters

        - :view_progress: 
        boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.
        
        - :rm_disk: 
        removes downloaded Enrollment data (and Characteristics data if present) from disk.
        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk)
        return df


class Completion(IPDS):
    '''IPEDS Completion'''
    subject = 'completion'

    def __init__(self, year_range=(1984,2023)):
        '''IPEDS Completion data object.
        
        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 1984-2023.
        '''
        super().__init__(year_range)

    def clean(self, complete_dir='completiondata', degree_level='bach', rm_disk=False):
        '''cleans downloaded Completion data, returns Pandas Dataframe.
        
        :complete_dir: directory where raw completion data is located; defaults to default download dir name.
        :degree_level: level of degree, options include ['assc', 'bach', 'mast', 'doct']
        :rm_disk: removes downloaded Completion data from disk.
        '''
        df = CLEANERS[self.subject](complete_dir, degree_level)
        if rm_disk:
            shutil.rmtree(complete_dir)
        return df
    
    def run(self, degree_level='bach', view_progress=False, merge_with_char=False, get_cip_codes=True, rm_disk=False):
        '''scrapes and cleans IPEDS Completion data; returns Pandas Dataframe.
        
        ## parameters

        - :degree_level:
        level of degree, options include ['assc', 'bach', 'mast', 'doct']

        - :view_progress: 
        boolean that, when true, prints completion statement for extraction of each year. If false, no messages printed.

        - :merge_with_char:
        boolean that, when true, scrapes institutional Characteristics data and merges with Completion data.

         - :get_cip_codes: 
        boolean that, when true, scrapes CIP (field of study) codes and merges with Completion data.
        
        - :rm_disk: 
        removes downloaded Enrollment data (and Characteristics data if present) from disk.

        --------------
        ## variables returned
        
        :id: six-digit (but not always six-digit) integer institutional identifier. While ID's can vary for an institution over time (due to a school splitting into two or merging), filtering by ID is generally more reliable than instution name. Available for all years.
        :cipcode: CIP (Classification of Instructional Programs) code. Note that CIP codes can vary by year.
        :totmen: total male degree earners.
        :totwomen: total female degree earners.
        :totmen_share: male share of total degree earners (within a certain CIP code).
        :deglevel: degree level (options include ['assc', 'bach', 'mast', 'doct'])
        :year: survey year integer.

        if merged with CIP data...
        
        :valuelabel: label for CIP code (e.g., 'Civil Engineering, General' for CIP code 14.0801)
        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk, degree_level=degree_level)
        if merge_with_char:
            char_df = Characteristics(year_range=self.year_range).run(view_progress=view_progress, rm_disk=True)
            df = df.merge(char_df, on=['id', 'year'])
        if get_cip_codes:
            cip_df = CipCodes(year_range=self.year_range).run(view_progress=view_progress, rm_disk=True)
            df = df.merge(cip_df, on=['cipcode', 'year'])
        return df


class Graduation(IPDS):
    '''IPEDS Graduation'''
    subject = 'graduation'

    def __init__(self, year_range=(1984,2023)):
        '''IPEDS Graduation data object.
        
        :year_range: tuple of inclusive year integers (indicates a range), iterable of year integers (indicates group of individual years), or single year to pull data from. Data available for years 2000-2023.
        '''
        super().__init__(year_range)

    def clean(self, grad_dir='graduationdata', degree_level='bach', rm_disk=False):
        '''cleans downloaded undergraduate Graduation data, returns Pandas Dataframe.
        
        :grad_dir: directory where raw graduation data is located; defaults to default download dir name.
        :degree_level: level of degree; options include ['assc', 'bach'].
        :rm_disk: removes downloaded Graduation data from disk.
        '''
        df = CLEANERS[self.subject](grad_dir, degree_level)
        if rm_disk:
            shutil.rmtree(grad_dir)
        return df
    
    def run(self, degree_level='bach', view_progress=False, merge_with_char=False, rm_disk=False):
        '''scrapes and cleans IPEDS Graduation data; returns Pandas Dataframe.
        
        ## parameters

        - :degree_level:
        level of degree; options include ['assc', 'bach'].

        - :view_progress: 
        boolean that, when true, prints graduation statement for extraction of each year. If false, no messages printed.

        - :merge_with_char:
        boolean that, when true, scrapes institutional Characteristics data and merges with Graduation data. Characteristics data will automatically be removed from disk when the Dataframe is instantiated. (To keep the Characteristics data, create a Characteristics object.)
        
        - :rm_disk: 
        removes downloaded Graduation data from disk.

        --------------
        ## variables returned
        
        :id: six-digit (but not always six-digit) integer institutional identifier. While ID's can vary for an institution over time (due to a school splitting into two or merging), filtering by ID is generally more reliable than instution name. Available for all years.
        :totmen: total adjusted cohort of men (*totwomen* is the same for women).
        :totmen_graduated: total number of men who graduated within 150% of normal time; this time is 6 years for four-year programs, and 3 years for two-year programs (*totwomen_graduated* is the same for women).
        :deglevel: identifier for level of graduates; =='assc' for those in two-year programs; == 'bach' for those in four-year programs.
        :year: survey year integer.

        The prefixes, ['wt', 'bk', 'asn', 'hsp'] correspond to measures for the White, Black, Asian and Hispanic population respectively.
        '''
        self.scrape(view_progress=view_progress)
        df = self.clean(rm_disk=rm_disk, degree_level=degree_level)
        if merge_with_char:
            char_df = Characteristics(year_range=self.year_range).run(view_progress=view_progress, rm_disk=True)
            df = df.merge(char_df, on=['id', 'year'])
        return df
    
        
if __name__ == '__main__':
    chars = Enrollment(year_range=(2000,2005))
    df = chars.run(True, True, False)
    print(df.columns)
    print(df.head(20))
    print(df.head(-20))
    print(df['year'].value_counts().sort_index())

    # #grad = Graduation(2000)
    # df2 = grad.run('bach', merge_with_char=True)
    # print(df2.columns)
    # print(df2.head(20))
    # print(df2.head(-20))
    # print(df2['year'].value_counts().sort_index())

    # enroll = Enrollment(2000)
    # df3 = enroll.run('undergrad', merge_with_char=True)
    # print(df3.columns)
    # print(df3.head(20))
    # print(df3.head(-20))
    # print(df3['year'].value_counts().sort_index())

    # admit = Admissions(2002)
    # df3 = admit.run(merge_with_char=True)
    # print(df3.columns)
    # print(df3.head(20))
    # print(df3.head(-20))
    # print(df3['year'].value_counts().sort_index())
    # print(df3.loc[:, ['accept_rate_men', 'accept_rate_women']].describe())