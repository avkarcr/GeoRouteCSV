import sys
import os
import json

from dotenv import load_dotenv
from config import VEHICLES, DEBUG_MODE, GEO_SYSTEM, COORD_DATA
from pyfiglet import Figlet
from colorama import Fore, Style, init

from modules.geo_clients import ORSLocalGeoSystem, ORSCloudGeoSystem

load_dotenv()
init(autoreset=True)


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
    figlet = Figlet(font='slant')
    banner_text = figlet.renderText('GeoRouteCSV')
    print('=================================================================')
    print(Fore.GREEN + banner_text + Style.RESET_ALL)


def get_open_profile():
    print(f"\nВыберите тип транспортного средства:")
    for i, key in enumerate(VEHICLES.keys(), start=1):
        print(f"{i}. {key}")
    while True:
        try:
            selection = int(input("\nВведите номер: "))
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


def get_json_data():
    data = False
    if DEBUG_MODE:
        input_data = './input.json'
    else:
        input_data = get_json_input_path()
    try:
        with open(input_data, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"❌ Файл не найден: {input_data}")
    except json.JSONDecodeError:
        print(f"❌ Файл {input_data} не является корректным JSON")
    except PermissionError:
        print(f"❌ Нет прав на чтение файла: {input_data}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка при чтении файла: {e}")
    if not data:
        sys.exit(1)
    return data


def get_coord_map():
    data = False
    try:
        with open(COORD_DATA, 'r', encoding='utf-8') as f:
                known_coords = json.load(f)
        for item in known_coords:
            item['lat'] = float(item['lat'])
            item['lon'] = float(item['lon'])
        data = {item['name']: item for item in known_coords}
    except FileNotFoundError:
        print(f"❌ Файл не найден: {COORD_DATA}")
    except json.JSONDecodeError:
        print(f"❌ Файл {COORD_DATA} не является корректным JSON")
    except PermissionError:
        print(f"❌ Нет прав на чтение файла: {COORD_DATA}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка при чтении файла: {e}")
    if not data:
        sys.exit(1)
    return data


def get_geo_client(vehicle_type):
    if GEO_SYSTEM == 'ors_vps':
        client = ORSLocalGeoSystem(vehicle_type=vehicle_type)
    else:
        print(f"❌ Система с геоданными {GEO_SYSTEM} пока не настроена в скрипте.")
        client = False
    if not client:
        sys.exit(1)
    return client
