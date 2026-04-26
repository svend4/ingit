"""
InGit CLI - Command Line Interface
Main entry point for CLI commands
"""

import click
import sys
from pathlib import Path

from ingit import __version__


@click.group()
@click.version_option(version=__version__, prog_name="ingit")
@click.pass_context
def cli(ctx):
    """
    InGit - Integrated Git Platform

    Offline-first система управления версиями, проектами и документацией
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument('path', type=click.Path(), default='.')
def init(path):
    """Инициализировать новый InGit проект"""
    project_path = Path(path)

    click.echo(f"🚀 Инициализация InGit проекта в {project_path.absolute()}")

    # Создаем структуру папок
    folders = [
        "00_inbox",
        "10_profile",
        "20_timeline",
        "30_documents/contracts",
        "30_documents/specs",
        "40_finance/expenses",
        "40_finance/income",
        "50_projects",
        "60_configs",
        "70_tasks/backlog",
        "70_tasks/in-progress",
        "70_tasks/done",
        "80_wiki",
        "90_exports",
        ".ingit/hooks",
    ]

    for folder in folders:
        folder_path = project_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✓ Создана папка: {folder}")

    # Создаем базовые файлы
    profile_yaml = project_path / "10_profile" / "project.yaml"
    if not profile_yaml.exists():
        profile_yaml.write_text("""type: project
name: "Мой проект InGit"
slug: my-ingit-project
description: |
  Описание проекта

status: active
visibility: private

# Команда
owner:
  type: user
  name: "Ваше имя"
  email: "your.email@example.com"

# Технологии
technologies:
  - Python
  - JavaScript

created_at: {}
""".format("2026-02-01T12:00:00Z"))
        click.echo(f"  ✓ Создан файл: 10_profile/project.yaml")

    # Создаем README
    readme = project_path / "README.md"
    if not readme.exists():
        readme.write_text("""# InGit Project

Этот проект использует InGit для управления версиями и документацией.

## Структура

- `00_inbox/` - временные файлы
- `10_profile/` - информация о проекте
- `20_timeline/` - журнал событий
- `30_documents/` - документация
- `40_finance/` - финансы
- `50_projects/` - исходный код
- `70_tasks/` - задачи
- `80_wiki/` - база знаний

## Использование

