import telebot
import sqlite3
import random
from telebot import types

bot = telebot.TeleBot('your token')

current_word_data = None
words_to_translate = []

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для изучения иностранных языков!')
    with open(r'the path to the picture here', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    send_language_choices(message)


@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    global current_word_data
    global words_to_translate
    global current_sentence_data
    global sentences_to_translate

    if current_word_data and words_to_translate:
        # Обработка ответа на перевод слова
        user_answer = message.text.strip().lower()
        correct_answer = current_word_data[5].strip().lower()

        if user_answer == correct_answer:
            bot.send_message(message.chat.id, 'Верно! Правильный ответ: ' + correct_answer)
        else:
            bot.send_message(message.chat.id, 'Неверно! Правильный ответ: ' + correct_answer)

        words_to_translate.pop(0)
        if words_to_translate:
            send_word(message, words_to_translate[0])
        else:
            bot.send_message(message.chat.id, 'Слова закончились. Выберите другое задание.')

        current_word_data = None
    elif current_sentence_data and sentences_to_translate:
        # Обработка ответа на перевод предложения
        user_answer = message.text.strip().lower()
        correct_answer = current_sentence_data[1].strip().lower()

        if user_answer == correct_answer:
            bot.send_message(message.chat.id, 'Верно! Правильный ответ: ' + correct_answer)
        else:
            bot.send_message(message.chat.id, 'Неверно! Правильный ответ: ' + correct_answer)

        sentences_to_translate.pop(0)
        if sentences_to_translate:
            send_sentence(message, sentences_to_translate[0])

        else:
            bot.send_message(message.chat.id, 'Предложения закончились. Выберите другое задание.')

        current_sentence_data = None  # Сброс текущего предложения
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите язык для продолжения обучения.')
        send_language_choices(message)

@bot.message_handler(content_types=['menu'])
def menu(message):
    bot.reply_to(message, 'Выберите язык, который хотели бы изучить!')
    send_language_choices(message)

def english_menu(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Перевод слов', callback_data='words')
    button2 = types.InlineKeyboardButton('Перевод предложений', callback_data='sentences')
    markup.row(button1, button2)
    bot.send_message(message.chat.id, 'Выберите задание', reply_markup=markup)

def french_menu(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Перевод слов', callback_data='words.fr')
    button2 = types.InlineKeyboardButton('Перевод предложений', callback_data='sentences.fr')
    markup.row(button1, button2)
    bot.send_message(message.chat.id, 'Выберите задание', reply_markup=markup)

def reset():
    global correct_answers
    correct_answers = 0

def send_word(message, word_data):
    global current_word_data
    russian_word = word_data[0]
    options = list(word_data[1:5])
    correct_option = word_data[5]

    random.shuffle(options)

    markup = types.InlineKeyboardMarkup()
    for option in options:
        button = types.InlineKeyboardButton(option, callback_data=option)
        markup.add(button)

    bot.send_message(message.chat.id, f'Переведите слово "{russian_word}":', reply_markup=markup)

    current_word_data = word_data

def send_sentence(message, sentence_data):
    global current_sentence_data
    russian_sentence = sentence_data[0]
    sentence_to_translate = sentence_data[1]

    bot.send_message(message.chat.id, f'Переведите предложение:\n\n{russian_sentence}')

    current_sentence_data = sentence_data

def send_language_choices(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Английский язык', callback_data='english')
    button2 = types.InlineKeyboardButton('Французский язык', callback_data='french')
    markup.row(button1, button2)
    bot.send_message(message.chat.id, 'Выберите язык:', reply_markup=markup)

correct_answers = 0
current_sentence_data = None
sentences_to_translate = []

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global current_word_data
    global current_sentence_data
    global words_to_translate
    global sentences_to_translate
    global correct_answers

    if call.data == 'english':
        bot.send_message(call.message.chat.id, 'Вы выбрали английский язык!')
        english_menu(call.message)
    elif call.data == 'words':
        bot.send_message(call.message.chat.id, 'Сейчас вы переводите слова')
        connect = sqlite3.connect('forTranslationWords.db')
        cursor = connect.cursor()
        cursor.execute(
            'SELECT word_russian, option1, option2, option3, option4, correct_option FROM forTranslationWords ORDER BY RANDOM() LIMIT 10')
        words_to_translate = cursor.fetchall()
        connect.close()

        send_word(call.message, words_to_translate[0])

    elif call.data == 'sentences':
        bot.send_message(call.message.chat.id, 'Сейчас вы переводите предложения')
        connect = sqlite3.connect('secondtaskEng.db')
        cursor = connect.cursor()
        cursor.execute(
            'SELECT sent_russian, right_sent FROM translation_tasks2Eng ORDER BY RANDOM() LIMIT 2')
        sentences_to_translate = cursor.fetchall()
        connect.close()

        send_sentence(call.message, sentences_to_translate[0])

    elif call.data == 'french':
        bot.send_message(call.message.chat.id, 'Вы выбрали французский язык!')
        french_menu(call.message)
    elif call.data == 'words.fr':
        bot.send_message(call.message.chat.id, 'Сейчас вы переводите слова')
        connect = sqlite3.connect('forTranslationWordsFR.db')
        cursor = connect.cursor()
        cursor.execute(
            'SELECT word_russian, option1, option2, option3, option4, correct_option FROM translation_tasksFR ORDER BY RANDOM() LIMIT 10')
        words_to_translate = cursor.fetchall()
        connect.close()

        send_word(call.message, words_to_translate[0])

    elif call.data == 'sentences.fr':
        bot.send_message(call.message.chat.id, 'Сейчас вы переводите предложения')
        connect = sqlite3.connect('secondtaskfr.db')
        cursor = connect.cursor()
        cursor.execute(
            'SELECT sent_russian, right_sent FROM secondFRtask ORDER BY RANDOM() LIMIT 2')
        sentences_to_translate = cursor.fetchall()
        connect.close()

        send_sentence(call.message, sentences_to_translate[0])

    elif current_word_data:
        user_answer = call.data.strip().lower()
        correct_answer = current_word_data[5].strip().lower()

        if user_answer == correct_answer:
            bot.send_message(call.message.chat.id, 'Верно! Правильный ответ: ' + correct_answer)
            correct_answers += 1
        else:
            bot.send_message(call.message.chat.id, 'Неверно! Правильный ответ: ' + correct_answer)

        if words_to_translate:
            words_to_translate = words_to_translate[1:]
            if words_to_translate:
                send_word(call.message, words_to_translate[0])
            else:
                bot.send_message(call.message.chat.id, f'Вы выполнили {correct_answers}/10 заданий верно')
                reset()
                send_language_choices(call.message)
    elif current_sentence_data:
        user_answer = call.data.strip().lower()
        correct_answer = current_sentence_data[1].strip().lower()

        if user_answer == correct_answer:
            bot.send_message(call.message.chat.id, 'Верно! Правильный ответ: ' + correct_answer)
            correct_answers += 1
        else:
            bot.send_message(call.message.chat.id, 'Неверно! Правильный ответ: ' + correct_answer)

        if sentences_to_translate:
            sentences_to_translate = sentences_to_translate[1:]
            if sentences_to_translate:
                send_sentence(call.message, sentences_to_translate[0])
            else:
                bot.send_message(call.message.chat.id, f'Вы выполнили {correct_answers}/10 заданий верно')
                reset()
                send_language_choices(call.message)

bot.polling(none_stop=True)
