from domain.enums import TaskAttributeText
from domain.types import TaskId, MessageId


def text_for_reply_to_bad_input(attribute: TaskAttributeText) -> str:
    return (f"Пожалуйста, "
            f"отправьте текстовое сообщение для {attribute} задачи! "
            f"(без специальных символов)")


def get_task_id(call_data: str | None) -> TaskId:
    return int(call_data.split("_")[-1])

def get_message_id(call_data: str | None) -> MessageId:
    return int(call_data.split("_")[-1])