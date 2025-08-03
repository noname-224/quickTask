from bot import bot
from database.db_funcs import (add_new_task, get_task_by_id,
                               mark_task_completed, mark_task_uncompleted,
                               delete_task, edit_task,
                               add_message, get_message, del_message)
from keyboards import create_kb_cancel_to_edit, create_kb_cancel_to_add
from weather.weather import main
from utils import (text_for_reply_to_bad_input, get_task_id, delete_msg,
                   show_tasklist, update_tasklist, show_message_task,
                   update_message_task, update_message_task_edit,
                   ALL_MESSAGE_TYPES)


@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def show_task(call):
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)


@bot.message_handler(commands=['view_tasks'])
def view_tasks_handler(message):
    delete_msg(message.chat.id, message.message_id)

    if mess_from_db := get_message("tasklist"):
        del_message(mess_from_db.id)
        delete_msg(message.chat.id, mess_from_db.id)
    add_message(msg_id=message.message_id + 1, msg_name="tasklist")
    show_tasklist(message)


@bot.callback_query_handler(func=lambda call: call.data == "remove_tasklist")
def remove_tasklist(call):
    if mess_from_db := get_message("tasklist"):
        if mess_from_db.id == call.message.id:
            del_message(mess_from_db.id)
            delete_msg(call.message.chat.id, mess_from_db.id)

    delete_msg(call.message.chat.id, call.message.id)

@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_by_btn(call):
    add(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_completed_"))
def bot_mark_task_completed(call):
    task_id = get_task_id(call.data)
    mark_task_completed(task_id)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("mark_uncompleted_"))
