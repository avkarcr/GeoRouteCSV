import json


def read_cities(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        cities = [line.strip() for line in file if line.strip()]
    return cities


source_cities = read_cities('source.txt')
dest_cities = read_cities('destination.txt')
routes = [[source, dest] for source in source_cities for dest in dest_cities]

with open('input.json', 'w', encoding='utf-8') as json_file:
    json.dump(routes, json_file, ensure_ascii=False, indent=4)

print(f'Создан файл input.json с {len(routes)} маршрутами.')
