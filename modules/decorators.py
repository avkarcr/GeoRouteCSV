import time
import sys
import requests
from config import MAX_DELAY


def with_retry_on_failure(func):
    """
    Декоратор, повторяющий вызов функции при сбое соединения с сервером.
    Повторяется с увеличивающейся задержкой (экспоненциально) до MAX_DELAY секунд.
    """

    def wrapper(*args, **kwargs):
        delay = 5
        total_wait = 0

        while True:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(f"🛑 Нет связи с сервером: {e}")
                print(f"⏳ Ждём {delay} секунд перед повтором...")

                time.sleep(delay)
                total_wait += delay
                delay = min(delay * 2, MAX_DELAY)

                if total_wait >= MAX_DELAY:
                    print(f"❌ Превышено максимальное время ожидания {MAX_DELAY} секунд. Завершаем.")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Ошибка в функции {func.__name__}: {e}")
                raise e  # пробрасываем прочие ошибки

    return wrapper