def bot_mark_task_uncompleted(call):
    task_id = get_task_id(call.data)
    mark_task_uncompleted(task_id)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def bot_delete_task(call):
    task_id = get_task_id(call.data)
    delete_task(task_id)
    update_tasklist(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_msg"))
def bot_edit_task(call):
    task_id = get_task_id(call.data)
    update_message_task_edit(task_id, call.message)


@bot.callback_query_handler(func=lambda call: call.data == "return")
def handle_return(call):
    update_tasklist(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("return_to_task_"))
def return_to_task(call):
    task_id = get_task_id(call.data)
    update_message_task(task_id, call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_title_"))
def edit_title(call):
    if mess_from_db := get_message("tasklist"):
        if mess_from_db.id == call.message.id:
            del_message(mess_from_db.id)
            delete_msg(call.message.chat.id, mess_from_db.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_title(msg, task_id, start_msg_id)
    )


def update_title(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('названия'))
        bot.register_next_step_handler(
            message, lambda msg: update_title(msg, task_id, start_msg_id))
        return

    edit_task(task_id=task_id, title=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    if mess_from_db := get_message("tasklist"):
        del_message(mess_from_db.id)
        delete_msg(message.chat.id, mess_from_db.id)
    add_message(msg_id=message.message_id + 1, msg_name="tasklist")
    show_message_task(task_id, message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_description"))
def edit_description(call):
    if mess_from_db := get_message("tasklist"):
        if mess_from_db.id == call.message.id:
            del_message(mess_from_db.id)
            delete_msg(call.message.chat.id, mess_from_db.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: update_description(msg, task_id, start_msg_id)
    )

def update_description(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('описания'))
        bot.register_next_step_handler(
            message,
            lambda msg: update_description(msg, task_id, start_msg_id)
        )
        return

    edit_task(task_id=task_id, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(
    #     message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    if mess_from_db := get_message("tasklist"):
        del_message(mess_from_db.id)
        delete_msg(message.chat.id, mess_from_db.id)
    add_message(msg_id=message.message_id + 1, msg_name="tasklist")
    show_message_task(task_id, message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_all"))
def edit_all(call):
    if mess_from_db := get_message("tasklist"):
        if mess_from_db.id == call.message.id:
            del_message(mess_from_db.id)
            delete_msg(call.message.chat.id, mess_from_db.id)

    task_id = get_task_id(call.data)
    task = get_task_by_id(task_id)
    start_msg_id = call.message.message_id + 1

    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Текущее <u><b>название</b></u>: "
             f"<code>{task.title}</code>\n\n"
             f"Напишите новое <u><b>название</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        call.message,
        lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
    )

def edit_all_get_title(message, task_id, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('названия'))
        bot.register_next_step_handler(
            message,
            lambda msg: edit_all_get_title(msg, task_id, start_msg_id)
        )
        return

    title = message.text

    task = get_task_by_id(task_id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Текущее <u><b>описание</b></u>: "
             f"<code>{task.description}</code>\n\n"
             f"Напишите новое <u><b>описание</b></u> задачи",
        parse_mode="HTML",
    )

    bot.register_next_step_handler(
        message,lambda msg: update_all(msg, task_id, start_msg_id, title))

def update_all(message, task_id, start_msg_id, title):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('описания'))
        bot.register_next_step_handler(
            message, lambda msg: update_all(msg, task_id, start_msg_id, title))
        return

    edit_task(task_id=task_id, title=title, description=message.text)

    # ToDo переделать отправку таких сообщений
    # bot.send_message(message.chat.id, "Изменения сохранены")

    bot.delete_messages(
        message.chat.id,list(range(start_msg_id, message.message_id + 1)))

    if mess_from_db := get_message("tasklist"):
        del_message(mess_from_db.id)
        delete_msg(message.chat.id, mess_from_db.id)
    add_message(msg_id=message.message_id + 1, msg_name="tasklist")
    show_message_task(task_id, message)


# - Команды [/start, /help] -
@bot.message_handler(commands=['start', 'help'])
def show_about(message):
    delete_msg(message.chat.id, message.id)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет {message.chat.first_name}!\n"
             "Я твой персональный ToDo-бот"
    )


def add(message):
    if mess_from_db := get_message("tasklist"):
        if mess_from_db.id == message.id:
            del_message(mess_from_db.id)
            delete_msg(message.chat.id, mess_from_db.id)


    start_msg_id = message.message_id + 1

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите название задачи",
        reply_markup = create_kb_cancel_to_add()

    )
    bot.register_next_step_handler(
        message, lambda msg: handle_add_title(msg, start_msg_id))

def handle_add_title(message, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('названия'))
        bot.register_next_step_handler(
            message, lambda msg: handle_add_title(msg, start_msg_id))
        return

    title = message.text

    bot.send_message(
        chat_id=message.chat.id,
        text="Напишите описание задачи",
        reply_markup = create_kb_cancel_to_add()
    )
    bot.register_next_step_handler(
        message, lambda msg: handle_add_description(msg, title, start_msg_id))

def handle_add_description(message, title, start_msg_id):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.reply_to(
            message=message,text=text_for_reply_to_bad_input('описания'))
        bot.register_next_step_handler(
            message, lambda msg: handle_add_description(
                msg, title, start_msg_id))
        return

    description = message.text
    add_new_task(title, description, message.chat.id)

    bot.delete_messages(
        message.chat.id, list(range(start_msg_id, message.message_id + 1)))

    if mess_from_db := get_message("tasklist"):
        del_message(mess_from_db.id)
        delete_msg(message.chat.id, mess_from_db.id)
    add_message(msg_id=message.message_id + 1, msg_name="tasklist")
    show_tasklist(message)


@bot.message_handler(content_types=['text'])
def weather(message):
    try:
        bot.send_message(
            chat_id=message.chat.id,
            text=main(message.text)
        )
    finally:
        delete_msg(message.chat.id, message.id)


# Перехват всех остальных сообщений
@bot.message_handler(content_types=ALL_MESSAGE_TYPES)
def handle(message):
    delete_msg(message.chat.id, message.message_id)




if __name__ == "__main__":
    bot.skip_pending = True
    bot.polling()