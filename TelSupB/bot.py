import config
import core
import telebot
import random
import datetime
import markup
import sys
from telebot import apihelper

if config.PROXY_URL:
    apihelper.proxy = {'https': config.PROXY_URL}

bot = telebot.TeleBot(config.TOKEN, skip_pending=True)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     '👋🏻 Hello! This is a bot for technical user support.\nIf you have any questions or issues, click the <b>Submit a Request</b> button, and our staff will respond to you shortly!',
                     parse_mode='html', reply_markup=markup.markup_main())


@bot.message_handler(commands=['agent'])
def agent(message):
    user_id = message.from_user.id

    if core.check_agent_status(user_id) == True:
        bot.send_message(message.chat.id, '🔑 You are logged in as a Support Agent', parse_mode='html',
                         reply_markup=markup.markup_agent())
    else:
        take_password_message = bot.send_message(message.chat.id,
                                                 '⚠️ You are not in the database. Please send a one-time access password.',
                                                 reply_markup=markup.markup_cancel())
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_password_message, get_password_message)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id

    if str(user_id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, '🔑 You are logged in as an Admin', reply_markup=markup.markup_admin())
    else:
        bot.send_message(message.chat.id, '🚫 This command is only available to the administrator.')


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    if message.text == '✏️ Написать запрос':
        take_new_request = bot.send_message(message.chat.id,
                                            'Введите свой запрос и наши сотрудники скоро с вами свяжутся.',
                                            reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)



    elif message.text == '✉️ My Requests':
        markup_and_value = markup.markup_reqs(user_id, 'my_reqs', '1')
    markup_req = markup_and_value[0]
    value = markup_and_value[1]

    if value == 0:
        bot.send_message(message.chat.id, 'You have no requests yet.', reply_markup=markup.markup_main())
    else:
        bot.send_message(message.chat.id, 'Your requests:', reply_markup=markup_req)

    else:
    bot.send_message(message.chat.id, 'You are returned to the main menu.', parse_mode='html',
                     reply_markup=markup.markup_main())


def get_password_message(message):
    password = message.text
    user_id = message.from_user.id

    if password == None:
        send_message = bot.send_message(message.chat.id, '⚠️ You are not sending text. Please try again.',
                                        reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)

    elif password.lower() == 'cancel':
        bot.send_message(message.chat.id, 'Canceled.', reply_markup=markup.markup_main())
    return

    elif core.valid_password(password) == True:
    core.delete_password(password)
    core.add_agent(user_id)


bot.send_message(message.chat.id, '🔑 You are logged in as a Support Agent', parse_mode='html',
                 reply_markup=markup.markup_main())
bot.send_message(message.chat.id, 'Select a section from the technical panel:', parse_mode='html',
                 reply_markup=markup.markup_agent())

else:
send_message = bot.send_message(message.chat.id, '⚠️ Invalid password. Please try again.',
                                reply_markup=markup.markup_cancel())

bot.clear_step_handler_by_chat_id(message.chat.id)
bot.register_next_step_handler(send_message, get_password_message)


