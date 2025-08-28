from abc import ABC, abstractmethod

from telebot.types import CallbackQuery, Message

from app.bot import bot
from app.keyboards import InlineKeyboardCreator
from database.repositories import UserRepository, TaskRepository
from domain.enums import BotState, TaskAttributeText
from domain.types import UserId
from utils.helpers import text_for_reply_to_bad_input


class BotStateMachine:
    def __init__(self, user_id, message: Message | None = None, call: CallbackQuery | None = None):
        self.__states: dict[BotState, IState] = {
            BotState.STATE_MANAGER: StateManager(self),
            BotState.STATE_TASK_TITLE_INPUT_REQUEST: StateTaskTitleInputRequest(self),
            BotState.STATE_TASK_TITLE_INPUT_RESPONSE: StateTaskTitleInputResponse(self),
            BotState.STATE_TASK_DESCRIPTION_INPUT_REQUEST: StateTaskDescriptionInputRequest(self),
            BotState.STATE_TASK_DESCRIPTION_INPUT_RESPONSE: StateTaskDescriptionInputResponse(self),
            BotState.STATE_TASK_ADDITION: StateTaskAddition(self),
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
            if self.bsm.call_data == 'add_task_by_clicking':
                self.bsm.state = BotState.STATE_TASK_TITLE_INPUT_REQUEST
                self.bsm.state.handle()
            if self.bsm.call_data == 'delete_checklist_window':
                bot.delete_message(
                    self.bsm.call.message.chat.id,
                    self.bsm.call.message.id,
                )
        else:
            if self.bsm.message.text == '/start':
                self.start()
            elif self.bsm.message.text == '/view_checklist':
                self.view_checklist()

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

    def view_checklist(self) -> None:
        tasks = self.bsm.task_repo.get_all(user_id=self.bsm.user.id)
        text = "Вот твои задачи.\nНажми чтобы перейти к описанию" if tasks else "У тебя нет задач!"

        bot.send_message(
            chat_id=self.bsm.message.chat.id,
            text=text,
            reply_markup=InlineKeyboardCreator.create_checklist_window_buttons(tasks)
        )

    def close_checklist(self) -> None:
        bot.delete_message(
            chat_id=self.bsm.message.chat.id,
        )


class StateTaskTitleInputRequest(IState):

    def handle(self) -> None:
        bot.send_message(
            chat_id=self.bsm.user.id,
            text="Напишите название задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(1)
        )
        self.bsm.state = BotState.STATE_TASK_TITLE_INPUT_RESPONSE
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_TITLE_INPUT_RESPONSE,
        )


class StateTaskTitleInputResponse(IState):

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

        self.bsm.state = BotState.STATE_TASK_DESCRIPTION_INPUT_REQUEST
        self.bsm.user_repo.update_state_and_context(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_TITLE_INPUT_REQUEST,
            context={"title": f"{title}"}
        )
        self.bsm.state.handle()


class StateTaskDescriptionInputRequest(IState):

    def handle(self) -> None:
        bot.send_message(
            chat_id=self.bsm.message.chat.id,
            text="Напишите описание задачи",
            reply_markup=InlineKeyboardCreator.create_cancel_adding_button(1)
        )
        self.bsm.state = BotState.STATE_TASK_DESCRIPTION_INPUT_RESPONSE
        self.bsm.user_repo.update_state(
            user_id=self.bsm.user.id,
            state=BotState.STATE_TASK_DESCRIPTION_INPUT_RESPONSE,
        )


class StateTaskDescriptionInputResponse(IState):

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
        StateManager.view_checklist(self)