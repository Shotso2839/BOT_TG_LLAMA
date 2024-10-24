from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import telebot
import os
import random
from datetime import datetime


#закоментированные сегменты это функции которые были реализованны не до конца
'''
translator = GoogleTranslator(source='auto', target='en')
translated_text = translator.translate("Привет, как дела?")
print(translated_text)
'''
#Это основной промпт что бы llm понимала что пришет в чат и сесть пользователь + запоминать предидущие сообщения
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""
#подключение лакально развёрнутой нейросети через Ollama
#дальше я всязываю текущиз запрос и template что бы в нейросеть закидывать вопрос-user_input и память
model = OllamaLLM(model='llama3.1:8b')
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

#это переменная для коректного добавления новых сообщений в память и возвращения результата ответа на вопрос после добавления
context = ""
def hendle_conversation(user_input):
    global context
    resolt = chain.invoke({"context": context, "question": user_input})
    context += f"\nUser:{user_input}\nAI:{resolt}"
    return resolt
#подключение к боту
bot = telebot.TeleBot('7566688809:AAFdJjsj2ipMlAowwlZKznLD7hp5uc_Wy0s')
#обработака команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Добро пожаловать {user_first_name}! Я llama бот, могу поддерживать диалог, отвечать на вопросы и ещё кое что.\nЧтобы узнать все команды используйте /help\nЕсли вы хотите что бы бот отвечал на каком то языке попросите его что бы от отвечал только на этом языке")
#отбаботка команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "/start - бот приветствует вас и описывает себя\n/end - это остановит бота, до того момента пока его сервер занаво не запустят\n/random_emoji - присылает случайную эмоцию из списка\n/current_time - узнать текущую дату и время\n/my_id - показывает ваш уникальный идентификатор id в Telegram")
#отбаботка команды /end
@bot.message_handler(commands=['end'])
def send_help(message):
    bot.send_message(message.chat.id, 'бот остановлен, до повторного запуска на сервере')
    bot.stop_polling()
    os._exit(0)
#отбаботка команды /my_id
@bot.message_handler(commands=['my_id'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"Ваш ID в Telegram: {user_id}")
#отбаботка команды /current_time время берётся с помощю отдельной библиотеки
@bot.message_handler(commands=['current_time'])
def current_time(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(message.chat.id, f"Текущая дата и время: {current_time}")

#эта команда выдавала ошибку, поэтому пока что не вошла в проект
'''
@bot.message_handler(commands=['weather'])
def get_weather(message):
    city = message.text.split()[1]
    api_key = 'y9e51a20c0a0a95a428a80f81c139fc61'
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(weather_url)
    data = response.json()
    if data.get('main'):
        temp = data['main']['temp']
        weather_desc = data['weather'][0]['description']
        bot.send_message(message.chat.id, f"The temperature in {city} is {temp}°C with {weather_desc}.")
    else:
        bot.send_message(message.chat.id, "City not found.")
'''
#отбаботка команды /random_emoji они реально случайные с помощю библиоткеи random
@bot.message_handler(commands=['random_emoji'])
def send_random_emoji(message):
    emojis = [
        '😐','😍','😎','🫡','🤪','🥸','😂','😕','😱']
    bot.send_message(message.chat.id, random.choice(emojis))

#стандартынй ответ на все сообщения кроме спец команд, они идут на обработку в нейросеть
@bot.message_handler(content_types=['text'])
def send_message_llama(message):
    bot.send_message(message.chat.id, hendle_conversation(message.text))

#ответ для фото что бы пользователь понимал что их нет смысла присылать
@bot.message_handler(content_types=['photo'])
def photo_message(message):
    bot.send_photo(message.chat.id, 'к сожаления я пока что не умею отвечать на фото')

#бесконечный запуск бота, что бы просто ожидать сообщения, ещё не разабрался как сделать через вебхуки
bot.polling(non_stop=True)