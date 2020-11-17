replaced_frequencies = {
    'CMIP5': {},
    'CMIP6': {
        '1hr': '1-hourly',
        '1hrCM': '1-hourly',
        '1hrPt': '1-hourly',
        '3hr': '3-hourly',
        '3hrPt': '3-hourly',
        '6hr': '6-hourly',
        '6hrPt': '6-hourly',
        'day': 'Daily',
        'dec': 'Decadal',
        'fx': 'Fixed',
        'mon': 'Monthly',
        'monC': 'Climatology Monthly Mean',
        'monPt': 'Monthly',
        'subhrPt': 'Sub-Hourly',
        'yr': 'Yearly',
        'yrPt': 'Yearly'
    }
}

removed_frequencies = [
    '1hr',
    '1hrCM',
    '1hrPt',
    '3hr',
    '3hrPt',
    '6hr',
    '6hrPt',
    'day',
    'dec',
    'fx',
    'mon',
    'monC',
    'monPt',
    'subhrPt',
    'yr',
    'yrPt'
]

replaced_experiments = {
    'CMIP5': {
        'esmFdbk2': '1pctCO2-rad',
        'abrupt4xCO2': 'abrupt-4xCO2',
        'amip4xCO2': 'amip-4xCO2',
        'amipFuture': 'amip-future4K',
        'amip4K': 'amip-p4K',
        'aqua4xCO2': 'aqua-4xCO2',
        'aquaControl': 'aqua-control',
        'aqua4K': 'aqua-p4K',
        'esmHistorical': 'esm-hist',
        'esmControl': 'esm-piControl',
        'historicalGHG': 'hist-GHG',
        'historicalNat': 'hist-nat',
        'historicalExt': 'historical-ext',
        'rcp26': 'rcp26-cmip5',
        'rcp45': 'rcp45-cmip5',
        'rcp60': 'rcp60-cmip5',
        'rcp85': 'rcp85-cmip5'
    },
    'CMIP6': {}
}

removed_experiments = [
    'esmFdbk2',
    'abrupt4xCO2',
    'amip4xCO2',
    'amipFuture',
    'amip4K',
    'aqua4xCO2',
    'aquaControl',
    'aqua4K',
    'esmHistorical',
    'esmControl',
    'historicalGHG',
    'historicalNat',
    'historicalExt',
    'rcp26',
    'rcp45',
    'rcp60',
    'rcp85',
    'Other'
]
