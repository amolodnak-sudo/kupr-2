import subprocess


def sanitize_id(name):
    result = ''
    for ch in name:
        if ch.isalnum() or ch == '_':
            result += ch
        else:
            result += '_'

    if result and result[0].isdigit():
        result = 'pkg_' + result

    return result


def to_mermaid(graph):
    lines = ['graph TD']

    all_nodes = set()
    for pkg, deps in graph.items():
        all_nodes.add(pkg)
        all_nodes.update(deps)

    for node in all_nodes:
        safe_id = sanitize_id(node)
        lines.append(f'    {safe_id}["{node}"]')

    for pkg, deps in graph.items():
        pkg_id = sanitize_id(pkg)
        for dep in deps:
            dep_id = sanitize_id(dep)
            lines.append(f"    {pkg_id} --> {dep_id}")

    return '\n'.join(lines)


def save_mermaid(mermaid_code, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(mermaid_code)


def render_svg(mmd_path, svg_path):
    try:
        subprocess.run(
            ['mmdc', '-i', mmd_path, '-o', svg_path],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError("mmdc не установлен")
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Ошибка mmdc: {error.stderr}")


def print_ascii_tree(graph, root, prefix='', visited=None):
    if visited is None:
        visited = set()

    if root in visited:
        print(f"{prefix}└── {root} (цикл)")
        return

    visited.add(root)
    print(f"{prefix}{root}")

    deps = graph.get(root, [])
    for i, dep in enumerate(deps):
        if i < len(deps) - 1:
            print(f"{prefix}├── ", end='')
            print_ascii_tree(graph, dep, prefix + '│   ', visited)
        else:
            print(f"{prefix}└── ", end='')
            print_ascii_tree(graph, dep, prefix + '    ', visited)
