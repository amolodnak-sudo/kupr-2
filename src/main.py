import sys
from config_parser import load_config, print_config


def main() -> int:
    config_path = 'config.csv'
    try:
        config = load_config(config_path)
        print_config(config)
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())