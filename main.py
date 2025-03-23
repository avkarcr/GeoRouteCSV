import json, itertools

import openrouteservice
from openrouteservice.directions import directions

from config import GEO_SYSTEM, DATA, DEBUG_MODE
from utils import (get_coordinates, get_open_profile, get_api_key,
                   get_calc_method, print_banner, get_json_input_path)

print_banner()

if DEBUG_MODE:
    input_data_test = './input_cities.json'
else:
    input_data_test = get_json_input_path()

MODE = get_calc_method()
input_data = DATA[MODE]

api_key = get_api_key(GEO_SYSTEM)
client = openrouteservice.Client(key=api_key)
open_profile, extras = get_open_profile()

routes_to_calculate = []

if MODE == 'manual':
    city1_name = input('Введите первый город (ОТКУДА): ')
    city2_name = input('Введите второй город (КУДА): ')
    city1_coord = get_coordinates(client, city1_name)
    city2_coord = get_coordinates(client, city2_name)
    routes_to_calculate.append((
        {'name': city1_name, 'coord': city1_coord},
        {'name': city2_name, 'coord': city2_coord}
    ))
elif MODE == 'cities':
    with open(input_data, 'r') as file:
        data = json.load(file)
    city_names = set()
    for pair in data:
        city_names.update(pair)
    city_coords = {}
    for city_name in city_names:
        city_coords[city_name] = get_coordinates(client, city_name)
    for city1, city2 in data:
        routes_to_calculate.append((
            {'name': city1, 'coord': city_coords[city1]},
            {'name': city2, 'coord': city_coords[city2]}
        ))
elif MODE == 'coordinates':
    with open(input_data, 'r') as file:
        data = json.load(file)
    for city1, city2 in itertools.combinations(data, 2):
        routes_to_calculate.append((
            {'name': city1['name'], 'coord': [city1['lon'], city1['lat']]},
            {'name': city2['name'], 'coord': [city2['lon'], city2['lat']]}
        ))
else:
    raise KeyError("Ошибка MODE в config.py")

for c1, c2 in routes_to_calculate:
    coords = [c1['coord'], c2['coord']]
    try:
        if not extras:
            route = directions(client, coords, profile=open_profile)
        else:
            route = directions(client, coords, profile=open_profile,
                               options={'profile_params': {'restrictions': extras}})
        distance_m = route['routes'][0]['summary']['distance']
        distance_km = distance_m / 1000
        print(f"🚛 {c1['name']} → {c2['name']}: {distance_km:.1f} км")

    except Exception as e:
        print(f"❌ Ошибка при расчёте маршрута {c1['name']} → {c2['name']}: {e}")
