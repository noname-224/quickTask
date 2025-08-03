from sqlalchemy import select
from sqlalchemy.orm import Session

from database.init_db import Task, Message, engine


# ---------- Task
def add_new_task(title, description, user_id):
    with Session(engine) as session:
        task = Task(
            title=title,
            description=description,
            user_id=user_id
        )

        session.add(task)
        session.commit()


def get_current_tasks(user_id):
    with Session(engine) as session:
        stmt = select(Task).where(Task.user_id == user_id)
        tasks = session.scalars(stmt).fetchall()
        return tasks


def get_task_by_id(task_id):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        return task


def mark_task_completed(task_id):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = "completed"
        session.commit()


def mark_task_uncompleted(task_id):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.status = "uncompleted"
        session.commit()


def delete_task(task_id):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        session.delete(task)
        session.commit()


def edit_task(task_id, title=None, description=None):
    with Session(engine) as session:
        if title and description:
            task = session.get(Task, task_id)
            task.title, task.description = title, description
        elif title:
            task = session.get(Task, task_id)
            task.title = title
        elif description:
            task = session.get(Task, task_id)
            task.description = description

        session.commit()


# ---------- Message
def add_message(msg_id, msg_name):
    with Session(engine) as session:
        message = Message(id=msg_id, name=msg_name)
        session.add(message)
        session.commit()


def del_message(msg_id):
    with Session(engine) as session:
        if message := session.get(Message, msg_id):
            session.delete(message)
            session.commit()


def get_message(msg_name) -> Message | None:
    with Session(engine) as session:
        stmt = select(Message).where(Message.name == msg_name)
        message = session.scalars(stmt).first()
        return message