def get_agent_id_message(message):
    agent_id = message.text

    if agent_id == None:
        take_agent_id_message = bot.send_message(message.chat.id, '⚠️ You are not sending text. Please try again.',
                                                 reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

    elif agent_id.lower() == 'cancel':
        bot.send_message(message.chat.id, 'Canceled.', reply_markup=markup.markup_main())
    return
    else:
        core.add_agent(agent_id)
        bot.send_message(message.chat.id, '✅ Agent successfully added.', reply_markup=markup.markup_main())
        bot.send_message(message.chat.id, 'Select a section from the admin panel:', reply_markup=markup.markup_admin())


def get_new_request(message):
    request = message.text


user_id = message.from_user.id
check_file = core.get_file(message)

# If the user sends a file
if check_file is not None:
    file_id = check_file['file_id']
    file_name = check_file['file_name']
    type = check_file['type']
    request = check_file['text']

    if str(request) == 'None':
        take_new_request = bot.send_message(message.chat.id, '⚠️ You did not enter your request. Please try again by sending text along with the file.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)

    else:
        req_id = core.new_req(user_id, request)
        core.add_file(req_id, file_id, file_name, type)

        bot.send_message(message.chat.id, f'✅ Your request with ID {req_id} has been created. You can view your current requests by clicking the <b>My Current Requests</b> button. Bye @End_Soft', parse_mode='html', reply_markup=markup.markup_main())        

# If the user sends only text
else:
    if request is None:
        take_new_request = bot.send_message(message.chat.id, '⚠️ The data type you are sending is not supported. Please try again by sending your request using one of the available data types (text, files, photos, videos, audio, voice messages). Bye @End_Soft', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)

    elif request.lower() == 'cancel':
        bot.send_message(message.chat.id, 'Canceled. Bye @End_Soft', reply_markup=markup.markup_main())
        return

    else:
        req_id = core.new_req(user_id, request)
        bot.send_message(message.chat.id, f'✅ Your request with ID {req_id} has been created. You can view your current requests by clicking the <b>My Current Requests</b> button. Bye @End_Soft', parse_mode='html', reply_markup=markup.markup_main())
else:
if request is None:
    take_new_request = bot.send_message(message.chat.id,
                                        '⚠️ The data type you are sending is not supported. Please try again by sending your request using one of the available data types (text, files, photos, videos, audio, voice messages).',
                                        reply_markup=markup.markup_cancel())

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(take_new_request, get_new_request)

elif request.lower() == 'cancel':
    bot.send_message(message.chat.id, 'Canceled.', reply_markup=markup.markup_main())
    return

else:
    req_id = core.new_req(user_id, request)
    bot.send_message(message.chat.id,
                     f'✅ Your request with ID {req_id} has been created. You can view your current requests by clicking the <b>My Current Requests</b> button.',
                     parse_mode='html', reply_markup=markup.markup_main())


def get_additional_message(message, req_id, status):
    additional_message = message.text
    check_file = core.get_file(message)

    # Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        additional_message = check_file['text']

        core.add_file(req_id, file_id, file_name, type)

    if additional_message is None:
        take_additional_message = bot.send_message(chat_id=message.chat.id,
                                                   text='⚠️ The data type you are sending is not supported. Please try again by sending your message using one of the available data types (text, files, photos, videos, audio, voice messages).',
                                                   reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status)

    elif additional_message.lower() == 'cancel':
        bot.send_message(message.chat.id, 'Canceled.', reply_markup=markup.markup_main())
        return

    else:
        if additional_message != 'None':
            core.add_message(req_id, additional_message, status)

        if check_file is not None:
            if additional_message != 'None':
                text = '✅ Your file and message have been successfully sent!'
            else:
                text = '✅ Your file has been successfully sent!'
        else:
            text = '✅ Your message has been successfully sent!'

        bot.send_message(message.chat.id, text, reply_markup=markup.markup_main())

        if status == 'agent':
            user_id = core.get_user_id_of_req(req_id)
            try:
                if additional_message == 'None':
                    additional_message = ''

                bot.send_message(user_id,
                                 f'⚠️ New response received for your request with ID {req_id}!\n\n🧑‍💻 Support Agent response:\n{additional_message}',
                                 reply_markup=markup.markup_main())

                if type == 'photo':
                    bot.send_photo(user_id, photo=file_id, reply_markup=markup.markup_main())
                elif type == 'document':
                    bot.send_document(user_id, data=file_id, reply_markup=markup.markup_main())
                elif type == 'video':
                    bot.send_video(user_id, data=file_id, reply_markup=markup.markup_main())
                elif type == 'audio':
                    bot.send_audio(user_id, audio=file_id, reply_markup=markup.markup_main())
                elif type == 'voice':
                    bot.send_voice(user_id, voice=file_id, reply_markup=markup.markup_main())
                else:
                    bot.send_message(user_id, additional_message, reply_markup=markup.markup_main())
            except:
                pass


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id

    if call.message:
        if ('my_reqs:' in call.data) or ('waiting_reqs:' in call.data) or ('answered_reqs:' in call.data) or (
                'confirm_reqs:' in call.data):
            """
            Button handlers for:

            ✉️ My Requests
            ❗️ Awaiting Support Response
            ⏳ Awaiting User Response
            ✅ Completed Requests
            """

            parts = call.data.split(':')
            callback = parts[0]
            number = parts[1]
            markup_and_value = markup.markup_reqs(user_id, callback, number)
            markup_req = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ No requests found.',
                                 reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a request to view the message history or add a new message:',
                                      reply_markup=markup_req)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Your requests:', reply_markup=markup_req)

            bot.answer_callback_query(call.id)
        # Открыть запрос
        elif 'open_req:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]

            req_status = core.get_req_status(req_id)
            request_data = core.get_request_data(req_id, callback)
            len_req_data = len(request_data)

            i = 1
            for data in request_data:
                if i == len_req_data:
                    markup_req = markup.markup_request_action(req_id, req_status, callback)
                else:
                    markup_req = None

                bot.send_message(chat_id=call.message.chat.id, text=data, parse_mode='html', reply_markup=markup_req)

                i += 1

            bot.answer_callback_query(call.id)

        # Добавить сообщение в запрос
        elif 'add_message:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            status_user = parts[2]

            take_additional_message = bot.send_message(chat_id=call.message.chat.id,
                                                       text='Send your message using one of the available data types (text, files, photos, videos, audio, voice messages)',
                                                       reply_markup=markup.markup_cancel())

            bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status_user)

            bot.answer_callback_query(call.id)

        # Complete Request
        elif 'confirm_req:' in call.data:
            parts = call.data.split(':')
            confirm_status = parts[1]
            req_id = parts[2]

            if core.get_req_status(req_id) == 'confirm':
                bot.send_message(chat_id=call.message.chat.id, text="⚠️ This request has already been completed.",
                                 reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            # Request confirmation to complete
            if confirm_status == 'wait':
                bot.send_message(chat_id=call.message.chat.id,
                                 text="To complete the request, click the <b>Confirm</b> button.", parse_mode='html',
                                 reply_markup=markup.markup_confirm_req(req_id))

            # Confirm completion
            elif confirm_status == 'true':
                core.confirm_req(req_id)

                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="✅ Request successfully completed.", reply_markup=markup.markup_main())
                except:
                    bot.send_message(chat_id=call.message.chat.id, text="✅ Request successfully completed.",
                                     reply_markup=markup.markup_main())

                bot.answer_callback_query(call.id)

        # Request Files
        elif 'req_files:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]
            number = parts[3]

            markup_and_value = markup.markup_files(number, req_id, callback)
            markup_files = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ No files found.',
                                 reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a file to download it.', reply_markup=markup_files)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Click on a file to download it.',
                                 reply_markup=markup_files)

            bot.answer_callback_query(call.id)

        # Отправить файл
        elif 'send_file:' in call.data:
            parts = call.data.split(':')
            id = parts[1]
            type = parts[2]

            file_id = core.get_file_id(id)

            if type == 'photo':
                bot.send_photo(call.message.chat.id, photo=file_id, reply_markup=markup.markup_main())
            elif type == 'document':
                bot.send_document(call.message.chat.id, data=file_id, reply_markup=markup.markup_main())
            elif type == 'video':
                bot.send_video(call.message.chat.id, data=file_id, reply_markup=markup.markup_main())
            elif type == 'audio':
                bot.send_audio(call.message.chat.id, audio=file_id, reply_markup=markup.markup_main())
            elif type == 'voice':
                bot.send_voice(call.message.chat.id, voice=file_id, reply_markup=markup.markup_main())

            bot.answer_callback_query(call.id)

        # Вернуться назад в панель агента
        elif call.data == 'back_agent':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='🔑 You are authorized as a Support Agent', parse_mode='html',
                                      reply_markup=markup.markup_agent())
            except:
                bot.send_message(call.message.chat.id, '🔑 You are authorized as a Support Agent', parse_mode='html',
                                 reply_markup=markup.markup_agent())

            bot.answer_callback_query(call.id)

            # Return to Admin panel
            elif call.data == 'back_admin':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='🔑 You are authorized as an Admin', parse_mode='html',
                                      reply_markup=markup.markup_admin())
            except:
                bot.send_message(call.message.chat.id, '🔑 You are authorized as an Admin', parse_mode='html',
                                 reply_markup=markup.markup_admin())

            bot.answer_callback_query(call.id)

        # Add an agent
        elif call.data == 'add_agent':
            take_agent_id_message = bot.send_message(chat_id=call.message.chat.id,
                                                     text='To add a support agent, enter their Telegram ID.',
                                                     reply_markup=markup.markup_cancel())
            bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

        # All agents
        elif 'all_agents:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_agents(number)
            markup_agents = markup_and_value[0]
            len_agents = markup_and_value[1]

            if len_agents == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ No agents found.',
                                 reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a support agent to remove them.', parse_mode='html',
                                      reply_markup=markup_agents)
            except:
                bot.send_message(call.message.chat.id, 'Click on a support agent to remove them.', parse_mode='html',
                                 reply_markup=markup_agents)

            bot.answer_callback_query(call.id)

            # Delete agent
            elif 'delete_agent:' in call.data:
            agent_id = call.data.split(':')[1]
            core.delete_agent(agent_id)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a support agent to remove them.', parse_mode='html',
                                      reply_markup=markup.markup_agents('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Click on a support agent to remove them.', parse_mode='html',
                                 reply_markup=markup.markup_agents('1')[0])

            bot.answer_callback_query(call.id)

        # Все пароли
        elif 'all_passwords:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_passwords(number)
            markup_passwords = markup_and_value[0]
            len_passwords = markup_and_value[1]

            if len_passwords == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ No passwords found.',
                                 reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a password to remove it.', parse_mode='html',
                                      reply_markup=markup_passwords)
            except:
                bot.send_message(call.message.chat.id, 'Click on a password to remove it.', parse_mode='html',
                                 reply_markup=markup_passwords)

            bot.answer_callback_query(call.id)

            # Delete password
            elif 'delete_password:' in call.data:
            password = call.data.split(':')[1]
            core.delete_password(password)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Click on a password to remove it.', parse_mode='html',
                                      reply_markup=markup.markup_passwords('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Click on a password to remove it.', parse_mode='html',
                                 reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        # Generate passwords
        elif call.data == 'generate_passwords':
            # 10 - number of passwords, 16 - password length
            passwords = core.generate_passwords(10, 16)
            core.add_passwords(passwords)

            text_passwords = ''
            i = 1
            for password in passwords:
                text_passwords += f'{i}. {password}\n'
                i += 1

            bot.send_message(call.message.chat.id, f"✅ {i - 1} passwords generated:\n\n{text_passwords}",
                             parse_mode='html', reply_markup=markup.markup_main())
            bot.send_message(call.message.chat.id, 'Click on a password to remove it.', parse_mode='html',
                             reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)


        # Stop the bot
        elif 'stop_bot:' in call.data:
            status = call.data.split(':')[1]

            # Request confirmation to stop
            if status == 'wait':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Are you sure you want to stop the bot?", parse_mode='html',
                                          reply_markup=markup.markup_confirm_stop())
                except:
                    bot.send_message(call.message.chat.id, "Are you sure you want to stop the bot?", parse_mode='html',
                                     reply_markup=markup.markup_confirm_stop())

            # Confirmation received
            elif status == 'confirm':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='✅ Bot stopped.')
                except:
                    bot.send_message(chat_id=call.message.chat.id, text='✅ Bot stopped.')

                bot.answer_callback_query(call.id)
                bot.stop_polling()
                sys.exit()


if __name__ == "__main__":
    bot.polling(none_stop=True)
