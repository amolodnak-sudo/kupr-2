import re
import subprocess


def sanitize_id(name):
    result = ""
    for ch in name:
        if ch.isalnum() or ch == '_':
            result += ch
        else:
            result += '_'
    if result and result[0].isdigit():
        result = 'n_' + result
    return result


def to_mermaid(graph):
    lines = ["graph TD"]
    all_nodes = set()
    for pkg, deps in graph.items():
        all_nodes.add(pkg)
        all_nodes.update(deps)
    for node in all_nodes:
        nid = sanitize_id(node)
        lines.append(f'    {nid}["{node}"]')
    for pkg, deps in graph.items():
        pkg_id = sanitize_id(pkg)
        for dep in deps:
            dep_id = sanitize_id(dep)
            lines.append(f"    {pkg_id} --> {dep_id}")
    return "\n".join(lines)



def save_mermaid(code, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(code)


def render_svg(mmd_path, svg_path):
    try:
        subprocess.run(
            ['mmdc', '-i', mmd_path, '-o', svg_path],
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        raise RuntimeError("mmdc не установлен")
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Ошибка: {error.stderr}")

def print_ascii_tree(graph, root):
    visited = set()

    def draw(pkg, prefix, is_last):
        connector = "└── " if is_last else "├── "
        print(prefix + connector + pkg)
        if pkg in visited:
            return
        visited.add(pkg)
        deps = graph.get(pkg, [])
        for i, dep in enumerate(deps):
            new_prefix = prefix + ("    " if is_last else "│   ")
            draw(dep, new_prefix, i == len(deps) - 1)

    print(root)
    visited.add(root)
    deps = graph.get(root, [])
    for i, dep in enumerate(deps):
        draw(dep, "", i == len(deps) - 1)