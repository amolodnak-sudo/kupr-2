from collections import deque


def build_graph_bfs(packages, root, max_depth):
    graph = {}
    visited = set()
    queue = deque([(root, 0)])

    while queue:
        pkg, depth = queue.popleft()

        if pkg in visited:
            continue
        visited.add(pkg)

        deps = packages.get(pkg, [])
        graph[pkg] = deps

        if depth < max_depth:
            for dep in deps:
                if dep not in visited:
                    queue.append((dep, depth + 1))

    return graph


def get_load_order(graph, root):
    order = []
    visited = set()
    queue = deque([root])

    while queue:
        pkg = queue.popleft()
        if pkg in visited:
            continue
        visited.add(pkg)
        order.append(pkg)
        for dep in graph.get(pkg, []):
            if dep not in visited:
                queue.append(dep)

    return order


def load_test_graph(path):
    graph = {}
    with open(path, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or '->' not in line:
                continue
            src, dsts = line.split('->')
            src = src.strip()
            deps_raw = dsts.strip()
            if deps_raw:
                deps = [d.strip() for d in deps_raw.split(',')]
            else:
                deps = []
            graph[src] = deps
    return graph


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

    def draw_node(pkg, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(prefix + connector + pkg)

        if pkg in visited:
            return
        visited.add(pkg)

        deps = graph.get(pkg, [])
        for i, dep in enumerate(deps):
            is_last_dep = i == len(deps) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            draw_node(dep, new_prefix, is_last_dep)

    print(root)
    visited.add(root)
    deps = graph.get(root, [])
    for i, dep in enumerate(deps):
        is_last = i == len(deps) - 1
        draw_node(dep, "", is_last)