import sys
import psycopg2
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget,
    QMessageBox, QComboBox
)
from PySide6.QtGui import QIcon

class TaskManager:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        self.connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="",
            host="localhost",
            port="5432"
        )
        self.cursor = self.connection.cursor()

    def add_task(self, description, priority):
        self.cursor.execute(
            "INSERT INTO tasks (description, priority) VALUES (%s, %s)",
            (description, priority)
        )
        self.connection.commit()

    def remove_task(self, task_id):
        self.cursor.execute(
            "DELETE FROM tasks WHERE id = %s",
            (task_id,)
        )
        self.connection.commit()

    def mark_task_completed(self, task_id, completed=True):
        self.cursor.execute(
            "UPDATE tasks SET completed = %s WHERE id = %s",
            (completed, task_id)
        )
        self.connection.commit()

    def get_tasks(self, completed=None):
        query = "SELECT * FROM tasks"
        if completed is not None:
            query += " WHERE completed = %s"
            self.cursor.execute(query, (completed,))
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()


class TaskApp(QWidget):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Список дел")
        self.setGeometry(100, 100, 400, 300)

        # Установка иконки
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Введите описание задачи")
        layout.addWidget(self.task_input)

        self.priority_combo = QComboBox(self)
        self.priority_combo.addItems(['высокий', 'средний', 'низкий'])
        layout.addWidget(self.priority_combo)

        self.add_button = QPushButton("Добавить задачу", self)
        self.add_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_button)

        self.task_list = QListWidget(self)
        layout.addWidget(self.task_list)

        self.remove_button = QPushButton("Удалить задачу", self)
        self.remove_button.clicked.connect(self.remove_task)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)
        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        tasks = self.task_manager.get_tasks()
        for task in tasks:
            status = "✓" if task[3] else "✗"
            self.task_list.addItem(f"{task[0]}: {task[1]} [{task[2]}] {status}")

    def add_task(self):
        description = self.task_input.text()
        priority = self.priority_combo.currentText()
        if description:
            self.task_manager.add_task(description, priority)
            self.load_tasks()
            self.task_input.clear()
        else:
            QMessageBox.warning(self, "Ошибка", "Введите описание задачи.")

    def remove_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = int(selected_item.text().split(":")[0])
            self.task_manager.remove_task(task_id)
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления.")

    def closeEvent(self, event):
        self.task_manager.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    task_manager = TaskManager(db_name='your_db', user='your_user', password='your_password')
    window = TaskApp(task_manager)
    window.show()
    sys.exit(app.exec())