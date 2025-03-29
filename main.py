import json
import csv
import sys

from openrouteservice.directions import directions

from config import COORD_DATA, OUTPUT_FILE
from utils import (get_open_profile, get_coord_map, get_geo_client,
                   print_banner, get_json_data)

print_banner()

data = get_json_data()
coord_map = get_coord_map()
open_profile, extras = get_open_profile()
client = get_geo_client(vehicle_type=open_profile)
if not client.check_connection():
    sys.exit(1)

# Собираем список уникальных названий городов|пунктов
city_names = set()
for pair in data:
    city_names.update(pair)

# Получаем координаты для полученного списка и сохраняем их в файле с координатами
new_coords = []
for city in city_names:
    if city not in coord_map:
        try:
            res = client.get_coordinates(city)
            if len(res) != 0:
                break
            lon, lat = res
            print(f"📍 Найдены координаты для {city}: {lat}, {lon}")
            coord_entry = {
                "name": city,
                "lat": lat,
                "lon": lon
            }
            new_coords.append(coord_entry)
            coord_map[city] = coord_entry
            print(f"\n✅ Координаты обновлены.")
        except Exception as e:
            print(f"❌ Ошибка при получении координат для {city}: {e}")

all_coords = list(coord_map.values())
with open(COORD_DATA, 'w', encoding='utf-8') as f:
    json.dump(all_coords, f, ensure_ascii=False, indent=2)
print(f"✅ Всего городов в базе: {len(all_coords)}\n")

routes_to_calculate = []
for city1, city2 in data:
    routes_to_calculate.append((
        {'name': city1, 'coord': {
            'lat': coord_map[city1]['lat'],
            'lon': coord_map[city1]['lon'],
        }},
        {'name': city2, 'coord': {
            'lat': coord_map[city2]['lat'],
            'lon': coord_map[city2]['lon'],
        }},
    ))

with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['from_city', 'to_city', 'distance_km'])

    for c1, c2 in routes_to_calculate:
        coords = [
            [c1['coord']['lon'], c1['coord']['lat']],
            [c2['coord']['lon'], c2['coord']['lat']],
        ]
        try:
            if not extras:
                route = directions(client, coords, profile=open_profile)
            else:
                route = directions(
                    client,
                    coords,
                    profile=open_profile,
                    options={'profile_params': {'restrictions': extras}}
                )

            distance_m = route['routes'][0]['summary']['distance']
            distance_km = round(distance_m / 1000, 2)

            print(f"🚛 {c1['name']} → {c2['name']}: {distance_km:.2f} км")

            writer.writerow([c1['name'], c2['name'], distance_km])

        except Exception as e:
            print(f"❌ Ошибка при расчёте маршрута {c1['name']} → {c2['name']}: {e}")



# from ors_local import ORSLocalGeoSystem
#
# geo = ORSLocalGeoSystem(vehicle_type='driving-hgv')
#
# geo.check_connection()
#
# coord1 = geo.get_coordinates("Станция Силикатная")
# coord2 = geo.get_coordinates("Барнаул")
#
# distance = geo.get_distance(coord1, coord2)
# print(f"Расстояние: {distance / 1000:.2f} км")