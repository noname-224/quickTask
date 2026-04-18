from abc import ABC, abstractmethod

from telebot.types import CallbackQuery, Message

from app.bot import bot
from app.keyboards import InlineKeyboardCreator
from database.repositories import UserRepository, TaskRepository
from domain.enums import BotState, TaskAttributeText, TaskStatus
from domain.types import UserId
from utils.helpers import text_for_reply_to_bad_input, get_task_id


class BotStateMachine:
    def __init__(self, user_id, message: Message | None = None, call: CallbackQuery | None = None):
        self.__states: dict[BotState, IState] = {
            BotState.STATE_MANAGER: StateManager(self),
            BotState.STATE_TASK_ADDITION_TITLE_INPUT_REQUEST: StateTaskAdditionTitleInputRequest(self),
            BotState.STATE_TASK_ADDITION_TITLE_INPUT_RESPONSE: StateTaskTitleAdditionInputResponse(self),
            BotState.STATE_TASK_ADDITION_DESCRIPTION_INPUT_REQUEST: StateTaskAdditionDescriptionInputRequest(self),
            BotState.STATE_TASK_ADDITION_DESCRIPTION_INPUT_RESPONSE: StateTaskAdditionDescriptionInputResponse(self),
            BotState.STATE_TASK_ADDITION: StateTaskAddition(self),
            BotState.STATE_TASK_EDITING_TITLE_INPUT_REQUEST: StateTaskEditingTitleInputRequest(self),
            BotState.STATE_TASK_EDITING_TITLE_INPUT_RESPONSE: StateTaskEditingTitleInputResponse(self),
            BotState.STATE_TASK_EDITING_DESCRIPTION_INPUT_REQUEST: StateTaskEditingDescriptionInputRequest(self),
            BotState.STATE_TASK_EDITING_DESCRIPTION_INPUT_RESPONSE: StateTaskEditingDescriptionInputResponse(self),
            BotState.STATE_TASK_EDITION: StateTaskEdition(self),
        }

        self.message = message
        self.call = call
        if message is not None:
            self.call_data = None
        else:
            self.call_data = call.data

        self.task_repo = TaskRepository()
        self.user_repo = UserRepository()

        if self.__is_user_registered(user_id):
            self.__state: IState = self.__states[self.user.state]
        else:
            self.__add_user()
            self.user = self.user_repo.get_user(user_id)
            self.__state: IState = self.__states[self.user.state]

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state: BotState):
        self.__state = self.__states[state]

    def __is_user_registered(self, user_id: UserId) -> bool:
        self.user = self.user_repo.get_user(user_id)
        return self.user is not None

    def __add_user(self):
        self.user_repo.add(
            user_id=self.message.from_user.id,
            username=self.message.from_user.username,
            first_name=self.message.from_user.first_name,
            last_name=self.message.from_user.last_name,
            is_premium=self.message.from_user.is_premium,
        )

    def handle(self):
        self.__state.handle()


class IState(ABC):
    def __init__(self, bsm: BotStateMachine):
        self.bsm = bsm

    @abstractmethod
    def handle(self) -> None:
        ...