```bash
# Создать задачу
ingit task create "Название задачи"

# Посмотреть список задач
ingit task list

# Сгенерировать отчет
ingit report summary
```
""")
        click.echo(f"  ✓ Создан файл: README.md")

    # Инициализируем git если нужно
    git_dir = project_path / ".git"
    if not git_dir.exists():
        import subprocess
        try:
            subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
            click.echo("  ✓ Инициализирован Git репозиторий")
        except:
            click.echo("  ⚠ Git не найден, пропускаем инициализацию", err=True)

    click.echo("\n✅ InGit проект успешно инициализирован!")
    click.echo(f"\nПерейдите в директорию: cd {project_path}")
    click.echo("Начните работу с: ingit task create 'Первая задача'")


@cli.group()
def task():
    """Управление задачами"""
    pass


@task.command('create')
@click.argument('title')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), default='medium')
@click.option('--type', '-t', type=click.Choice(['task', 'bug', 'feature']), default='task')
@click.option('--assignee', '-a', help='Исполнитель задачи')
def task_create(title, priority, type, assignee):
    """Создать новую задачу"""
    import yaml
    from datetime import datetime

    # Найти следующий номер задачи
    tasks_dir = Path("70_tasks/backlog")
    if not tasks_dir.exists():
        click.echo("❌ Не найдена директория задач. Выполните 'ingit init' сначала.", err=True)
        sys.exit(1)

    existing_tasks = list(Path("70_tasks").rglob("task-*.yaml"))
    task_numbers = [int(t.stem.split('-')[1]) for t in existing_tasks if t.stem.startswith('task-')]
    next_number = max(task_numbers, default=-1) + 1

    task_file = tasks_dir / f"task-{next_number:03d}.yaml"

    task_data = {
        'type': type,
        'title': title,
        'description': '',
        'status': 'backlog',
        'priority': priority,
        'assignee': assignee or 'unassigned',
        'estimated_hours': 0,
        'labels': [],
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }

    with open(task_file, 'w') as f:
        yaml.dump(task_data, f, allow_unicode=True, default_flow_style=False)

    click.echo(f"✅ Задача #{next_number} создана: {task_file}")
    click.echo(f"   Название: {title}")
    click.echo(f"   Приоритет: {priority}")
    click.echo(f"   Тип: {type}")


@task.command('list')
@click.option('--status', '-s', help='Фильтр по статусу')
@click.option('--priority', '-p', help='Фильтр по приоритету')
def task_list(status, priority):
    """Показать список задач"""
    import yaml

    tasks_dir = Path("70_tasks")
    if not tasks_dir.exists():
        click.echo("❌ Не найдена директория задач", err=True)
        sys.exit(1)

    tasks = []
    for task_file in tasks_dir.rglob("task-*.yaml"):
        with open(task_file) as f:
            task_data = yaml.safe_load(f)
            task_data['file'] = task_file
            task_data['number'] = task_file.stem.split('-')[1]
            tasks.append(task_data)

    # Фильтрация
    if status:
        tasks = [t for t in tasks if t.get('status') == status]
    if priority:
        tasks = [t for t in tasks if t.get('priority') == priority]

    if not tasks:
        click.echo("📋 Задач не найдено")
        return

    # Группировка по статусу
    from collections import defaultdict
    by_status = defaultdict(list)
    for task in tasks:
        by_status[task.get('status', 'unknown')].append(task)

    click.echo("\n📋 Задачи InGit:\n")

    status_emoji = {
        'backlog': '📝',
        'in_progress': '🔄',
        'done': '✅',
        'cancelled': '❌'
    }

    priority_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴',
        'urgent': '🔥'
    }

    for status_name, status_tasks in by_status.items():
        emoji = status_emoji.get(status_name, '📌')
        click.echo(f"{emoji} {status_name.upper()} ({len(status_tasks)}):")

        for task in sorted(status_tasks, key=lambda t: t.get('number', '000')):
            num = task.get('number', '?')
            title = task.get('title', 'Без названия')
            priority_str = task.get('priority', 'medium')
            p_emoji = priority_emoji.get(priority_str, '⚪')
            assignee = task.get('assignee', 'unassigned')

            click.echo(f"  {p_emoji} #{num}: {title} (@{assignee})")

        click.echo()


@cli.group()
def report():
    """Генерация отчетов"""
    pass


@report.command('summary')
@click.argument('path', type=click.Path(exists=True), default='.')
def report_summary(path):
    """Сводка по проекту"""
    import subprocess

    script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "generate-report.py"

    if not script_path.exists():
        click.echo("❌ Скрипт генерации отчетов не найден", err=True)
        sys.exit(1)

    try:
        result = subprocess.run(
            ["python", str(script_path), path, "summary"],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при генерации отчета: {e.stderr}", err=True)
        sys.exit(1)


@report.command('weekly')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--days', '-d', type=int, default=7, help='Количество дней')
def report_weekly(path, days):
    """Еженедельный отчет"""
    import subprocess

    script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "generate-report.py"

    try:
        result = subprocess.run(
            ["python", str(script_path), path, "weekly"],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка: {e.stderr}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Показать версию InGit"""
    click.echo(f"InGit v{__version__}")
    click.echo("Offline-first система управления проектами")


@cli.command()
def doctor():
    """Проверить конфигурацию системы"""
    click.echo("🔍 Проверка конфигурации InGit...\n")

    checks = []

    # Проверка Python
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python", python_version, sys.version_info >= (3, 9)))

    # Проверка Git
    import subprocess
    try:
        git_version = subprocess.check_output(["git", "--version"], text=True).strip()
        checks.append(("Git", git_version.split()[-1], True))
    except:
        checks.append(("Git", "не установлен", False))

    # Проверка структуры проекта
    required_dirs = ["70_tasks", "10_profile"]
    all_exist = all(Path(d).exists() for d in required_dirs)
    checks.append(("Структура проекта", "найдена" if all_exist else "не найдена", all_exist))

    # Вывод результатов
    for name, value, status in checks:
        emoji = "✅" if status else "❌"
        click.echo(f"{emoji} {name}: {value}")

    all_ok = all(status for _, _, status in checks)

    if all_ok:
        click.echo("\n✅ Все проверки пройдены!")
    else:
        click.echo("\n⚠️  Обнаружены проблемы. Проверьте конфигурацию.")
        sys.exit(1)


if __name__ == '__main__':
    cli()
