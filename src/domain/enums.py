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


class BotState(Enum):
    STATE_MANAGER = 0
    STATE_TASK_TITLE_INPUT_REQUEST = 1
    STATE_TASK_TITLE_INPUT_RESPONSE = 2
    STATE_TASK_DESCRIPTION_INPUT_REQUEST = 3
    STATE_TASK_DESCRIPTION_INPUT_RESPONSE = 4
    STATE_TASK_ADDITION = 5