class StateManager(IState):

    def handle(self) -> None:
        if self.bsm.call_data is not None:
            if self.bsm.call_data == 'delete_checklist_window':
                bot.delete_message(
                    self.bsm.call.message.chat.id,
                    self.bsm.call.message.id,
                )
            elif self.bsm.call_data == 'add_task_by_clicking':
                self.bsm.state = BotState.STATE_TASK_ADDITION_TITLE_INPUT_REQUEST
                self.bsm.state.handle()
            elif self.bsm.call_data == 'change_window_to_checklist':
                self.update_window_to_checklist()
            elif self.bsm.call_data.startswith('change_window_to_task_edit_'):
                self.update_window_to_task_edit()
            elif self.bsm.call_data.startswith('change_window_to_task_'):
                self.update_window_to_task()
            elif self.bsm.call_data.startswith('delete_task_from_checklist_'):
                self.delete_task()
            elif self.bsm.call_data.startswith('mark_task_completed_'):
                self.mark_task_completed()
            elif self.bsm.call_data.startswith('mark_task_uncompleted_'):
                self.mark_task_uncompleted()
            elif self.bsm.call_data.startswith('edit_task_title_'):
                self.bsm.state = BotState.STATE_TASK_EDITING_TITLE_INPUT_REQUEST
                self.bsm.state.handle()
            elif self.bsm.call_data.startswith('edit_task_description_'):
                self.bsm.state = BotState.STATE_TASK_EDITING_DESCRIPTION_INPUT_REQUEST
                self.bsm.state.handle()
            elif self.bsm.call_data.startswith('edit_task_all_'):
                self.bsm.state = BotState.STATE_TASK_EDITING_TITLE_INPUT_REQUEST
                self.bsm.state.handle()
        else:
            if self.bsm.message.text == '/start':
                self.start()
            elif self.bsm.message.text == '/view_checklist':
                self.send_checklist_window()

    def start(self) -> None:
        bot.send_message(
            chat_id=self.bsm.message.chat.id,
            text=f"Привет {self.bsm.user.first_name}! "
                 f"Я твой персональный ToDo-бот.\n\n"
                 f"Ты можешь управлять мной, посылая эти команды:\n\n"
                 f"/view_checklist – просмотреть список задач\n"
            # f"или отправь название города, "
            # f"а я расскажу про погоду в этом регионе"
        )

    def send_checklist_window(self) -> None:
        tasks = self.bsm.task_repo.get_all(user_id=self.bsm.user.id)
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию" if tasks else "У тебя нет задач!"

        bot.send_message(
            chat_id=self.bsm.message.chat.id,
            text=text,
            reply_markup=InlineKeyboardCreator.create_checklist_window_buttons(tasks)
        )
    def send_task_window(self, task_id):
        task = self.bsm.task_repo.get_one(task_id=task_id)

        if task is not None:
            mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"

            bot.send_message(
                chat_id=self.bsm.message.chat.id,
                text=f"Название: {task.title} {mark}\n\n"
                     f"Описание: {task.description}",
                reply_markup=InlineKeyboardCreator.create_task_window_buttons(task)
            )
        else:
            self.update_window_to_checklist()

    def update_window_to_checklist(self) -> None:
        tasks = self.bsm.task_repo.get_all(user_id=self.bsm.user.id)
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию" if tasks else "У тебя нет задач!"

        bot.edit_message_text(
            chat_id=self.bsm.call.message.chat.id,
            message_id=self.bsm.call.message.message_id,
            text=text,
            reply_markup=InlineKeyboardCreator.create_checklist_window_buttons(tasks)
        )

    def close_checklist_window(self) -> None:
        bot.delete_message(
            chat_id=self.bsm.message.chat.id,
        )

    # def send_task_window(self):
    #     task = self.bsm.task_repo.get_one(task_id)

    def update_window_to_task(self):
        task_id = get_task_id(self.bsm.call_data)
        task = self.bsm.task_repo.get_one(task_id)
        if task is not None:
            mark = "✅" if task.status == TaskStatus.COMPLETED else "❌"

            bot.edit_message_text(
                chat_id=self.bsm.call.message.chat.id,
                message_id=self.bsm.call.message.message_id,
                text=f"Название: {task.title} {mark}\n\n"
                     f"Описание: {task.description}",
                reply_markup=InlineKeyboardCreator.create_task_window_buttons(task)
            )
        else:
            self.update_window_to_checklist()

    def delete_task(self):
        task_id = get_task_id(self.bsm.call_data)
        self.bsm.task_repo.delete(task_id)
        self.update_window_to_checklist()

    def mark_task_completed(self):
        task_id = get_task_id(self.bsm.call_data)
        self.bsm.task_repo.mark_completed(task_id)
        self.update_window_to_task()

    def mark_task_uncompleted(self):
        task_id = get_task_id(self.bsm.call_data)
        self.bsm.task_repo.mark_uncompleted(task_id)
        self.update_window_to_task()

    def update_window_to_task_edit(self):
        task_id = get_task_id(self.bsm.call_data)
        task = self.bsm.task_repo.get_one(task_id)

        if task is not None:
            bot.edit_message_text(
                chat_id=self.bsm.call.message.chat.id,
                message_id=self.bsm.call.message.message_id,
                text=f"Название: {task.title}\n\n"
                     f"Описание: {task.description}",
                reply_markup=InlineKeyboardCreator.create_task_edit_window_buttons(task.id)
            )
        else:
            self.update_window_to_checklist()


