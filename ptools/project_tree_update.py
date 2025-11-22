#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path


class ProjectTreeUpdater:
    """Пример использования из директории проекта: python ptools/project_tree_update.py ../ ptools/target_structure.txt
    """
    def __init__(self):
        self.created_count = 0

    def parse_tree_structure(self, tree_file_path):
        """Парсит текстовое дерево проекта и возвращает структуру"""
        with open(tree_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        structure = {}
        current_path = []

        for line in lines:
            line = line.rstrip()
            if not line:
                continue

            # Удаляем символы дерева (├──, └──, │) и оставляем только отступы
            clean_line = re.sub(r'[├└──│]', '', line).strip()
            if not clean_line:
                continue

            # Определяем уровень вложенности по количеству пробелов
            indent_level = self.get_indent_level(line)

            # Обновляем текущий путь
            current_path = current_path[:indent_level]

            if clean_line.endswith('/'):
                # Это директория
                dir_name = clean_line[:-1].strip()
                current_path.append(dir_name)
                full_path = '/'.join(current_path)
                structure[full_path] = 'directory'
            else:
                # Это файл - убираем комментарии если есть
                file_name = clean_line.split(' # ')[0].strip()
                full_path = '/'.join(current_path + [file_name])
                structure[full_path] = 'file'

        return structure

    def get_indent_level(self, line):
        """Определяет уровень отступа"""
        # Считаем что каждый уровень = 4 пробела, но игнорируем символы дерева
        clean_line = re.sub(r'[├└──│]', ' ', line)
        spaces = len(clean_line) - len(clean_line.lstrip())
        return spaces // 4

    def create_missing_items(self, project_root, target_structure):
        """Создает отсутствующие файлы и папки"""
        project_path = Path(project_root)

        # Сначала создаем все директории
        for item_path, item_type in target_structure.items():
            if item_type == 'directory':
                full_path = project_path / item_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    print(f"Создана директория: {item_path}")
                    self.created_count += 1

        # Затем создаем файлы
        for item_path, item_type in target_structure.items():
            if item_type == 'file':
                full_path = project_path / item_path
                if not full_path.exists():
                    # Создаем родительские директории если нужно
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    # Создаем файл с базовым содержимым
                    self.create_file_with_template(full_path)
                    print(f"Создан файл: {item_path}")
                    self.created_count += 1

    def create_file_with_template(self, file_path):
        """Создает файл с шаблонным содержимым в зависимости от расширения"""
        templates = {
            '.py': "",
            '.sql': '',
            '.yml': '',
            '.yaml': '',
            '.md': '',
            '.txt': '',
            '.ini': '',
            '.cfg': '',
            '.vcl': '',
            '.json': '',
            '.html': '',
            '.css': '',
            '.js': '',
        }

        content = templates.get(file_path.suffix, '')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def run(self, project_dir, tree_file):
        """Основной метод запуска"""
        if not os.path.exists(project_dir):
            print(f"Ошибка: директория проекта '{project_dir}' не существует")
            sys.exit(1)

        if not os.path.exists(tree_file):
            print(f"Ошибка: файл с деревом '{tree_file}' не существует")
            sys.exit(1)

        print("Анализ структуры проекта...")
        target_structure = self.parse_tree_structure(tree_file)

        print(f"Найдено {len(target_structure)} элементов в целевом дереве")
        print("Создание отсутствующих элементов...")

        self.create_missing_items(project_dir, target_structure)

        if self.created_count == 0:
            print("Все файлы и папки уже существуют")
        else:
            print(f"Создано {self.created_count} элементов")


def main():
    if len(sys.argv) != 3:
        print("Использование: python project_tree_update.py <директория_проекта> <файл_с_деревом>")
        print("Пример: python project_tree_update.py ./my_project project_structure.txt")
        sys.exit(1)

    project_dir = sys.argv[1]
    tree_file = sys.argv[2]

    updater = ProjectTreeUpdater()
    updater.run(project_dir, tree_file)


if __name__ == "__main__":
    main()