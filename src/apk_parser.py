import io
import re
import tarfile
import urllib.request


def fetch_index(url: str) -> str:
    index_url = url.rstrip('/') + '/APKINDEX.tar.gz'
    with urllib.request.urlopen(index_url) as resp:
        data = resp.read()

    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        for member in tar.getmembers():
            if member.name == 'APKINDEX':
                f = tar.extractfile(member)
                return f.read().decode('utf-8')
    raise ValueError("APKINDEX не найден в архиве")


def parse_packages(text: str) -> dict:
    packages = {}
    current_name = None
    current_deps = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            if current_name:
                packages[current_name] = current_deps
                current_name = None
                current_deps = []
            continue

        if line.startswith('P:'):
            current_name = line[2:]
        elif line.startswith('D:') and current_name:
            raw = line[2:].split()
            current_deps = [re.split(r'[<>=]', d)[0] for d in raw]

    return packages


def get_direct_deps(packages: dict, name: str) -> list:
    if name not in packages:
        raise KeyError(f"Пакет {name} не найден")
    return packages[name]