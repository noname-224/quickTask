from typing import Optional

from domain.enums import TaskAttributeText
# from domain.exceptions import UserNotFound
from domain.types import TaskId, MessageId

# CONSTS
# ALL_MESSAGE_TYPES = [
#     'text', 'photo', 'video', 'audio', 'document', 'sticker','animation',
#     'voice', 'video_note', 'contact', 'location','venue', 'poll', 'dice',
#     'game', 'invoice','successful_payment', 'passport_data', 'chat_member',
#     'chat_join_request'
# ]


# ToDo прикольное решение моей проблемы
# Функция для экранирования специальных символов в MarkdownV2
def escape_markdown_v2(text: str) -> str:
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def text_for_reply_to_bad_input(attribute: TaskAttributeText) -> str:
    return (f"Пожалуйста, "
            f"отправьте текстовое сообщение для {attribute} задачи! "
            f"(без специальных символов)")


class GetIdFromCallData:

    @staticmethod
    def task_id(call_data: Optional[str]) -> TaskId:
        return int(call_data.split("_")[-1])

    @staticmethod
    def message_id(call_data: Optional[str]) -> MessageId:
        return int(call_data.split("_")[-1])