class StateTaskAdditionTitleInputRequest(IState):

    def handle(self) -> None:
        bot.send_message(
            chat_id=self.bsm.user.id,
            text="Напишите название задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(1)
        )
        self.bsm.state = BotState.STATE_TASK_ADDITION_TITLE_INPUT_RESPONSE
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_ADDITION_TITLE_INPUT_RESPONSE,
        )


class StateTaskTitleAdditionInputResponse(IState):

    def handle(self) -> None:
        if self.bsm.message is None:
            bot.answer_callback_query(
                callback_query_id=self.bsm.call.id,
                text=f"Сначала завершите добавление")
            return

        if self.bsm.message.content_type != 'text' or self.bsm.message.text.startswith('/'):
            bot.reply_to(
                message=self.bsm.message,
                text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
            )
            return

        title = self.bsm.message.text

        self.bsm.state = BotState.STATE_TASK_ADDITION_DESCRIPTION_INPUT_REQUEST
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_ADDITION_TITLE_INPUT_REQUEST,
            context={"title": f"{title}"}
        )
        self.bsm.state.handle()


class StateTaskAdditionDescriptionInputRequest(IState):

    def handle(self) -> None:
        bot.send_message(
            chat_id=self.bsm.message.chat.id,
            text="Напишите описание задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(1)
        )
        self.bsm.state = BotState.STATE_TASK_ADDITION_DESCRIPTION_INPUT_RESPONSE
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_ADDITION_DESCRIPTION_INPUT_RESPONSE,
        )


class StateTaskAdditionDescriptionInputResponse(IState):

    def handle(self) -> None:
        if self.bsm.message is None:
            bot.answer_callback_query(
                callback_query_id=self.bsm.call.id,
                text=f"Сначала завершите добавление")
            return

        if self.bsm.message.content_type != 'text' or self.bsm.message.text.startswith('/'):
            bot.reply_to(
                message=self.bsm.message,
                text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
            )
            return

        description = self.bsm.message.text

        self.bsm.state = BotState.STATE_TASK_ADDITION
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_ADDITION,
            context={"description": f"{description}"}
        )
        self.bsm.state.handle()


class StateTaskAddition(IState):

    def handle(self) -> None:
        self.bsm.user = self.bsm.user_repo.get_user(user_id=self.bsm.user.id)
        self.bsm.task_repo.add(
            title=self.bsm.user.context["title"],
            description=self.bsm.user.context["description"],
            user_id=self.bsm.user.id,
        )
        self.bsm.user_repo.clear_context(user_id=self.bsm.user.id)

        self.bsm.state = BotState.STATE_MANAGER
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=BotState.STATE_MANAGER,
        )
        StateManager.send_checklist_window(self)


# Запрос на ввод для изменения НАЗВАНИЯ
class StateTaskEditingTitleInputRequest(IState):

    def handle(self) -> None:
        editing_type = self.bsm.call_data.rsplit('_', 1)[0]

        task_id = get_task_id(self.bsm.call_data)
        task = self.bsm.task_repo.get_one(task_id)

        bot.send_message(
            chat_id=self.bsm.call.message.chat.id,
            text=f"Текущее <u><b>название</b></u>: <code>{task.title}</code>\n\n"
                 f"Напишите новое <u><b>название</b></u> задачи",
            parse_mode="HTML",
            reply_markup=InlineKeyboardCreator.create_cancel_editing_button(1)
        )

        state = BotState.STATE_TASK_EDITING_TITLE_INPUT_RESPONSE
        self.bsm.state = state
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=state,
            context={
                "editing_type": editing_type,
                "task_id": task_id,
            }
        )


