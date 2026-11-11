import sys

from config_parser import load_config, print_config
from apk_parser import fetch_apk_index, parse_packages, get_direct_deps
from graph_builder import (
    build_graph_bfs,
    get_load_order,
    load_test_graph,
    to_mermaid,
    save_mermaid,
    print_ascii_tree
)
from visualizer import (
    to_mermaid,
    save_mermaid,
    render_svg,
    print_ascii_tree
)
EXIT_SUCCESS = 0
EXIT_ERROR = 1
ENUMERATE_START = 1


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


def run_test_mode(config, package_name):
    print("\n--- Этап 3: Тестовый режим ---")
    repo_path = config['repo_url']
    print(f"Загрузка тестового графа из: {repo_path}")
    return load_test_graph(repo_path)


def run_visualization(graph, package_name, config):
    print("\n--- Этап 5: Визуализация ---")
    mermaid_code = to_mermaid(graph)
    print("\nMermaid-код:")
    print(mermaid_code)

    mmd_path = 'graph.mmd'
    save_mermaid(mermaid_code, mmd_path)
    print(f"\nMermaid-код сохранён в файл: {mmd_path}")
    print("Для конвертации в SVG используем: mmdc -i graph.mmd -o graph.svg")
    print("или онлайн-редактор https://mermaid.live")

    if config['ascii_tree'].lower() == 'true':
        print("\nASCII-дерево зависимостей:")
        print_ascii_tree(graph, package_name)


def main() -> int:
    config_path = 'config.csv'

    try:
        config = load_config(config_path)
        print("--- Этап 1: Конфигурация ---")
        print_config(config)

        test_mode = config['test_mode'].lower() == 'true'
        package_name = config['package_name']
        max_depth = int(config['max_depth'])

        if test_mode:
            packages = run_test_mode(config, package_name)
        else:
            packages = run_normal_mode(config, package_name)

        print("\n--- Этап 3: Построение графа (BFS без рекурсии) ---")
        graph = build_graph_bfs(packages, package_name, max_depth)

        print(f"\nГраф зависимостей (макс. глубина: {max_depth}):")
        for pkg, deps in graph.items():
            deps_str = ', '.join(deps) if deps else '(нет)'
            print(f"  {pkg} -> {deps_str}")

        print("\n--- Этап 4: Порядок загрузки ---")
        order = get_load_order(graph, package_name)
        print(f"Порядок загрузки для '{package_name}':")
        for index, pkg in enumerate(order, start=ENUMERATE_START):
            print(f"  {index}. {pkg}")

        print("\n[Сравнение с реальным менеджером пакетов]")
        print("В реальном 'apk' порядок может отличаться.")
        print("Причина: 'apk' использует топологическую сортировку,")
        print("учитывает приоритеты и виртуальные пакеты, а наш")
        print("алгоритм использует простой обход в ширину (BFS).")

        run_visualization(graph, package_name, config)

        return EXIT_SUCCESS

    except FileNotFoundError as error:
        print(f"Ошибка: Файл не найден - {error}", file=sys.stderr)
        return EXIT_ERROR
    except ValueError as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        return EXIT_ERROR
    except KeyError as error:
        print(f"Ошибка данных: {error}", file=sys.stderr)
        return EXIT_ERROR
    except RuntimeError as error:
        print(f"Ошибка выполнения: {error}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:
        print(f"Непредвиденная ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())