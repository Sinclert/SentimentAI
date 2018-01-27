

CLEANING_FILTERS = [
    {
        'pattern': 'http\S+',
        'replace': ''
    },
    {
        'pattern': '#',
        'replace': ''
    },
    {
        'pattern': '&\w+;',
        'replace': ''
    },
    {
        'pattern':
            '[\U00002600-\U000027B0'
            '\U0001F300-\U0001F64F'
            '\U0001F680-\U0001F6FF'
            '\U0001F910-\U0001F919]+',
        'replace': ''
    },
    {
        'pattern': '\s+',
        'replace': ' '
    },
]
