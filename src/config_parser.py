import csv
import os


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    config = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            config[row['key']] = row['value']

    _validate(config)
    return config


def _validate(config: dict) -> None:
    required = [
        'package_name', 'repo_url', 'test_mode',
        'output_file', 'ascii_tree', 'max_depth'
    ]
    for key in required:
        if key not in config or not config[key]:
            raise ValueError(f"Отсутствует параметр: {key}")

    if not config['max_depth'].isdigit():
        raise ValueError("max_depth должен быть числом")


def print_config(config: dict) -> None:
    for key, value in config.items():
        print(f"{key}: {value}")