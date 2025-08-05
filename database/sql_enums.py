from enum import Enum


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"