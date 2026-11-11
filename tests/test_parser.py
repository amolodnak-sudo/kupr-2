import os
import sys
import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'src'
))
from apk_parser import (
    parse_packages,
    get_direct_deps
)


def test_parse_packages_empty():
    result = parse_packages('')
    assert result == {}


def test_parse_packages_simple():
    index = "P:test_pkg\nV:1.0.0\nD:dep1 dep2\n\n"
    result = parse_packages(index)
    assert 'test_pkg' in result
    assert result['test_pkg'] == ['dep1', 'dep2']


def test_parse_packages_no_deps():
    index = "P:empty_pkg\nV:2.0.0\n\n"
    result = parse_packages(index)
    assert result['empty_pkg'] == []


def test_get_direct_deps():
    packages = {
        'pkg_a': ['pkg_b', 'pkg_c'],
        'pkg_b': ['pkg_d']
    }
    deps = get_direct_deps(packages, 'pkg_a')
    assert deps == ['pkg_b', 'pkg_c']


def test_get_direct_deps_missing():
    packages = {'pkg_a': ['pkg_b']}
    with pytest.raises(KeyError):
        get_direct_deps(packages, 'nonexistent')