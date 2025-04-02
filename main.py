import json
import csv
import sys
import time

from logging_config import logger
from config import COORD_DATA, OUTPUT_FILE
from utils import (get_open_profile, get_coord_map, get_geo_client,
                   print_banner, get_json_data)

print_banner()

data = get_json_data()
coord_map = get_coord_map()
logger.info(f'Got coordinates map from COORD_DATA. There are {len(coord_map)} items')
time.sleep(1)

open_profile, extras = get_open_profile()
client = get_geo_client(vehicle_type=open_profile)
if not client.check_connection():
    sys.exit(1)

# Собираем список уникальных названий городов|пунктов
city_names = set()
for pair in data:
    city_names.update(pair)

count_cities = len(city_names)
count_city = 0
logger.info(f'Получено {count_cities} уникальных названий городов')

# Получаем координаты для полученного списка и сохраняем их в файле с координатами
new_coords = []
for city in city_names.copy():
    count_city += 1
    logger.info(f'Город {count_city} из {count_cities}: {city}')
    if city not in coord_map:
        logger.debug(f'No coordinates for {city}. Asking Nominatim for lat and lon...')
        try:
            res = client.get_coordinates(city)
            if len(res) == 0:
                logger.error(f'Произошла ошибка при получении координат для {city}')
                city_names.discard(city)
            elif not res[0]:
                logger.error(f'Город {city} не найден в базе данных')
                city_names.discard(city)
            else:
                lat, lon = res
                logger.success(f"📍 Найдены координаты для {city}: {lat}, {lon}")
                coord_entry = {
                    "name": city,
                    "lat": lat,
                    "lon": lon
                }
                new_coords.append(coord_entry)
                coord_map[city] = coord_entry
                logger.debug(f'Added coords to the coord_map. Total coords: {len(coord_map)}')
        except Exception as e:
            logger.error(f"❌ Ошибка при получении координат для {city}: {e}")
    else:
        logger.debug(f'We already have coordinates for {city} in our coordination map')

all_coords = list(coord_map.values())
with open(COORD_DATA, 'w', encoding='utf-8') as f:
    json.dump(all_coords, f, ensure_ascii=False, indent=2)
logger.success(f"\n✅ База данных координат обновлена с учетом новых городов. Всего городов в базе: {len(all_coords)}\n")
logger.info(f'Ошибки определения геопозиции записаны в файл errors.log\n')

logger.info(f'Очищаем входные данные от городов, координаты по которым не удалось получить...')
del count_city, count_cities, city, new_coords
city_names_normalized = {c.lower() for c in city_names}

routes_to_calculate = []
undefined_routes = []
for city1, city2 in data:
    if city1.lower() in city_names_normalized and city2.lower() in city_names_normalized:
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
    else:
        undefined_routes.append((
            {'name': city1, 'coord': {
                'lat': 'undefined',
                'lon': 'undefined',
            }},
            {'name': city2, 'coord': {
                'lat': 'undefined',
                'lon': 'undefined',
            }},
        ))

with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['from_city', 'to_city', 'distance_km'])
    total_routes = len(routes_to_calculate)
    for c1, c2 in routes_to_calculate:
        coords = [
            [c1['coord']['lon'], c1['coord']['lat']],
            [c2['coord']['lon'], c2['coord']['lat']],
        ]
        result = ""
        try:
            distance_m = client.get_distance(coords[0], coords[1])
            if distance_m != 0:
                result = round(distance_m / 1000, 2)
                c1_name = c1['name']
                c2_name = c2['name']
                logger.success(f'Get distance for {c1_name} - {c2_name}: {result}')
            else:
                logger.error(f'No route calculated for {c1_name} - {c2_name}')
                result = "машрут не может быть построен"
        except Exception as e:
            logger.error(f"❌ Ошибка при получении координат для: {e}")
            result = "ошибка"
        finally:
            writer.writerow([c1['name'], c2['name'], result])

    #     if not extras:
    #         route = directions(client, coords, profile=open_profile)
    #     else:
    #         route = directions(
    #             client,
    #             coords,
    #             profile=open_profile,
    #             options={'profile_params': {'restrictions': extras}}
    #         )

print()
print("Работа скрипта завершена")
