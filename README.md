# GeoRouteCSV

**GeoRouteCSV** — это инструмент для расчёта расстояний между городами с использованием API [OpenRouteService](https://openrouteservice.org/).  
На вход подаётся JSON-файл со списком пар городов (откуда → куда), на выходе — CSV-файл с расстояниями, рассчитанными на основе выбранного транспортного средства.

---

## 🔧 Предварительная настройка

### Клонируйте репозиторий:
```bash
git clone https://github.com/avkarcr/GeoRouteCSV.git
```
### Убедитесь, что у вас установлен Python 3.9+:
```bash
python --version
```
### Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate   # для Linux/macOS
venv\Scripts\activate      # для Windows
```
### Установите необходимые зависимости
```bash
pip install --upgrade pip && pip install -r requirements.txt
```
## 🚀 Запуск

```bash
python main.py input.json
```
Где input.json — это JSON-файл, содержащий список пар городов (или названий
логистических узлов, например "Станция Ховрино") в формате:
```json
[
  ["Москва", "Хабаровск"],
  ["Станция Ховрино", "Благовещенск"]
]
```
## 📦 Выходной результат
На выходе скрипт генерирует CSV-файл (например, output.csv), содержащий следующие колонки:
- `from_city` — название города отправления  
- `to_city` — название города назначения  
- `distance_km` — расстояние по дороге в километрах
## ⚙️ Настройки транспортного средства
Тип транспорта выбирается в файле config.py.
Пример конфигурации:
```python
vehicle_type = {
    'Driving Car': {
        'open_profile': 'driving-car',
        'extras': None,
    },
    'Heavy Goods Vehicle': {
        'open_profile': 'driving-car',
        'extras': None,
    },
    '40-foot Standard': {
        'open_profile': 'driving-hgv',
        'extras': {
            'weight': 30000,
            'height': 4.0,
            'width': 2.5,
            'length': 16.0,
            'axleload': 11000,
            'hazmat': False
        },
    },
}
```
## 🔐 API-ключи
### OpenRouteService
1. Зарегистрируйтесь на openrouteservice.org (может потребоваться VPN для корректного логина).
2. Для получения API ключа на странице https://openrouteservice.org/dev/#/api-docs необходимо
нажать на серую ссылку "API key" (с правой стороны экрана). 
3. Создайте файл .env в корневой папке проекта на основе примера .env.example и добавьте туда ваш ключ:
```ini
OPENROUTESERVICE_API=ваш_api_ключ
```
## 📁 Структура проекта (основные файлы)
```lua
GeoRouteCSV/
├── data/
│   └── coordinates.json — кэш координат городов для повторного использования
├── main.py — основной скрипт запуска
├── config.py — файл с настройками транспортных средств
├── .env.example — пример .env файла
├── input.json — входной JSON-файл с парами городов
├── output.csv — выходной CSV-файл с расстояниями между городами
├── utils.py — файл с утилитами, необходимыми для работы приложения
├── requirements.txt — список зависимостей для установки через pip
├── LICENSE — лицензия проекта (MIT)
└── README.md — инструкция по использованию проекта
```
## 📌 Примечания
- Скрипт в релизе 1.0 работает только с API OpenRouteService.
- Скрипт автоматически определяет координаты городов с помощью API и дополняет
справочник координат `data/coordinates.json`.
- Если для указанного маршрута не удаётся построить путь, об этом будет выведено предупреждение.
