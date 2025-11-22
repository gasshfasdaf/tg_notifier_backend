#!/usr/bin/env python3
import os
import sys
from pathlib import Path


class CodeFileAnalyzer:
    def __init__(self):
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            'venv', '.venv', '.idea', '.vscode', '.mypy_cache'
        }
        self.exclude_files = {
            '.DS_Store', 'Thumbs.db', '.gitkeep', '.gitignore'
        }

    def is_file_with_content(self, file_path):
        """Проверяет, содержит ли файл полезный контент (не только комментарии/пустые строки)"""
        try:
            if not file_path.is_file():
                return False

            # Проверяем размер файла
            if file_path.stat().st_size == 0:
                return False

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Удаляем пустые строки и строки только с пробелами
            non_empty_lines = [line for line in lines if line.strip()]

            if not non_empty_lines:
                return False

            # Для разных типов файлов применяем разные стратегии проверки
            return self.has_meaningful_content(file_path, non_empty_lines)

        except (UnicodeDecodeError, PermissionError, OSError):
            # Пропускаем бинарные файлы и файлы без доступа
            return False

    def has_meaningful_content(self, file_path, lines):
        """Проверяет есть ли в файле нетривиальный контент"""
        extension = file_path.suffix.lower()

        if extension in ['.py', '.js', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.rb']:
            return self.has_code(lines)
        elif extension in ['.html', '.xml', '.xhtml']:
            return self.has_html_content(lines)
        elif extension in ['.css', '.scss', '.less']:
            return self.has_css_content(lines)
        elif extension in ['.json']:
            return self.has_json_content(lines)
        elif extension in ['.yml', '.yaml']:
            return self.has_yaml_content(lines)
        elif extension in ['.md', '.txt', '.rst']:
            return self.has_text_content(lines)
        elif extension in ['.sql']:
            return self.has_sql_content(lines)
        else:
            # Для остальных файлов считаем что есть контент если есть непустые строки
            return len(lines) > 0

    def has_code(self, lines):
        """Проверяет наличие кода (не только комментариев)"""
        code_lines = 0
        total_lines = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            total_lines += 1
            # Считаем строкой кода если это не чистый комментарий
            if not (line.startswith('#') or line.startswith('//') or
                    line.startswith('/*') or line.startswith('*') or
                    line.endswith('*/')):
                code_lines += 1

        # Считаем что файл с кодом если хотя бы 30% строк - не комментарии
        return code_lines > 0 and (code_lines / total_lines) > 0.3

    def has_html_content(self, lines):
        """Проверяет наличие HTML контента (не только теги)"""
        content_found = False
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<!--') and not line.endswith('-->'):
                # Проверяем есть ли текст вне тегов
                clean_line = re.sub(r'<[^>]+>', '', line)
                if clean_line.strip():
                    content_found = True
                    break
        return content_found

    def has_css_content(self, lines):
        """Проверяет наличие CSS правил (не только комментарии)"""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('/*') and not line.startswith('*') and not line.endswith('*/'):
                if ':' in line and '{' not in line and '}' not in line:
                    return True
        return False

    def has_json_content(self, lines):
        """Проверяет валидный JSON контент"""
        content = ''.join(lines)
        try:
            import json
            json.loads(content)
            return True
        except:
            return False

    def has_yaml_content(self, lines):
        """Проверяет наличие YAML контента"""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if ':' in line:
                    return True
        return False

    def has_text_content(self, lines):
        """Проверяет наличие текстового контента"""
        return len([line for line in lines if line.strip() and not line.strip().startswith('#')]) > 0

    def has_sql_content(self, lines):
        """Проверяет наличие SQL команд (не только комментарии)"""
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
                        'FROM', 'WHERE', 'JOIN', 'TABLE', 'DATABASE']
        for line in lines:
            line = line.upper().strip()
            if line and not line.startswith('--'):
                for keyword in sql_keywords:
                    if keyword in line:
                        return True
        return False

    def scan_project(self, project_dir):
        """Сканирует проект и возвращает список файлов с контентом"""
        project_path = Path(project_dir)
        files_with_content = []

        for item in project_path.rglob('*'):
            if item.is_file():
                # Пропускаем исключенные файлы и директории
                if any(excluded in item.parts for excluded in self.exclude_dirs):
                    continue
                if item.name in self.exclude_files:
                    continue

                if self.is_file_with_content(item):
                    # Сохраняем относительный путь от project_dir
                    rel_path = item.relative_to(project_path)
                    files_with_content.append(str(rel_path))

        return sorted(files_with_content)

    def run(self, project_dir):
        """Основной метод запуска"""
        if not os.path.exists(project_dir):
            print(f"Ошибка: директория проекта '{project_dir}' не существует")
            sys.exit(1)

        print(f"Сканирование проекта: {project_dir}")
        files = self.scan_project(project_dir)

        print(f"\nНайдено файлов с контентом: {len(files)}\n")

        for file_path in files:
            print(file_path)


def main():
    if len(sys.argv) != 2:
        print("Использование: python code_file_analyzer.py <директория_проекта>")
        print("Пример: python code_file_analyzer.py ./my_project")
        sys.exit(1)

    project_dir = sys.argv[1]

    analyzer = CodeFileAnalyzer()
    analyzer.run(project_dir)


if __name__ == "__main__":
    import re  # Добавляем импорт для regex

    main()