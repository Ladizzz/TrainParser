import requests
from bs4 import BeautifulSoup
import time
import datetime
import telebot
import sys

bot = telebot.TeleBot('***REMOVED***')
train_number = 0
iteration = 0
sleep_time = 60
url = 'https://pass.rw.by/ru/route/?from=%D0%9E%D1%80%D1%88%D0%B0&from_exp=2100170&from_esr=166403&to=%D0%9C%D0%B8%D0%BD%D1%81%D0%BA&to_exp=2100000&to_esr=140210&front_date=%D1%81%D0%B5%D0%B3%D0%BE%D0%B4%D0%BD%D1%8F&date=today'


@bot.message_handler(commands=['start'])
def start_message(message):
    hideboard = telebot.types.ReplyKeyboardRemove()
    # keyboard = telebot.types.InlineKeyboardMarkup()
    # keyboard = telebot.types.ReplyKeyboardMarkup()
    # keyboard.row(telebot.types.InlineKeyboardButton('Set', callback_data='/set'),
    #              telebot.types.InlineKeyboardButton('Update', callback_data='/update'),
    #              telebot.types.InlineKeyboardButton('Restart', callback_data='/start'))
    # keyboard.row(telebot.types.KeyboardButton('/set'),
    #              telebot.types.KeyboardButton('/update'),
    #              telebot.types.KeyboardButton('/start'))
    bot.send_message(message.chat.id, 'Привет, вот список доступных поездов:')
    bot.send_message(message.chat.id, parser_2())
    # bot.send_message(message.chat.id, 'Для выбора поезда используйте /set', reply_markup=keyboard)
    hello_message = 'Для выбора поезда используйте /set "число"\n'
    hello_message += 'Для ручного обновления используйте /update\n'
    hello_message += 'Для изменения времени обновления используйте /time "число"\n'
    hello_message += 'Для завершения работы используйте /stop'
    bot.send_message(message.chat.id, hello_message, reply_markup=hideboard)


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    hello_message = 'Bye!\n'
    bot.send_message(message.chat.id, hello_message)
    sys.exit(0)


def updater(message, start_iteration):
    global iteration
    while iteration == start_iteration:
        ans = parser_4(train_number)
        current_datetime = datetime.datetime.now()
        print(current_datetime)
        temp = parser_3(train_number)
        print(temp)
        if ans is not None:
            bot.send_message(message.chat.id, str(current_datetime) + '\n' + str(temp))
        else:
            print('Telegram message was not sent!')
        time.sleep(sleep_time)


@bot.message_handler(commands=['set'])
def set_train(message):
    global train_number
    command = message.text.split()
    train_number = int(command[1]) - 1
    bot.send_message(message.chat.id, f'Поезд №{train_number + 1} выбран успешно!')
    global iteration
    iteration += 1
    updater(message, iteration)


@bot.message_handler(commands=['update'])
def fast_update(message):
    global iteration
    iteration += 1
    bot.send_message(message.chat.id, f'Ручное обновление выполнено успешно!')
    updater(message, iteration)


@bot.message_handler(commands=['time'])
def set_train(message):
    global sleep_time
    command = message.text.split()
    sleep_time = int(command[1])
    global iteration
    iteration += 1
    bot.send_message(message.chat.id, f'Установлено время обновления в {sleep_time} секунд!')
    updater(message, iteration)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')
    else:
        bot.send_message(message.chat.id, 'Команда не распознана')


def parser_2():
    global url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup)
    items = soup.find_all('div', class_='sch-table__row-wrap')
    # print(items)
    ans = ''

    for number, data in enumerate(items, start=1):
        train_name = data.find('span', class_='train-route').text.strip()
        train_departure = data.find('div', class_='sch-table__time train-from-time').text.strip()
        train_arrive = data.find('div', class_='sch-table__time train-to-time').text.strip()
        train_duration = data.find('div', class_='sch-table__duration train-duration-time').text.strip()
        train_tickets = data.find('div', class_='sch-table__tickets')

        ans += f'{number}: {train_name} {train_departure} {train_arrive} {train_duration}\n'
        ans += 'Билеты:\n'

        if train_tickets != '\n':
            ticket_types = data.find_all('div', class_='sch-table__t-name')
            ticket_space = data.find_all('a', class_='sch-table__t-quant js-train-modal dash')
            ticket_cost = data.find_all('span', class_='ticket-cost')
            for j in range(len(ticket_types)):
                # if ticket_types[j]:
                #     print(f'Тип: {ticket_types[j].text}')
                # if ticket_space[j]:
                #     print(f'Свободно: {ticket_space[j].text}')
                # if ticket_cost[j]:
                #     print(f'Цена: {ticket_cost[j].text}')
                ans += f'Тип: {ticket_types[j].text} --- Свободно: {ticket_space[j].text} --- Цена: {ticket_cost[j].text}\n'

        train_tickets_bad = data.find('div', class_='sch-table__no-info')
        if train_tickets_bad:
            train_tickets_bad = data.find('div', class_='sch-table__no-info').text.strip()
            ans += f'{train_tickets_bad}\n'
        ans += '\n'

    return ans


def parser_3(number):
    global url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    items = soup.find_all('div', class_='sch-table__row-wrap')

    train_name = items[number].find('span', class_='train-route').text.strip()
    train_departure = items[number].find('div', class_='sch-table__time train-from-time').text.strip()
    train_arrive = items[number].find('div', class_='sch-table__time train-to-time').text.strip()
    train_duration = items[number].find('div', class_='sch-table__duration train-duration-time').text.strip()
    train_tickets = items[number].find('div', class_='sch-table__tickets')
    ans = f'{train_name} {train_departure} {train_arrive} {train_duration}'
    ans += '\nБилеты:\n'
    if train_tickets:
        ticket_types = items[number].find_all('div', class_='sch-table__t-name')
        ticket_space = items[number].find_all('a', class_='sch-table__t-quant js-train-modal dash')
        ticket_cost = items[number].find_all('span', class_='ticket-cost')
        for j in range(len(ticket_types)):
            ans += f'Тип: {ticket_types[j].text} Свободно: {ticket_space[j].text} Цена: {ticket_cost[j].text}\n'

    train_tickets_bad = items[number].find('div', class_='sch-table__no-info')
    if train_tickets_bad:
        train_tickets_bad = items[number].find('div', class_='sch-table__no-info').text.strip()
        ans += f'{train_tickets_bad}'

    return ans


def parser_4(number):
    global url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    items = soup.find_all('div', class_='sch-table__row-wrap')
    ans = ''
    train_tickets = items[number].find('div', class_='sch-table__tickets')
    if train_tickets.text != '\n':
        train_name = items[number].find('span', class_='train-route').text.strip()
        train_departure = items[number].find('div', class_='sch-table__time train-from-time').text.strip()
        train_arrive = items[number].find('div', class_='sch-table__time train-to-time').text.strip()
        train_duration = items[number].find('div', class_='sch-table__duration train-duration-time').text.strip()
        ans += f'{train_name} {train_departure} {train_arrive} {train_duration}'

        ans += '\nБилеты:\n'
        ticket_types = items[number].find_all('div', class_='sch-table__t-name')
        ticket_space = items[number].find_all('a', class_='sch-table__t-quant js-train-modal dash')
        ticket_cost = items[number].find_all('span', class_='ticket-cost')
        for j in range(len(ticket_types)):
            ans += f'Тип: {ticket_types[j].text} Свободно: {ticket_space[j].text} Цена: {ticket_cost[j].text}\n'
        return ans
    else:
        return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot.polling()
