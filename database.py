import sqlite3


# Путь к файлу базы данных
DB_PATH = "todobot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            deadline INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'uncompleted',
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


def add_new_task(title, description, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, description, user_id) 
        VALUES (?, ?, ?)""", (
        title, description, user_id)
    )

    conn.commit()
    conn.close()


def get_current_tasks(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, status FROM tasks 
        WHERE user_id = ? ORDER BY status DESC, id""",
        (user_id,)
    )
    cur_tasks = cursor.fetchall()

    conn.close()
    return cur_tasks

def get_task_by_id(task_id):
    """Получить статус задачи по ее ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, status FROM tasks
        WHERE id = ?""",(task_id,)
    )
    task_data = cursor.fetchone()

    conn.commit()
    conn.close()
    return task_data


def get_task_by_index(user_id, task_index):
    """Получить task(id, title, description)
    по порядковому номеру для пользователя."""
    tasks = get_current_tasks(user_id)

    if task_index < 1 or task_index > len(tasks):
        return None
    return tasks[task_index - 1]


def mark_task_completed(task_id):
    """Отметить задачу как выполненную."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks SET status = 'completed' WHERE id = ? """,
        (task_id,)
    )

    conn.commit()
    conn.close()

def mark_task_uncompleted(task_id):
    """Отметить задачу как не завершенную."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks SET status = 'uncompleted' WHERE id = ? """,
        (task_id,)
    )

    conn.commit()
    conn.close()


def delete_task(task_id):
    """Удалить задачу по её ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks WHERE id = ?""", (task_id,)
    )

    conn.commit()
    conn.close()


def edit_task(task_id, title=None, description=None):
    """Редактировать задачу (название и/или описание)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if title and description:
        cursor.execute("""
            UPDATE tasks SET title = ?, description = ? WHERE id = ?""",
            (title, description, task_id)
        )
    elif title:
        cursor.execute("""
            UPDATE tasks SET title = ? WHERE id = ?""",
            (title, task_id)
        )
    elif description:
        cursor.execute("""
            UPDATE tasks SET description = ? WHERE id = ?""",
            (description, task_id)
        )

    conn.commit()
    conn.close()




# -----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()