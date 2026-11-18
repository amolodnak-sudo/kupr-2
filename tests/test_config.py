import os
import sys
import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'src'
))
from config_parser import load_config


def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.csv"
    config_file.write_text(
        "key,value\n"
        "package_name,test_pkg\n"
        "repo_url,https://example.com\n"
        "test_mode,false\n"
        "output_file,test.svg\n"
        "ascii_tree,true\n"
        "max_depth,3"
    )

    config = load_config(str(config_file))
    assert config['package_name'] == 'test_pkg'
    assert config['max_depth'] == '3'


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config('nonexistent.csv')


def test_load_config_missing_field(tmp_path):
    config_file = tmp_path / "config.csv"
    config_file.write_text(
        "key,value\n"
        "package_name,test_pkg\n"
    )

    with pytest.raises(ValueError):
        load_config(str(config_file))