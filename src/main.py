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


def main() -> int:
    config_path = 'config.csv'

    try:
        config = load_config(config_path)
        print("--- Этап 1: Конфигурация ---")
        print_config(config)

        test_mode = config['test_mode'].lower() == 'true'
        package_name = config['package_name']
        max_depth = int(config['prop_max_depth'] if 'prop_max_depth' in config else config['max_depth'])
        ascii_tree_enabled = config['ascii_tree'].lower() == 'true'
        output_file = config['output_file']

        if test_mode:
            print("\n--- Этап 3: Тестовый режим ---")
            repo_path = config['repo_url']
            print(f"Загрузка тестового графа из: {repo_path}")
            packages = load_test_graph(repo_path)
        else:
            print("\n--- Этап 2: Сбор данных ---")
            repo_url = config['repo_url']
            print(f"Загрузка индекса из: {repo_url}")
            index_text = fetch_apk_index(repo_url)
            packages = parse_packages(index_text)

            print(f"\nПрямые зависимости пакета '{package_name}':")
            deps = get_direct_deps(packages, package_name)
            if deps:
                for dep in deps:
                    print(f"  - {dep}")
            else:
                print("  (нет зависимостей)")

        print("\n--- Этап 3: Построение графа (BFS без рекурсии) ---")
        graph = build_graph_bfs(packages, package_name, max_depth)

        print(f"\nГраф зависимостей (макс. глубина: {max_depth}):")
        for pkg, deps in graph.items():
            deps_str = ', '.join(deps) if deps else '(нет)'
            print(f"  {pkg} -> {deps_str}")

        print("\n--- Этап 4: Порядок загрузки ---")
        order = get_load_order(graph, package_name)
        print(f"Порядок загрузки для '{package_name}':")
        for index, pkg in enumerate(order, start=1):
            print(f"  {index}. {pkg}")

        print("\n[Сравнение с реальным менеджером пакетов]")
        print("В реальном 'apk' порядок может отличаться.")
        print("Причина: 'apk' использует топологическую сортировку,")
        print("учитывает приоритеты и виртуальные пакеты, а наш алгоритм")
        print("использует простой обход в ширину (BFS) по уровню вложенности.")

        print("\n--- Этап 5: Визуализация ---")

        mermaid_code = to_mermaid(graph)
        print("\nMermaid-код:")
        print(mermaid_code)

        mmd_path = 'graph.mmd'
        save_mermaid(mermaid_code, mmd_path)
        print(f"\nMermaid-код сохранён в файл: {mmd_path}")
        print(f"Для конвертации в SVG выполните в терминале:")
        print(f"  mmdc -i {mmd_path} -o {output_file}")
        print("  (или используйте онлайн-редактор https://mermaid.live)")

        if ascii_tree_enabled:
            print("\nASCII-дерево зависимостей:")
            print_ascii_tree(graph, package_name)

        return 0

    except FileNotFoundError as error:
        print(f"Ошибка: Файл не найден - {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        return 1
    except KeyError as error:
        print(f"Ошибка данных: Ключ или пакет не найден - {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"Ошибка выполнения: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Непредвиденная ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())