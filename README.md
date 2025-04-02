# GeoRouteCSV

**GeoRouteCSV** — это инструмент для расчёта расстояний между городами с использованием API [OpenRouteService](https://openrouteservice.org/).  
На вход подаётся JSON-файл со списком пар городов (откуда → куда), на выходе — CSV-файл с расстояниями, рассчитанными на основе выбранного транспортного средства.
---

## 🔧 Предварительная настройка

### 😵‍ Характеристики VPS для установки экземляров необходимого ПО (OpenRouteService и Nominatim)
- Ubuntu 22.04
- 4 CPU
- 16 Gb RAM
- 250 Gb SSD (для работы с картой России)

### Выполните базовую настройку сервера:
```bash
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y
reboot
```

### Убедитесь, что у вас установлен Python версии не ниже 3.9:
```bash
python3 --version
```

### Установите необходимые программы:
```bash
sudo apt install tmux iptables curl wget jq git python3-venv ca-certificates gpg -y
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Настройте Firewall:
```bash
iptables -F INPUT
iptables -P INPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -i lo -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -P INPUT DROP
sudo mkdir -p /etc/iptables/
sudo iptables-save > /etc/iptables/rules.v4
sudo echo "iptables-restore < /etc/iptables/rules.v4" >> /etc/profile
```

### Все дальнейшие действия рекомендуется выполнять в сессии tmux. Запустите новую сессию tmux:
```bash
tmux new
```
- Для сворачивания сессии нажмите одновременно ctrl+b, а потом клавишу d.
- Для возобновления сессии введите `tmux attach`.
- Для других параметров tmux читаем [шпаргалку](https://habr.com/ru/articles/126996/).

Если связь с сервером пропадет, то при повторном подключении к серверу процесс установки не прервется.
Подключаетесь и активируете ранее созданную сессию tmux.

### Скачайте необходимые карты в формате OpenStreetMap (ниже - примеры, выберите нужную вам карту на сайте https://download.geofabrik.de):
```bash
mkdir -p ~/maps
cd ~/maps
wget https://download.geofabrik.de/russia-latest.osm.pbf
```

### Справочно (для продвинутых пользователей):
Если требуется использовать несколько карт сразу, то их надо объединить:
```bash
sudo apt install osmium-tool
cd ~/maps && osmium merge russia-latest.osm.pbf some-other-map-latest.osm.pbf -o merged-map.osm.pbf
```
После объединения карт измените название файла в docker-compose и настройте обновления самостоятельно следуя [инструкции](https://nominatim.org/release-docs/latest/admin/Advanced-Installations/#importing-multiple-regions-with-updates)

## 💚 Установка приложений

### В дальнейших шагах по настройке предполагается, что вы будете использовать карту России: в каталоге `~/maps` должен лежать файл `russia-latest.osm.pbf`.

### Клонируйте репозиторий:
```bash
cd ~ && git clone https://github.com/avkarcr/GeoRouteCSV.git
```

### Создайте виртуальное окружение:
```bash
cd ~/GeoRouteCSV && python3 -m venv venv
source venv/bin/activate
```

### Установите необходимые зависимости (далее все делаем в виртуальном окружении venv):
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### Настройка переменных окружения

#### Создайте файл .env по примеру .env.example и добавьте туда свои данные:
```bash
mv .env.example .env
vim .env
```
Чтобы начать редактировать файл нажмите Insert,
когда закончите редактировать, нажимайте ESC, а потом `:wq` и Enter.

#### Придумайте свой пароль для Nominatim и впишите URL для обновления карт
```bash
mv .env.example .env
```

NOMINATIM_PASSWORD=12345
REPLICATION_URL=https://download.geofabrik.de/russia-updates/


### Запускаем образы докер:
```bash
docker compose --env-file .env.docker up -d
```
Установка контейнеров занимает **НЕСКОЛЬКО ЧАСОВ**, наберитесь терпения.
Можно создать миниатюрного бота в телеграмм и прописать API и свой ID в .env.
Тогда бот напишет, когда установка завершится.
Или сообщит об ошибке, если контейнер "отвалится".

### Отслеживание окончания установки с помощью телеграм бота:
Отслеживание окончания установки с помощью телеграм бота может быть весьма удобно.
- Создайте бота в BotFather Telegram
- Добавьте токен бота и свой id в .env
- Запускайте скрипт в сессии tmux, он будет крутиться до тех пор,
пока все программы не установятся, либо установка не завершится ошибкой docker.
- Опрос статуса скрипт делает раз в 10 минут, можете поменять этот параметр в файле tg_notify.py.
- Виртуальное окружение venv должно быть активно.

Вот команды:
```bash
cd ~/GeoRouteCSV
source venv/bin/activate
cd tools
python tg_notify.py
```

## 🚀 Использование скрипта

После длительной подготовки и установки неоходимого ПО мы получим:

- **Nominatim**

Инструмент для геокодирования, позволяющий преобразовывать названия мест и адреса
в географические координаты и наоборот. Он использует данные OpenStreetMap
и обеспечивает быстрый и точный поиск местоположений.

- **OpenRouteService**

Сервис, предоставляющий услуги по построению маршрутов, расчету изохрон,
матриц расстояний и времени в пути. Сервис основан на данных OpenStreetMap
и предлагает гибкие возможности для планирования маршрутов с учетом различных параметров.

**Найстройки в данном проекте позволяют рассчитывать маршрут для автомобилей и грузовиков.**

### Как запустить
При запуска скрипта предполагается, что у нас есть файл input.json с машрутами.
Как сгенерировать этот файл, читаем в подразделе [входные данные для скрипта](#входные-данные-для-скрипта).
```bash
cd ~/GeoRouteCSV
source venv/bin/activate
python main.py ./data/input.json
```
После отработки скрипта мы получим три основных файла в каталоге `GeoRouteCSV/data`:
- **coordinates.json** - файл с географическими координатами городов и пунктов `input.json`
- **errors.log** - файл с ошибками, связанными с определением координат и построением машрутов
- **output.csv** - итоговый файл с расстояниями между городами в км

Итоговый файл `output.csv` имеет следующую структуру:
- `from_city` — название города/пункта отправления  
- `to_city` — название города/пункта назначения  
- `distance_km` — расстояние для выбранного транспортного средства в километрах

Выбрать тип транспортного средства можно будет при запуске скрипта.

### Входные данные для скрипта:
Скрипт обрабатывает машруты, указанные в файле JSON (в нашем примере `input.json`),
который имеет следующую структуру:
```json
[
  ["Станция Селятино", "Казань"],
  ["Станция Селятино", "Благовещенск"],
  ["Станция Ховрино", "Казань"],
  ["Станция Ховрино", "Благовещенск"]
]
```
Этот файл вы можете создать либо вручную для небольшого количества машрутов,
либо воспользоваться утилитами, которые описаны ниже.

## 🛠️ Полезные утилиты (дополнительно)
В каталоге GeoRouteCSV/tools вы найдете несколько полезных дополнительных утилит:
1. `check.sh`
Эта утилита запускается в командой строке bash и показывает статус установки
в текущий момент времени. Удобно, если вы не хотите возиться с ботом в телеграме.
```bash
$HOME/GeoRouteCSV/tools/check.sh
```
2. `convert_excel_json.py`
Эта утилита нужна, чтобы сделать файл с машрутами в формате, понятном GeoRouteCSV.
Вы берете файл Excel, в столбец A вписываете город отправления,
а напротив в столбец B - город назначения.
**Без заголовков!**
<table>
  <tr><td>Москва</td><td>Санкт-Петербург</td></tr>
  <tr><td>Казань</td><td>Самара</td></tr>
  <tr><td>Екатеринбург</td><td>Новосибирск</td></tr>
</table>

Не забываем **включать виртуальное окружение** для запуска любых скриптов python.
Копируете Excel-файл на сервер и запускаете утилиту:
```bash
python $HOME/GeoRouteCSV/tools/convert_excel_json.py input.xlsx
```
На выходе получим файл `input.json` в нужном формате.
Этот файл можно использовать в дальнейшем для расчета машрутов.
3. `mix_routes_from_files.py`
Эта утилита нужна, если у вас есть отдельно список из **N** городов `destination.txt`
и список из **M** логистических пунктов отправления `source.txt`.
Утилита просто комбинирует каждый логистический пункт из файла `source.txt`
и собирает прописывает для него машруты до всех городов из файла `destination.txt`.
Таким образом, мы получим N*M машрутов.
Не забываем **включать виртуальное окружение** для запуска любых скриптов python.
Разместите файлы `source.txt` и `destination.txt` в директории tools и запустите скрипт:
```bash
cd $HOME/GeoRouteCSV/tools
python mix_routes_from_files.py
```
В папке tools будет создан `input.json` — это JSON-файл, содержащий список **N*M** комбинаций
логистических узлов и городов.

## 📁 Структура проекта (основные файлы)
```lua
GeoRouteCSV/
├── data/
│   ├── input.json — файл с машрутами
│   ├── coordinates.json — кэш координат городов для повторного использования
│   ├── errors.log — лог ошибок при обработке машрутов и поиску координат
│   └── output.csv — выходной CSV-файл с расстояниями между городами
├── modules/
│   ├── decorators.py — рабочий скрипт с декораторами
│   └── geo_clients.py — рабочий скрипт с классами для Геомодулей
├── tools/
│   ├── check.sh — bash-утилита для проверки установки ПО
│   ├── convert_excel_json.py — утилита для конвертации XLSX в JSON
│   ├── mix_routes_from_files.py — утилита для формирования машрутов из списков пунктов и городов
│   └── tg_notify.py — утилита для информирования об окончании установки ПО в Телеграме
├── ors-docker/
│   └── ors-config.yml — файл с настройками профилей OpenRouteService
├── .env.example — пример .env файла
├── main.py — основной скрипт запуска
├── config.py — файл с настройками
├── docker-compose.yml — файл для запуска докер-образов
├── .env.docker — файл с переменными окружения для докера
├── utils.py — файл с утилитами, необходимыми для работы приложения
├── requirements.txt — список зависимостей для установки через pip
├── LICENSE — лицензия проекта (MIT)
├── README.md — инструкция по использованию проекта
└── .git/, .gitignore, .idea/ и пр. — прочие системные файлы и каталоги
```
## 📌 Примечания
- Скрипт в релизе 1.0 работает только с OpenRouteService, установленным через докер.
