choices_per_stage = {
    'DialogueStates:PROCESSOR_BRAND': ['Apple', 'HP', 'MSI', 'Acer', 'Lenovo', 'ASUS', 'Other'],
    'DialogueStates:PROCESSOR_SERIES_Apple': ['M1', 'M2'],
    'DialogueStates:PROCESSOR_SERIES_Other': [
        'intel core i3',
        'intel core i5',
        'intel core i7',
        'intel pentium',
        'intel celeron',
        'intel core',
        'zhaoxin',
        'qualcomm',
        'AMD ryzen',
        'other',
    ],
    'DialogueStates:VIDEOCARD_TYPE': [
        'интегрированная',
        'geforce rtx',
        'geforce mx',
        'geforce gtx',
        'radeon',
        'other',
    ],
    'DialogueStates:HDMI_PORT': ['Да, как без него вообще жить можно!', 'Не, без него обойдусь...'],
    'DialogueStates:MATERIAL': ['металл', 'пластик'],
}

all_processors_regexp = '|'.join(
    choices_per_stage['DialogueStates:PROCESSOR_SERIES_Apple'] +
    choices_per_stage['DialogueStates:PROCESSOR_SERIES_Other']
)

hdmi_port_answers = {
    'Да, как без него вообще жить можно!': 1,
    'Не, без него обойдусь...': 0,
}
