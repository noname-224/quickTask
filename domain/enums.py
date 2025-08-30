from enum import Enum, StrEnum


class TaskAttributeText(StrEnum):
    TITLE = "названия"
    DESCRIPTION = "описания"

class CancelledOperationName(StrEnum):
    ADDITION = "Добавление"
    EDITING = "Редактирование"


class MessageUploadMethod(Enum):
    SEND = True
    UPDATE = False


class TaskStatus(StrEnum):
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"