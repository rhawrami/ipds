
DATASETS = {

    'characteristics' : {
        'description' : '''Institutional characteristics for each school in a given year, including information like
                            a school's name and address; available for years 1984-2023.''',
        'dir' : 'characteristicsdata',
        'file_prefix' : 'characteristics',
        'format_rules' : [
            (lambda y : y <= 1985, 'IC{year}'),
            (lambda y : (1985 < y <= 1989) or (1991 < y <= 1994), 'IC{year}_A'),
            (lambda y : y == 1990,  'IC90HD'), 
            (lambda y : y == 1991,  'IC1991_hdr'),
            (lambda y : 1994 < y < 1997, 'ic{lag0}{lead1}_A'), # check later
            (lambda y : y == 1997, 'ic9798_HDR'), 
            (lambda y : y == 1998, 'IC98hdac'),
            (lambda y : y == 1999, 'IC99_HD'),
            (lambda y : y == 2000 or y == 2001, 'FA{year}HD'),
            (lambda y : y >= 2002, 'HD{year}')
        ]
        
    },

    'admissions' : {
        'description' : '''Admissions data for each school in a given year (measured in the Fall), including information like
                           ACT/SAT scores and acceptance rates by gender; available for years 2001-2023.''',
        'dir' : 'admissionsdata',
        'file_prefix' : 'admissions',
        'format_rules' : [
            (lambda y: 2001 <= y <= 2013, 'IC{year}'),
            (lambda y: 2014 <= y <= 2023, 'ADM{year}'), 
        ]
    },

    'enrollment' : {
        'description' : '''Enrollment data for each school in a given year (measured in the Fall), including information like
                            the male enrollment share and enrollment by gender and race; available at the undergraduate or graduate
                            level; available for years 1984-2023.''',
        'dir' : 'enrollmentdata',
        'file_prefix' : 'enrollment',
        'format_rules' : [
            (lambda y: y <= 1985, 'EF{year}'),
            (lambda y: (1985 < y < 1990) or (1991 < y < 1994), 'EF{year}_A'),
            (lambda y: y == 1990, 'EF90_A'),
            (lambda y: y == 1991, 'ef1991_A'),
            (lambda y: y == 1994,  'EF{year}_ANR'),
            (lambda y: 1994 < y < 2000, 'EF{lag0}_ANR'),
            (lambda y: y >= 2000, 'EF{year}A')
        ]
    },

    'completion' : {
        'description' : '''Completion data for each school in a given year by detailed subject field, including information like
                            the male completion share within a subject (e.g., Economics); available at the Associate, Bachelor's, 
                            Master's or Doctoral level; available for years 1984-2023.''', 
        'dir' : 'completiondata',
        'file_prefix' : 'completion',
        'format_rules' : [
            (lambda y: y < 1990 or (1991 < y < 1995), 'C{year}_CIP'),
            (lambda y: y == 1990, 'C8990CIP'),
            (lambda y: y == 1991, 'c1991_cip'),
            (lambda y: 1995 <= y < 2000, 'C{lag1}{lag0}_A'),
            (lambda y: y >= 2000, 'C{year}_A')
        ]
    },

    'graduation' : {
        'description' : '''Graduation data for each school in a given year, including information 
                            like the graduation rate by gender and race; available at the Associate or
                            Bachelor's level; available for years 2000-2023.''',
        'dir' : 'graduationdata',
        'file_prefix' : 'graduation',
        'format_rules' : [
            (lambda y: y in range(2000,2024), 'GR{year}')
        ]
    },

    'cip' : {
        'description' : '''Provides subject field codes for subjects in a given year; should be used
                           with Completion data; available for years 1984-2023.''',
        'dir' : 'cipdata',
        'file_prefix' : 'cip',
        'format_rules' : [
            (lambda y: (y < 1990) or (1991 < y < 1995), 'C{year}_CIP'),
            (lambda y: y == 1990, 'C8990CIP'),
            (lambda y: y == 1991, 'c1991_cip'),
            (lambda y: 1995 <= y < 2000, 'C{lag1}{lag0}_A'),
            (lambda y: y >= 2000, 'C{year}_A')
        ]
    }

}

VARIABLES = {

    'characteristics' : {
        
    },

    'admissions' : {

    },

    'enrollment' : {

    },

    'completion' : {

    },

    'graduation' : {

    }
    
}