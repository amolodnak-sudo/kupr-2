import sys
import argparse

from config_parser import load_config, print_config
from apk_parser import fetch_apk_index, parse_packages, get_direct_deps
from graph_builder import (
    build_graph_bfs,
    get_load_order,
    load_test_graph,
)
from visualizer import (
    to_mermaid,
    save_mermaid,
    render_svg,
    print_ascii_tree,
)

EXIT_SUCCESS = 0
EXIT_ERROR = 1
ENUMERATE_START = 1
MERMAID_FILE = 'graph.mmd'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Визуализация зависимостей APK'
    )
    parser.add_argument(
        '--config',
        default='config.csv',
        help='Путь к конфигурации',
    )
    parser.add_argument(
        '--test-file',
        default=None,
        help='Путь к тестовому файлу',
    )
    return parser.parse_args()


def run_normal_mode(config, package_name):
    print("\n--- Этап 2: Сбор данных ---")
    repo_url = config['repo_url']
    print(f"Загрузка индекса из: {repo_url}")
    index_text = fetch_apk_index(repo_url)
    packages = parse_packages(index_text)

    print(f"\nПрямые зависимости '{package_name}':")
    deps = get_direct_deps(packages, package_name)
    if deps:
        for dep in deps:
            print(f"  - {dep}")
    else:
        print("  (нет зависимостей)")
    return packages


def run_test_mode(config, package_name, test_file=None):
    print("\n--- Этап 3: Тестовый режим ---")
    repo_path = test_file if test_file else config['repo_url']
    print(f"Загрузка тестового графа из: {repo_path}")
    return load_test_graph(repo_path)


def print_graph_info(graph, max_depth):
    print(f"\nГраф зависимостей (макс. глубина: {max_depth}):")
    for pkg, deps in graph.items():
        deps_str = ', '.join(deps) if deps else '(нет)'
        print(f"  {pkg} -> {deps_str}")


def print_load_order(order, package_name):
    print(f"Порядок загрузки для '{package_name}':")
    for index, pkg in enumerate(order, start=ENUMERATE_START):
        print(f"  {index}. {pkg}")


def print_comparison_note():
    print("\n[Сравнение с реальным менеджером пакетов]")
    print("В реальном 'apk' порядок может отличаться.")
    print("Причина: 'apk' использует топологическую")
    print("сортировку, учитывает приоритеты и виртуальные")
    print("пакеты, а наш алгоритм использует BFS.")


def run_visualization(graph, package_name, config):
    print("\n--- Этап 5: Визуализация ---")
    mermaid_code = to_mermaid(graph)
    print("\nMermaid-код:")
    print(mermaid_code)

    save_mermaid(mermaid_code, MERMAID_FILE)
    print(f"\nMermaid-код сохранён: {MERMAID_FILE}")

    output_file = config['output_file']
    try:
        render_svg(MERMAID_FILE, output_file)
        print(f"SVG сохранён: {output_file}")
    except RuntimeError as error:
        print(f"Предупреждение: {error}")
        print("Используйте: https://mermaid.live")

    if config['ascii_tree'].lower() == 'true':
        print("\nASCII-дерево зависимостей:")
        print_ascii_tree(graph, package_name)


def handle_error(error, error_type):
    print(f"{error_type}: {error}", file=sys.stderr)
    return EXIT_ERROR


def main() -> int:
    args = parse_args()

    try:
        config = load_config(args.config)
        print("--- Этап 1: Конфигурация ---")
        print_config(config)

        test_mode = config['test_mode'].lower() == 'true'
        package_name = config['package_name']
        max_depth = int(config['max_depth'])

        if test_mode:
            packages = run_test_mode(
                config, package_name, args.test_file
            )
        else:
            packages = run_normal_mode(config, package_name)

        print("\n--- Этап 3: Построение графа (BFS) ---")
        graph = build_graph_bfs(
            packages, package_name, max_depth
        )

        print_graph_info(graph, max_depth)

        print("\n--- Этап 4: Порядок загрузки ---")
        order = get_load_order(graph, package_name)
        print_load_order(order, package_name)
        print_comparison_note()

        run_visualization(graph, package_name, config)

        return EXIT_SUCCESS

    except FileNotFoundError as error:
        return handle_error(error, "Ошибка: файл не найден")
    except ValueError as error:
        return handle_error(error, "Ошибка конфигурации")
    except KeyError as error:
        return handle_error(error, "Ошибка данных")
    except RuntimeError as error:
        return handle_error(error, "Ошибка выполнения")
    except Exception as error:
        return handle_error(error, "Непредвиденная ошибка")


if __name__ == '__main__':
    sys.exit(main())
