import os

def find_string_in_files(search_string, directory="."):
    """
    Ищет строки в файлах рекурсивно в указанной директории.

    :param search_string: Строка, которую нужно найти.
    :param directory: Директория, в которой производится поиск.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        if search_string in line:
                            print(f"Найдено: {search_string} в файле {file_path}, строка {line_num}")
            except (UnicodeDecodeError, PermissionError):
                # Игнорируем файлы, которые нельзя прочитать
                continue

if __name__ == "__main__":
    find_string_in_files("API_BASE_URL")
