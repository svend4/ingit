#!/usr/bin/env python3
"""
InGit Report Generator
Генерация отчетов на основе YAML-метаданных
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

class ReportGenerator:
    """Генератор отчетов для InGit проектов"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.tasks = []
        self.finances = []
        self.project_info = {}

    def load_project(self) -> None:
        """Загрузить данные проекта"""
        # Загрузить информацию о проекте
        project_file = self.project_path / "10_profile" / "project.yaml"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                self.project_info = yaml.safe_load(f)

        # Загрузить задачи
        tasks_dir = self.project_path / "70_tasks"
        for task_file in tasks_dir.rglob("*.yaml"):
            with open(task_file, 'r', encoding='utf-8') as f:
                task = yaml.safe_load(f)
                task['_file'] = task_file
                self.tasks.append(task)

        # Загрузить финансы
        finance_dir = self.project_path / "40_finance"
        if finance_dir.exists():
            for finance_file in finance_dir.rglob("*.yaml"):
                with open(finance_file, 'r', encoding='utf-8') as f:
                    record = yaml.safe_load(f)
                    record['_file'] = finance_file
                    self.finances.append(record)

    def generate_summary(self) -> str:
        """Генерация краткой сводки проекта"""
        output = []
        output.append("# 📊 Сводка проекта\n")

        # Информация о проекте
        if self.project_info:
            output.append(f"## Проект: {self.project_info.get('name', 'N/A')}\n")
            output.append(f"**Статус:** {self.project_info.get('status', 'N/A')}")
            output.append(f"**Начало:** {self.project_info.get('start_date', 'N/A')}")
            output.append(f"**Целевой релиз:** {self.project_info.get('target_release', 'N/A')}\n")

        # Статистика по задачам
        output.append("## 📋 Задачи\n")
        task_stats = defaultdict(int)
        for task in self.tasks:
            status = task.get('status', 'unknown')
            task_stats[status] += 1

        output.append(f"- Всего задач: {len(self.tasks)}")
        for status, count in sorted(task_stats.items()):
            emoji = {'backlog': '📦', 'in_progress': '🔄', 'done': '✅', 'cancelled': '❌'}.get(status, '📌')
            output.append(f"- {emoji} {status}: {count}")

        # Часы работы
        total_estimated = sum(task.get('estimated_hours', 0) for task in self.tasks)
        total_actual = sum(task.get('actual_hours', 0) for task in self.tasks)
        output.append(f"\n**Оценочное время:** {total_estimated}ч")
        output.append(f"**Фактическое время:** {total_actual}ч")
        if total_estimated > 0:
            progress = (total_actual / total_estimated) * 100
            output.append(f"**Прогресс:** {progress:.1f}%\n")

        # Финансы
        if self.finances:
            output.append("## 💰 Финансы\n")
            total_income = sum(f.get('amount', 0) for f in self.finances if f.get('type') == 'income')
            total_expenses = sum(abs(f.get('amount', 0)) for f in self.finances if f.get('type') == 'expense')

            output.append(f"**Доходы:** {total_income:,.2f} RUB")
            output.append(f"**Расходы:** {total_expenses:,.2f} RUB")
            output.append(f"**Прибыль:** {total_income - total_expenses:,.2f} RUB\n")

            # Бюджет проекта
            if 'budget' in self.project_info:
                budget = self.project_info['budget']
                remaining = budget - total_expenses
                output.append(f"**Бюджет проекта:** {budget:,.2f} RUB")
                output.append(f"**Остаток бюджета:** {remaining:,.2f} RUB")
                output.append(f"**Использовано:** {(total_expenses/budget)*100:.1f}%\n")

        return "\n".join(output)

    def generate_task_report(self) -> str:
        """Детальный отчет по задачам"""
        output = []
        output.append("# 📋 Отчет по задачам\n")

        # Группировка по статусам
        by_status = defaultdict(list)
        for task in self.tasks:
            status = task.get('status', 'unknown')
            by_status[status].append(task)

        for status in ['in_progress', 'backlog', 'done', 'cancelled']:
            tasks = by_status.get(status, [])
            if not tasks:
                continue

            emoji = {'backlog': '📦', 'in_progress': '🔄', 'done': '✅', 'cancelled': '❌'}.get(status, '📌')
            output.append(f"## {emoji} {status.upper()} ({len(tasks)})\n")

            for task in sorted(tasks, key=lambda t: t.get('priority', 'low'), reverse=True):
                number = task.get('number', '?')
                title = task.get('title', 'Untitled')
                priority = task.get('priority', 'medium')
                assignee = task.get('assignee', 'Unassigned')

                priority_emoji = {'low': '🔵', 'medium': '🟡', 'high': '🔴', 'urgent': '🚨'}.get(priority, '⚪')

                output.append(f"### #{number}: {title}")
                output.append(f"- {priority_emoji} **Приоритет:** {priority}")
                output.append(f"- 👤 **Исполнитель:** {assignee}")

                if 'estimated_hours' in task:
                    est = task['estimated_hours']
                    act = task.get('actual_hours', 0)
                    output.append(f"- ⏱️ **Часы:** {act}/{est}ч")

                if 'due_date' in task:
                    output.append(f"- 📅 **Срок:** {task['due_date']}")

                labels = task.get('labels', [])
                if labels:
                    output.append(f"- 🏷️ **Метки:** {', '.join(labels)}")

                output.append("")

        return "\n".join(output)

    def generate_weekly_report(self, days: int = 7) -> str:
        """Отчет за последние N дней"""
        output = []
        cutoff_date = datetime.now() - timedelta(days=days)

        output.append(f"# 📅 Отчет за последние {days} дней\n")
        output.append(f"**Период:** {cutoff_date.strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}\n")

        # Завершенные задачи
        completed_tasks = [
            t for t in self.tasks
            if t.get('status') == 'done' and 'completed_at' in t
        ]

        output.append(f"## ✅ Завершено задач: {len(completed_tasks)}\n")
        for task in completed_tasks:
            output.append(f"- #{task.get('number')}: {task.get('title')}")

        # Добавленные задачи
        new_tasks = [
            t for t in self.tasks
            if 'created_at' in t
        ]

        if new_tasks:
            output.append(f"\n## 📝 Новые задачи: {len(new_tasks)}\n")
            for task in new_tasks[-5:]:  # Последние 5
                output.append(f"- #{task.get('number')}: {task.get('title')}")

        # Финансы за период
        recent_finances = [
            f for f in self.finances
            if 'date' in f
        ]

        if recent_finances:
            output.append(f"\n## 💰 Финансы за период\n")
            income = sum(f.get('amount', 0) for f in recent_finances if f.get('type') == 'income')
            expenses = sum(abs(f.get('amount', 0)) for f in recent_finances if f.get('type') == 'expense')
            output.append(f"- Доходы: {income:,.2f} RUB")
            output.append(f"- Расходы: {expenses:,.2f} RUB")
            output.append(f"- Чистая прибыль: {income - expenses:,.2f} RUB")

        return "\n".join(output)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: generate-report.py <project_path> [report_type]")
        print("\nReport types:")
        print("  summary  - краткая сводка (по умолчанию)")
        print("  tasks    - детальный отчет по задачам")
        print("  weekly   - отчет за последнюю неделю")
        sys.exit(1)

    project_path = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else "summary"

    generator = ReportGenerator(project_path)
    generator.load_project()

    if report_type == "summary":
        print(generator.generate_summary())
    elif report_type == "tasks":
        print(generator.generate_task_report())
    elif report_type == "weekly":
        print(generator.generate_weekly_report())
    else:
        print(f"Unknown report type: {report_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()
