import sys

from loguru import logger
logger.remove()
logger.add(sys.stdout, level="DEBUG", format="{time} {level} {message}", colorize=True)
logger.add("./data/errors.log", level="ERROR", rotation="10 MB", retention="7 days", compression="zip")

DEBUG_MODE = True
GEO_SYSTEM = 'ors_vps'  # yandex, google, openrouteservice - cloud ORS, ors_vps - docker ORS
COORD_DATA = './data/coordinates.json'
OUTPUT_FILE = "./data/output.csv"
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
    # Не рекомендуется использовать, слишком явные ограничения для OpenStreetMap
    # '40-foot container': {
    #     'open_profile': 'driving-hgv',
    #     'extras': {
    #         "weight": 30000,  # масса в кг
    #         "height": 4.0,  # метры
    #         "width": 2.5,  # метры
    #         "length": 16.0,  # метры
    #         "axleload": 11000,  # нагрузка на ось в кг
    #         "hazmat": False,  # опасный груз
    #     },
    # },
}
