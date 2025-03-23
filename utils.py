import sys
import os
import json

from dotenv import load_dotenv
from config import VEHICLES
from pyfiglet import Figlet
from colorama import Fore, Style, init

load_dotenv()


def get_api_key(geo_system):
    api_keys = {
        'yandex': os.getenv('YANDEX_API'),
        'google': os.getenv('GOOGLE_API'),
        'openrouteservice': os.getenv('OPENROUTESERVICE_API')
    }
    return api_keys.get(geo_system)


def get_json_input_path():
    if len(sys.argv) < 2:
        print(f"❌ Не указан необходимый параметр - файл json.")
        print_help()
        sys.exit(1)

    json_path = sys.argv[1]

    if not os.path.isfile(json_path):
        print(f"❌ Указанный файл не найден: {json_path}")
        print_help()
        sys.exit(1)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not all(isinstance(pair, list) and len(pair) == 2 for pair in data):
            print(f"❌ Файл {json_path} не соответствует ожидаемому формату.")
            print_help()
            sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при чтении JSON: {e}")
        print_help()
        sys.exit(1)

    return json_path


def print_help():
    print("\n Использование:")
    print("  python script.py input.json\n")
    print("🔹 Где input.json — JSON-файл со списком пар городов:")
    print('  Пример:\n')
    print("""  [
    ["Москва", "Казань"],
    ["Санкт-Петербург", "Новосибирск"]
  ]\n""")


def print_banner():
    init(autoreset=True)
    figlet = Figlet(font='slant')
    banner_text = figlet.renderText('GeoRouteCSV')
    print('=================================================================')
    print(Fore.GREEN + banner_text + Style.RESET_ALL)


def get_coordinates(client, city_name):
    response = client.request(
        '/geocode/search',
        get_params={
            'text': city_name,
            'size': 1,
            'boundary.country': 'RU',
        },
    )
    features = response.get('features')
    if not features:
        return "not found"
    if len(features) > 1:
        return "not unique"
    coords = features[0]['geometry']['coordinates']
    # return coords[0], coords[1]
    return coords


def get_open_profile():
    print(f"\nВыберите тип транспортного средства:")
    for i, key in enumerate(VEHICLES.keys(), start=1):
        print(f"{i}. {key}")
    while True:
        try:
            selection = int(input("Введите номер: "))
            if 1 <= selection <= len(VEHICLES):
                selected_key = list(VEHICLES.keys())[selection - 1]
                selected_profile = VEHICLES[selected_key]
                print(f"\n✅ Вы выбрали: {selected_key}\n")
                break
            else:
                print("⚠️ Неверный номер. Повторите.")
        except ValueError:
            print("⚠️ Введите число.")
    return selected_profile['open_profile'], selected_profile['extras']
