LEVELS = [
    1000,
    10000,
    20000,
    #30000,
    #40000,
    50000,
    #60000,
    #70000,
    #80000,
    #90000,
    100000,
]

VARS = {
    'tas': ('undefined', [0]),
    #'ta': ('plev', LEVELS),
    #'pr': ('undefined', [0]),
}

MODELS = [
    'bcc-csm1-1',
    'BNU-ESM',
    'CanESM2',
    'CCSM4',
    'CNRM-CM5',
    'CSIRO-Mk3-6-0',
    'GISS-E2-H',
    'IPSL-CM5A-LR',
    'MIROC-ESM',
    'MRI-CGCM3',
    'NorESM1-M',
]

YEARS = range(1850, 2100)

NAME = "%(var)s_%(level)s_%(model)s_%(year)s.txt"
PREFIX = "%(var)s_%(level)s_%(model)s"


def generate_datasets():
    for var in VARS:
        levname, levels = VARS[var]
        for level in levels:
            for model in MODELS:
                yield var, levname, level, model

