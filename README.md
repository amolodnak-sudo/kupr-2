

## Описание

Программа анализирует зависимости пакета
в репозитории Alpine Linux и строит граф
зависимостей с визуализацией в формате
Mermaid/SVG.

Используется алгоритм BFS без рекурсии
для обхода графа с учётом максимальной
глубины и циклических зависимостей.

## Структура проекта
```
kupr-2/
├── src/
│ ├── main.py # Точка входа
│ ├── config_parser.py # Парсер CSV
│ ├── apk_parser.py # Парсер APKINDEX
│ ├── graph_builder.py # BFS и граф
│ └── visualizer.py # Mermaid/SVG
├── tests/
│ ├── test_config.py
│ ├── test_parser.py
│ └── test_graph.py
├── config.csv # Конфигурация
├── run.sh / run.bat # Скрипт запуска
└── README.md
```

## Настройки (config.csv)

| Параметр      | Описание                              |
|---------------|---------------------------------------|
| package_name  | Имя анализируемого пакета             |
| repo_url      | URL репозитория или путь к файлу      |
| test_mode     | Режим тестового репозитория (true/false) |
| output_file   | Имя выходного SVG-файла               |
| ascii_tree    | Вывод ASCII-дерева (true/false)       |
| max_depth     | Максимальная глубина анализа          |

## Установка и запуск

### Требования
- Python 3.8+
- Node.js (для конвертации Mermaid в SVG)
- Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`

### Запуск программы
```bash
# Linux/Mac
./run.sh

# Windows
run.bat

# Или напрямую
python src/main.py
```

 ### Запуск тестов
```bash
python -m pytest tests/ -v
```

# Примеры использования
## Пример 1: Анализ пакета curl
```
config.csv:
key,value
package_name,curl
repo_url,https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64/
test_mode,false
output_file,graph.svg
ascii_tree,true
max_depth,3
```

### Запуск:
```bash
python src/main.py
```
### Вывод:
```
--- Этап 1: Конфигурация ---
package_name: curl
repo_url: https://dl-cdn.alpinelinux.org/...
test_mode: false
output_file: graph.svg
ascii_tree: true
max_depth: 3

--- Этап 2: Сбор данных ---
Прямые зависимости 'curl':
  - libcurl
  - so:libc.musl-x86_64.so.1
  - so:libcurl.so.4
  - so:libz.so.1

--- Этап 3: Построение графа (BFS) ---
  curl -> libcurl, so:libc.musl-x86_64.so.1, ...

--- Этап 4: Порядок загрузки ---
  1. curl
  2. libcurl
  ...

--- Этап 5: Визуализация ---
Mermaid-код сохранён в graph.mmd
SVG-изображение сохранено: graph.svg
```

## Пример 2: Тестовый режим
```config.csv
csv
key,value
package_name,A
repo_url,tests/test_repo.txt
test_mode,true
output_file,graph.svg
ascii_tree,true
max_depth,5
```

```tests/test_repo.txt
A -> B, C
B -> D
C -> D, E
D -> A
E ->
```

## Сравнение с реальным apk

### Реальный вывод apk:
```bash
$ apk info --depends curl
libcurl
so:libc.musl-x86_64.so.1
so:libcurl.so.4
so:libz.so.1
```

### Наш вывод:
```
Прямые зависимости 'curl':
  - libcurl
  - so:libc.musl-x86_64.so.1
  - so:libcurl.so.4
  - so:libz.so.1
```
### Расхождения:
```
Прямые зависимости совпадают. Однако порядок загрузки отличается:
apk использует топологическую сортировку (сначала устанавливает зависимости без своих зависимостей)
Наш алгоритм использует BFS (сначала корень, потом его зависимости)
Это объясняется тем, что apk должен гарантировать, что все зависимости установлены до установки зависимого пакета.
```