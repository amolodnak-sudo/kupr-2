import os
import sys
import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'src'
))
from graph_builder import (
    build_graph_bfs,
    get_load_order,
    load_test_graph
)


def test_build_graph_bfs_simple():
    packages = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': [],
        'D': []
    }
    graph = build_graph_bfs(packages, 'A', 2)
    assert 'A' in graph
    assert 'B' in graph
    assert 'C' in graph


def test_build_graph_bfs_cycle():
    packages = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A']
    }
    graph = build_graph_bfs(packages, 'A', 5)
    assert len(graph) <= 3
    assert 'A' in graph


def test_build_graph_bfs_depth_limit():
    packages = {
        'A': ['B'],
        'B': ['C'],
        'C': ['D']
    }
    graph = build_graph_bfs(packages, 'A', 1)
    assert 'A' in graph
    assert 'B' in graph
    assert 'C' not in graph


def test_get_load_order():
    graph = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': [],
        'D': []
    }
    order = get_load_order(graph, 'A')
    assert order[0] == 'A'
    assert 'B' in order
    assert 'D' in order


def test_load_test_graph(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text(
        "A -> B, C\n"
        "B -> D\n"
        "C ->\n"
        "D ->"
    )
    graph = load_test_graph(str(test_file))
    assert graph['A'] == ['B', 'C']
    assert graph['B'] == ['D']
    assert graph['C'] == []