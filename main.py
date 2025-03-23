import json, itertools

import openrouteservice
from openrouteservice.directions import directions

from config import GEO_SYSTEM, COORD_DATA, DEBUG_MODE
from utils import (get_coordinates, get_open_profile, get_api_key,
                   print_banner, get_json_input_path)

print_banner()

if DEBUG_MODE:
    input_data = './input.json'
else:
    input_data = get_json_input_path()
with open(input_data, 'r') as file:
    data = json.load(file)

api_key = get_api_key(GEO_SYSTEM)
client = openrouteservice.Client(key=api_key)
open_profile, extras = get_open_profile()

with open(COORD_DATA, 'r', encoding='utf-8') as f:
    try:
        known_coords = json.load(f)
    except json.JSONDecodeError:
        print('В файле с координатами ошибка декодирования json')
        exit(1)
coord_map = {item['name']: item for item in known_coords}
new_coords = []

city_names = set()
for pair in data:
    city_names.update(pair)

for city in city_names:
    if city not in coord_map:
        try:
            lon, lat = get_coordinates(client, city)  # формат [lon, lat]
            print(f"📍 Найдены координаты для {city}: {lat}, {lon}")
            coord_entry = {
                "name": city,
                "lat": lat,
                "lon": lon
            }
            new_coords.append(coord_entry)
            coord_map[city] = coord_entry
        except Exception as e:
            print(f"❌ Ошибка при получении координат для {city}: {e}")

all_coords = list(coord_map.values())
with open(COORD_DATA, 'w', encoding='utf-8') as f:
    json.dump(all_coords, f, ensure_ascii=False, indent=2)
print(f"\n✅ Координаты обновлены. Всего городов в базе: {len(all_coords)}\n")

routes_to_calculate = {}
for city1, city2 in data:
    routes_to_calculate.append((
        {'name': city1, 'coord': all_coords[city1]},
        {'name': city2, 'coord': all_coords[city2]}
    ))

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
