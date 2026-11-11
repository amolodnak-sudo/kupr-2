
def to_mermaid(graph):
    lines = ["graph TD"]
    for pkg, deps in graph.items():
        if not deps:
            lines.append(f"    {pkg}[{pkg}]")
        for dep in deps:
            lines.append(f"    {pkg}[{pkg}] --> {dep}[{dep}]")
    return "\n".join(lines)


def save_mermaid(code, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(code)


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
            is_last_dep = i == len(deps) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            draw(dep, new_prefix, is_last_dep)

    print(root)
    visited.add(root)
    deps = graph.get(root, [])
    for i, dep in enumerate(deps):
        is_last_dep = i == len(deps) - 1
        draw(dep, "", is_last_dep)