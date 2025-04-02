DEBUG_MODE = True
GEO_SYSTEM = 'ors_vps'  # yandex, google, openrouteservice - cloud ORS, ors_vps - docker ORS
COORD_DATA = './data/coordinates.json'
OUTPUT_FILE = "output.csv"
MAX_DELAY = 120  # in sec.
NOMINATIM_LOCALPORT = 7070
ORS_LOCALPORT = 8080

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
