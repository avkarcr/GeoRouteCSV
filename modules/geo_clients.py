import requests
from abc import ABC, abstractmethod
from colorama import Fore, Style, init

from config import ORS_LOCALPORT, NOMINATIM_LOCALPORT, logger
from modules.decorators import with_retry_on_failure

init(autoreset=True)


class GeoSystem(ABC):
    """
    Базовый интерфейс геосистемы для работы с геокодингом и маршрутами.

    Методы:
    - get_coordinates(name): получить координаты [lon, lat] по названию города|пункта.
    - check_connection(): проверить соединение с сервером по работе с геоданными.
    - get_distance(coord1, coord2): вернуть расстояние в метрах между двумя координатами.

    Атрибуты:
    - vehicle_type: строка с типом транспортного средства, например 'driving-car' или 'driving-hgv'.

    Подклассы должны реализовать свои версии методов под конкретные API: ORS, Yandex, Google и т.д.
    """

    def __init__(self, vehicle_type='driving-car'):
        self.vehicle_type = vehicle_type

    @abstractmethod
    def get_coordinates(self, name: str) -> list:
        """Получить координаты [lon, lat] по названию города/адреса"""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Проверить соединение с сервисом (например, запрос /health или ping)"""
        pass

    @abstractmethod
    def get_distance(self, coord1: list, coord2: list) -> float:
        """
        Вернуть расстояние в метрах между двумя координатами:
        coord1 = [lon1, lat1], coord2 = [lon2, lat2]
        """
        pass


class ORSLocalGeoSystem(GeoSystem):
    """
    Реализация GeoSystem для локального OpenRouteService, запущенного через Docker.

    Работает через эндпоинт http://localhost:PORT/
    где PORT - это туннель в localhost на VPS
    с установленными Nominatim и OSR в докере

    При инициализации задаются два базовых ендпоинта:
    - base_url_geodata - сервер Nominatim для получения координат
    - base_url_direction - сервер OSR для построения маршрутов

    Поддерживает:
    - Геокодинг (поиск координат по названию)
    - Проверку состояния сервера (/health)
    - Расчёт маршрута и получение расстояния
    """

    def __init__(self, vehicle_type='driving-car'):
        super().__init__(vehicle_type)
        self.base_url_geodata = f'http://localhost:{NOMINATIM_LOCALPORT}'
        self.base_url_direction = f'http://localhost:{ORS_LOCALPORT}/ors/v2'

    def check_connection(self) -> bool:
        print("Проверяем соединение с сервером Nominatim...", end='', flush=True)
        try:
            r = requests.get(f"{self.base_url_geodata}/status", timeout=2)
            if r.status_code == 200 and r.text == 'OK':
                print(f" {Fore.GREEN}[OK]{Style.RESET_ALL}")
            else:
                print(f" {Fore.RED}[FAILED] — статус: {r.text}")
                return False
        except Exception as e:
            print(f" {Fore.RED}[FAILED] — ошибка: {e}")
            return False

        print("Проверяем соединение с сервером ORS...", end='', flush=True)
        try:
            r = requests.get(f"{self.base_url_direction}/health", timeout=2)
            if r.status_code == 200 and r.json().get('status') == 'ready':
                print(f" {Fore.GREEN}[OK]{Style.RESET_ALL}")
                return True
            else:
                print(f" {Fore.RED}[FAILED] — статус: {r.text}")
                return False
        except Exception as e:
            print(f" {Fore.RED}[FAILED] — ошибка: {e}")
            return False

    @with_retry_on_failure
    def get_coordinates(self, name: str) -> list:
        """
        Возвращает координаты [lon, lat] для заданного названия (город/адрес)
        """
        try:
            response = requests.get(
                f"{self.base_url_geodata}/search",
                params={'q': name, 'format': 'json', 'limit': 1},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return [data[0]['lat'], data[0]['lon']]
                else:
                    return [False, False]
            else:
                logger.error(f"Город {name}: ошибка при выполнении запроса: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при геокодировании '{name}': {e}")
            return []

    def get_distance(self, coord1: list, coord2: list) -> float:
        """
        Возвращает расстояние между двумя координатами в метрах.
        Формат координат: [lon, lat]
        """
        try:
            response = requests.post(
                f"{self.base_url_direction}/directions/{self.vehicle_type}",
                json={
                    "coordinates": [coord1, coord2]
                },
                timeout=10
            )
            data = response.json()
            return data['routes'][0]['summary']['distance']  # в метрах
        except Exception as e:
            return 0


class ORSCloudGeoSystem(GeoSystem):
    """
    Реализация GeoSystem для облачного решения OpenRouteService.

    Поддерживает:
    - Геокодинг (поиск координат по названию)
    - Проверку состояния сервера (/health)
    - Расчёт маршрута и получение расстояния
    """

    def __init__(self, vehicle_type='driving-car'):
        super().__init__(vehicle_type)
        self.base_url = 'http://localhost:8080/ors/v2'  # debug
        # self.client = openrouteservice.Client(key=get_api_key(GEO_SYSTEM))  todo

    def check_connection(self) -> bool:  # todo
        print("Проверяем соединение с сервером ORS...", end='', flush=True)
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            if r.status_code == 200 and r.json().get('status') == 'ready':
                print(f" {Fore.GREEN}[OK]{Style.RESET_ALL}")
                return True
            else:
                print(f" {Fore.RED}[FAILED] — статус: {r.text}")
                return False
        except Exception as e:
            print(f" {Fore.RED}[FAILED] — ошибка: {e}")
            return False

    def get_coordinates(self, cities):  #client, city_name): todo
        # response = client.request(
        #     '/geocode/search',
        #     get_params={
        #         'text': city_name,
        #         'size': 1,
        #         'boundary.country': 'RU',
        #     },
        # )
        response = {}
        features = response.get('features')
        if not features:
            return "not found"
        if len(features) > 1:
            return "not unique"
        coords = features[0]['geometry']['coordinates']
        # return coords[0], coords[1]
        return coords

    def get_distance(self, coord1: list, coord2: list) -> float:
        """
        Возвращает расстояние между двумя координатами в метрах.
        Формат координат: [lon, lat]
        """
        try:
            response = requests.post(
                f"{self.base_url}/v2/directions/{self.vehicle_type}/geojson",
                json={
                    "coordinates": [coord1, coord2],
                    "instructions": False
                },
                timeout=10
            )
            data = response.json()
            return data['features'][0]['properties']['summary']['distance']  # в метрах
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении маршрута: {e}")
