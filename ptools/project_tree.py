#!/usr/bin/env python3
import os
import sys
from pathlib import Path

class ProjectTreeGenerator:
    def __init__(self):
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            'venv', '.venv', '.idea', '.vscode', '.mypy_cache'
        }

    def should_include(self, item):
        """Определяем, нужно ли включать файл/папку в вывод"""
        if item.name in self.exclude_dirs:
            return False
        # Включаем только определенные скрытые файлы
        allowed_hidden = ['.env.example', '.gitlab-ci.yml', '.dockerignore', '.env']
        if item.name.startswith('.') and item.name not in allowed_hidden:
            return False
        return True

    def generate_tree(self, directory, prefix="", is_last=True, is_root=True):
        path = Path(directory)

        # Получаем и фильтруем элементы
        items = []
        for item in path.iterdir():
            if self.should_include(item):
                items.append(item)

        # Сортируем: сначала директории, потом файлы, всё по алфавиту
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))

        # Обрабатываем элементы
        for index, item in enumerate(items):
            is_last_item = index == len(items) - 1

            # Определяем символы для текущего элемента
            if is_root:
                # Для корневого уровня
                if item.is_file():
                    print(f"{'├── ' if index < len(items) - 1 else '└── '}{item.name}")
                else:
                    print(f"{'├── ' if index < len(items) - 1 else '└── '}{item.name}/")
            else:
                # Для вложенных уровней
                if item.is_file():
                    print(f"{prefix}{'└── ' if is_last_item else '├── '}{item.name}")
                else:
                    print(f"{prefix}{'└── ' if is_last_item else '├── '}{item.name}/")

            # Рекурсивно обрабатываем поддиректории
            if item.is_dir():
                # Формируем префикс для следующего уровня
                if is_root:
                    next_prefix = "│   " if index < len(items) - 1 else "    "
                else:
                    if is_last_item:
                        next_prefix = prefix + "    "
                    else:
                        next_prefix = prefix + "│   "

                self.generate_tree(item, next_prefix, is_last_item, is_root=False)

    def run(self, target_dir):
        if not os.path.exists(target_dir):
            print(f"Ошибка: директория '{target_dir}' не существует")
            sys.exit(1)

        target_path = Path(target_dir)

        # Выводим название корневой директории
        if target_dir == ".":
            root_name = Path.cwd().name
        else:
            root_name = target_path.name

        print(f"{root_name}/")
        self.generate_tree(target_dir)

def main():
    generator = ProjectTreeGenerator()

    # Используем текущую директорию, если не указана другая
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    generator.run(target_dir)

if __name__ == "__main__":
    main()

