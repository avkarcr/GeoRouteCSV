import os
import sys
import time
import subprocess
from datetime import datetime as dt
import requests

from dotenv import load_dotenv

from config import NOMINATIM_LOCALPORT, ORS_LOCALPORT

load_dotenv()

MIN = 10  # периодичность опроса контейнеров
TOKEN = os.getenv("TELEGRAM_API")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATUS_CHECKS = {
    "Nominatim": {
        "url": f"http://localhost:{NOMINATIM_LOCALPORT}/status",
        "check_fn": lambda r: r.status_code == 200,
        "docker_name": "nominatim",
        "ready": False
    },
    "Openrouteservice": {
        "url": f"http://localhost:{ORS_LOCALPORT}/ors/v2/health",
        "check_fn": lambda r: r.status_code == 200 and r.json().get("status") == "ready",
        "docker_name": "openrouteservice",
        "ready": False
    }
}


def check_service(name: str, service: dict) -> bool:
    try:
        response = requests.get(service["url"], timeout=5)
        return service["check_fn"](response)
    except Exception as e:
        return False


def notify(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[{dt.now()}] Ошибка отправки сообщения от Telegram бота, "
              f"проверьте API и CHAT_ID в переменных окружения. "
              f"Отправьте боту команду /start.\nСкрипт завершает работу.")
        sys.exit(1)


def is_docker_up(container_keyword: str) -> bool:

    # debug
    if container_keyword == 'openrouteservice':
        return True

    try:
        output = subprocess.check_output(["docker", "ps", "--format", "{{.Names}} {{.Status}}"])
        lines = output.decode().splitlines()
        for line in lines:
            if container_keyword in line and "Up" in line:
                return True
        return False
    except Exception as e:
        return False


def main():
    notify(f"Начинаем мониторить установку GeoRouteCSV каждые {MIN} минут")
    start_time = int(time.time())
    count = 0
    while not all(service["ready"] for service in STATUS_CHECKS.values()):
        now_count = int(time.time())
        hours_passed = (now_count - start_time) // 3600
        if hours_passed > count:
            count = hours_passed
            notify(f"Прошло {count} ч. с начала мониторинга...")

        now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Проверка: продолжается процесс установки...")
        for name, service in STATUS_CHECKS.items():
            if not service["ready"]:
                if not is_docker_up(service["docker_name"]):
                    notify(f"{name}: контейнер Docker остановился. Завершаю работу.")
                    print(f"[FATAL] {name}: контейнер не запущен. Завершаем.")
                    return
                if check_service(name, service):
                    notify(f"{name} готов к работе")
                    service["ready"] = True
        time.sleep(MIN*60)
    notify("Завершено отслеживание установки всех сервисов.")


if __name__ == '__main__':
    main()
