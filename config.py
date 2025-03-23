DEBUG_MODE = True
GEO_SYSTEM = 'openrouteservice'  # yandex, google
COORD_DATA = './data/coordinates.json'

VEHICLES = {
    'car': {
        'open_profile': 'driving-car',
        'extras': None,
    },
    'truck': {
        'open_profile': 'driving-hgv',
        'extras': None,
    },
    '40-foot container': {
        'open_profile': 'driving-hgv',
        'extras': {
            "weight": 30000,  # масса в кг
            "height": 4.0,  # метры
            "width": 2.5,  # метры
            "length": 16.0,  # метры
            "axleload": 11000,  # нагрузка на ось в кг
            "hazmat": False,  # опасный груз
        },
    },
}