# ввод нового НАЗВАНИЯ
class StateTaskEditingTitleInputResponse(IState):

    def handle(self) -> None:
        if self.bsm.message is None:
            bot.answer_callback_query(
                callback_query_id=self.bsm.call.id,
                text=f"Сначала завершите изменение")
            return

        if self.bsm.message.content_type != 'text' or self.bsm.message.text.startswith('/'):
            bot.reply_to(
                message=self.bsm.message,
                text=text_for_reply_to_bad_input(TaskAttributeText.TITLE)
            )
            return

        title = self.bsm.message.text
        if self.bsm.user.context['editing_type'] == 'edit_task_title':
            state = BotState.STATE_TASK_EDITION
        else:
            state = BotState.STATE_TASK_EDITING_DESCRIPTION_INPUT_REQUEST

        self.bsm.state = state
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=state,
            context={"title": f"{title}"}
        )

        self.bsm.state.handle()


# Запрос на ввод для изменения ОПИСАНИЯ
class StateTaskEditingDescriptionInputRequest(IState):

    def handle(self) -> None:

        if self.bsm.user.context == {}:
            editing_type = self.bsm.call_data.rsplit('_', 1)[0]
            task_id = get_task_id(self.bsm.call_data)
            self.bsm.user_repo.update_context(
                user_id=self.bsm.user.id,
                context={"editing_type": editing_type, "task_id": task_id},
            )
            task = self.bsm.task_repo.get_one(task_id)

            bot.send_message(
                chat_id=self.bsm.call.message.chat.id,
                text=f"Текущее <u><b>описание</b></u>: <code>{task.description}</code>\n\n"
                     f"Напишите новое <u><b>описание</b></u> задачи",
                parse_mode="HTML",
                reply_markup=InlineKeyboardCreator.create_cancel_editing_button(1)
            )
        else:
            task_id = self.bsm.user.context['task_id']
            task = self.bsm.task_repo.get_one(task_id)

            bot.send_message(
                chat_id=self.bsm.message.chat.id,
                text=f"Текущее <u><b>описание</b></u>: <code>{task.description}</code>\n\n"
                     f"Напишите новое <u><b>описание</b></u> задачи",
                parse_mode="HTML",
                reply_markup=InlineKeyboardCreator.create_cancel_editing_button(1)
            )

        state = BotState.STATE_TASK_EDITING_DESCRIPTION_INPUT_RESPONSE
        self.bsm.state = state
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=state,
        )


# Ввод нового ОПИСАНИЯ
class StateTaskEditingDescriptionInputResponse(IState):

    def handle(self) -> None:
        if self.bsm.message is None:
            bot.answer_callback_query(
                callback_query_id=self.bsm.call.id,
                text=f"Сначала завершите изменение")
            return

        if self.bsm.message.content_type != 'text' or self.bsm.message.text.startswith('/'):
            bot.reply_to(
                message=self.bsm.message,
                text=text_for_reply_to_bad_input(TaskAttributeText.DESCRIPTION)
            )
            return

        description = self.bsm.message.text

        state = BotState.STATE_TASK_EDITION
        self.bsm.state = state
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=state,
            context={"description": f"{description}"}
        )

        self.bsm.state.handle()


# Сохранение изменений в базу
class StateTaskEdition(IState):

    def handle(self) -> None:
        self.bsm.user = self.bsm.user_repo.get_user(user_id=self.bsm.user.id)
        task_id = self.bsm.user.context['task_id']
        if self.bsm.user.context['editing_type'] == 'edit_task_title':
            title = self.bsm.user.context['title']
            description = None
        elif self.bsm.user.context['editing_type'] == 'edit_task_description':
            title = None
            description = self.bsm.user.context['description']
        else:
            title = self.bsm.user.context['title']
            description = self.bsm.user.context['description']


        self.bsm.task_repo.edit(
            task_id=task_id,
            title=title,
            description=description,
        )

        StateManager.send_task_window(self, task_id)
        self.bsm.user_repo.clear_context(user_id=self.bsm.user.id)
        state = BotState.STATE_MANAGER
        self.bsm.state = state
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=state,
        )
