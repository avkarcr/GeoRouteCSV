import pandas as pd
import json
import sys
import os


def convert_excel_to_json(excel_path, output_path='./data/input.json'):
    if not os.path.isfile(excel_path):
        print(f"❌ Файл не найден: {excel_path}")
        return

    try:
        df = pd.read_excel(excel_path, usecols=[0, 1], header=None)
    except Exception as e:
        print(f"❌ Ошибка при чтении Excel: {e}")
        return

    pairs = []
    for index, row in df.iterrows():
        from_city = str(row[0]).strip()
        to_city = str(row[1]).strip()
        if from_city and to_city:
            pairs.append([from_city, to_city])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    print(f"✅ Успешно: {len(pairs)} маршрутов сохранено в {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🛈 Использование:")
        print("  python convert_excel_json.py путь_к_excel.xlsx")
        sys.exit(1)

    excel_file = sys.argv[1]
    convert_excel_to_json(excel_file)
