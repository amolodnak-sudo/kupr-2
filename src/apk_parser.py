import io
import re
import tarfile
import urllib.request


def fetch_apk_index(repo_url):
    index_url = repo_url.rstrip('/') + '/APKINDEX.tar.gz'

    try:
        with urllib.request.urlopen(index_url) as response:
            data = response.read()
    except urllib.error.URLError as error:
        raise RuntimeError(f"Не удалось скачать индекс: {error}")

    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name == 'APKINDEX':
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        return file_obj.read().decode('utf-8')
    except tarfile.TarError as error:
        raise RuntimeError(f"Ошибка распаковки APKINDEX: {error}")

    raise ValueError("Файл APKINDEX не найден в архиве")


def parse_packages(index_text):
    packages = {}
    current_name = None
    current_deps = []

    for line in index_text.splitlines():
        line = line.strip()

        if not line:
            if current_name:
                packages[current_name] = current_deps
                current_name = None
                current_deps = []
            continue

        if line.startswith('P:'):
            current_name = line[2:].strip()
        elif line.startswith('D:') and current_name:
            raw_deps = line[2:].split()
            cleaned = []
            for dep in raw_deps:
                name = re.split(r'[<>=]', dep)[0]
                cleaned.append(name)
            current_deps = cleaned

    if current_name:
        packages[current_name] = current_deps

    return packages


def get_direct_deps(packages, package_name):
    if package_name not in packages:
        raise KeyError(f"Пакет '{package_name}' не найден в репозитории")
    return packages[package_name]