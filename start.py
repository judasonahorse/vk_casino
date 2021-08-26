from datetime import datetime, timedelta
from random import randint
import requests
import vk_api

import buttons
import casino
from sqlighter import SQLighter
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
import socket
import urllib3
import time
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import config

vk_session = vk_api.VkApi(token=config.BotToken)  # Обработка access_token
longpoll = VkBotLongPoll(vk_session, config.group_id)  # Данные для работы в сообществе
vk = vk_session.get_api()  # Работа с VK API

db = SQLighter('user.db')

time_format = "%Y-%m-%d %H:%M:%S"
список_дуэль = {'id': 'value'}
список_крестики_нолики = {'id': 'value'}
игры_крестики_нолики = {'id': 'value'}


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def получаем_топ_общий(chat_id_name):
    top_list = ""
    i = 0
    for top in db.get_top(chat_id_name):
        if top[3] != None:
            if top[3] != 0 or top[7] != 0 or top[6] != 0:
                i = i + 1
                if i > 5:
                    break
                top_list = top_list + "\n" + f"{i}. {top[2]}\n    Баланс:{top[3]}₽\n    Банк:{top[7]}\n    Миллионы:{top[6]}"
    return top_list


def get_last_game_id(game_id):
    for game in db.get_last_game_id(game_id):
        return game[0]


def получаем_баланс(user_id, chat_id_name):
    for баланс in db.get_balance(user_id, chat_id_name):
        return баланс[0]


def бонус_по_мск(user_id, chat_id_name):
    for время_бонус in db.get_time_bonus(user_id, chat_id_name):
        бонус_время = datetime.strptime(время_бонус[0], time_format) + timedelta(hours=3)
        return бонус_время


def получаем_время_когда_будет_бонус(user_id, chat_id_name):
    for время_бонус in db.get_time_bonus(user_id, chat_id_name):
        бонус_время = datetime.strptime(время_бонус[0], time_format)
        return бонус_время


def получаем_время_когда_был_положено_под_процент(user_id, chat_id_name):
    for время_процент in db.get_time_bank_procent(user_id, chat_id_name):
        время_сейчас = (datetime.now()).strftime(time_format)
        if время_процент[0] == 0:
            db.update_time_bank_procent(user_id, время_сейчас, chat_id_name)
            процент_время = datetime.strptime(время_сейчас, time_format)
        else:
            процент_время = datetime.strptime(время_процент[0], time_format)
        return процент_время


def bonus(user_id, chat_id_name):
    сейчас_время = datetime.now()

    if получаем_время_когда_будет_бонус(user_id, chat_id_name) < сейчас_время:
        db.update_time_bonus(user_id, datetime.now() + timedelta(minutes=config.время_для_бонуса), chat_id_name)
        db.update_bonus(user_id, 1, chat_id_name)
        return True
    return False


def получаем_сколько_бонусов_юзера(user_id, chat_id_name):
    for бонус in db.get_bonus(user_id, chat_id_name):
        return бонус[0]


def get_last_name(user_id):
    return str(vk.users.get(user_ids=(str(user_id)))[0]['last_name'])  # получение фамилииmsg


def получаем_медали(user_id, chat_id_name):
    for медаль in db.get_medal(user_id, chat_id_name):
        return медаль[0]


def получаем_банк(user_id, chat_id_name):
    for банк in db.get_bank(user_id, chat_id_name):
        return банк[0]


def получаем_сколько_накапал_банк(id, chat_id_name):
    время_процент = получаем_время_когда_был_положено_под_процент(id, chat_id_name)
    сколько_прошло_после_вклада = ((datetime.now() - время_процент).total_seconds()) / 60
    процент_банк_сумма = ""
    старое_значение_банка = получаем_банк(id, chat_id_name)
    if сколько_прошло_после_вклада > 1:
        процент_банк_сумма = round(получаем_банк(id, chat_id_name) + (
                (получаем_банк(id, chat_id_name) / 100) * (config.проценты_банк * сколько_прошло_после_вклада)), 1)
        db.update_bank(id, процент_банк_сумма, chat_id_name)
        db.update_time_bank_procent(id, (datetime.now()).strftime(time_format), chat_id_name)
        return int(round(процент_банк_сумма - старое_значение_банка, 1))
    return 0


def main():
    while True:

        try:

            for event in longpoll.listen():
                random = randint(0, 100)
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.obj.peer_id != event.obj.from_id:

                        chat_id_name = f"id{event.object['peer_id']}id"
                        game_id_name = f"gameid{event.object['peer_id']}gameid"
                        db.create_table_for_chat(chat_id_name)

                        last_name = get_last_name(event.object.from_id)

                        msg = str(event.object['text'].lower()).replace("[club201483157|@d1slor] ", "")

                        if not db.subscriber_exists(event.object.from_id, chat_id_name):
                            db.add_subscriber(event.object.from_id, chat_id_name)
                            db.update_firstname(event.object.from_id, last_name, chat_id_name)

                        def рейтинг():
                            медали = получаем_медали(event.object.from_id, chat_id_name)
                            всего_денег = получаем_баланс(event.object.from_id, chat_id_name) + получаем_банк(
                                event.object.from_id, chat_id_name)
                            if всего_денег != None and всего_денег > 1000000:
                                на_сколько_повысился = медали + (
                                        всего_денег / 1000000)
                                db.update_bank(event.object.from_id, 0, chat_id_name)
                                db.update_balance(event.object.from_id, config.размер_бонуса, chat_id_name)
                                db.update_medal(event.object.from_id, round(на_сколько_повысился, 1), chat_id_name)

                                return на_сколько_повысился
                            return медали

                        def проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие, исключение=False,
                                            исключение2=False):
                            if db.subscriber_exists(номер_счёта_получателя, chat_id_name):
                                if int(номер_счёта_получателя) != int(event.object.from_id) or исключение == True:
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id, chat_id_name), получаем_баланс(номер_счёта_получателя,
                                                                                             chat_id_name)
                                    if баланс_отправителя is None:
                                        db.update_balance(event.object.from_id, config.размер_бонуса, chat_id_name)
                                    elif баланс_получателя is None:
                                        db.update_balance(номер_счёта_получателя, config.размер_бонуса, chat_id_name)
                                    elif not isint(деньги_отправляемые):
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, деньги должны быть целочислены",
                                                         keyboard=buttons.menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(деньги_отправляемые) < 0 or int(деньги_отправляемые) == 0:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, жулик нельзя переводить меньше 0 или 0",
                                                         keyboard=buttons.menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(баланс_отправителя) < int(деньги_отправляемые) and исключение2 == False:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, у вас столько денег нет",
                                                         keyboard=buttons.menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(деньги_отправляемые) > int(
                                            получаем_банк(event.object.from_id, chat_id_name)) and исключение2 == True:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, у вас столько денег нет",
                                                         keyboard=buttons.menu.get_keyboard(),
                                                         random_id=get_random_id())


                                    else:
                                        действие()

                                else:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, нельзя переводить себе",
                                                     keyboard=buttons.menu.get_keyboard(),
                                                     random_id=get_random_id())


                            else:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, такого счёта нет",
                                                 keyboard=buttons.menu.get_keyboard(),
                                                 random_id=get_random_id())

                        if msg == casino.крестик_1 or msg == casino.крестик_2 or msg == casino.крестик_3 or msg == casino.крестик_4 or msg == casino.крестик_5 or msg == casino.крестик_6 or msg == casino.крестик_7 or msg == casino.крестик_8 or msg == casino.крестик_9:
                            try:
                                игра = игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]

                                номер_ячейки = int(msg[0][0])
                                крестик = "❌"
                                нолик = "⭕"

                                def кто_выйграл(знак, игра):
                                    if игра[1] == знак and игра[2] == знак and игра[3] == знак:
                                        return True
                                    elif игра[4] == знак and игра[5] == знак and игра[6] == знак:
                                        return True
                                    elif игра[7] == знак and игра[8] == знак and игра[9] == знак:
                                        return True
                                    elif игра[1] == знак and игра[5] == знак and игра[9] == знак:
                                        return True
                                    elif игра[3] == знак and игра[5] == знак and игра[7] == знак:
                                        return True
                                    elif игра[1] == знак and игра[4] == знак and игра[7] == знак:
                                        return True
                                    elif игра[2] == знак and игра[5] == знак and игра[8] == знак:
                                        return True
                                    elif игра[3] == знак and игра[6] == знак and игра[9] == знак:
                                        return True

                                    return False

                                def ничья(игра):
                                    if игра[1] != casino.крестик_1 and игра[2] != casino.крестик_2 and игра[
                                        3] != casino.крестик_3 and игра[
                                        4] != casino.крестик_4 and игра[5] != casino.крестик_5 and игра[
                                        6] != casino.крестик_6 and игра[
                                        7] != casino.крестик_7 and игра[8] != casino.крестик_8 and игра[
                                        9] != casino.крестик_9:
                                        return True
                                    False
                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, нет такой игры",

                                                 random_id=get_random_id())

                            def кто_выйграл2(игра):

                                if кто_выйграл(крестик, игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]) is True:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, Победил! {деньги_отправляемые}₽",
                                                     keyboard=casino.крестики_нолики(игра),
                                                     random_id=get_random_id())
                                    db.get_balance(event.object.from_id) + (деньги_отправляемые * 2)
                                    return True


                                elif кто_выйграл(нолик, игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]) is True:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{get_last_name(список_крестики_нолики[event.object.from_id][1])}, Победил! {деньги_отправляемые}₽",
                                                     keyboard=casino.крестики_нолики(игра),
                                                     random_id=get_random_id())
                                    db.get_balance(список_крестики_нолики[event.object.from_id][1]) + (
                                                деньги_отправляемые * 2)


                                elif ничья(игры_крестики_нолики[
                                               event.object.from_id + список_крестики_нолики[event.object.from_id][1]][
                                               0]) is True:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"Ничья!",
                                                     keyboard=casino.крестики_нолики(игра),
                                                     random_id=get_random_id())
                                    return True

                                return False

                            def обнуление_игры():
                                игрок = список_крестики_нолики[event.object.from_id][1]

                                игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]] = 0
                                список_крестики_нолики[игрок] = 0
                                список_крестики_нолики[event.object.from_id] = 0

                            if event.object.from_id == игры_крестики_нолики[
                                event.object.from_id + список_крестики_нолики[event.object.from_id][1]][1][0]:
                                if список_крестики_нолики[event.object.from_id][3] is True:

                                    игра[номер_ячейки] = крестик

                                    if not кто_выйграл2(игра):
                                        игры_крестики_нолики[
                                            event.object.from_id + список_крестики_нолики[event.object.from_id][1]][
                                            1][0] = список_крестики_нолики[event.object.from_id][1]
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{get_last_name(список_крестики_нолики[event.object.from_id][1])},Ходите! {деньги_отправляемые}₽",
                                                         keyboard=casino.крестики_нолики(игра),
                                                         random_id=get_random_id())

                                    else:
                                        обнуление_игры()
                                elif список_крестики_нолики[event.object.from_id][3] is False:

                                    игра[номер_ячейки] = нолик
                                    if not кто_выйграл2(игра):
                                        игры_крестики_нолики[
                                            event.object.from_id + список_крестики_нолики[event.object.from_id][1]][
                                            1][0] = список_крестики_нолики[event.object.from_id][1]
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{get_last_name(список_крестики_нолики[event.object.from_id][1])},Ходите!",
                                                         keyboard=casino.крестики_нолики(игра),
                                                         random_id=get_random_id())
                                    else:
                                        обнуление_игры()

                            else:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name},не ваш ход!",
                                                 keyboard=casino.крестики_нолики(игра),
                                                 random_id=get_random_id())

                        if config.крестики_нолики_принять_текст == msg:

                            try:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name},доиграйте с {get_last_name(список_крестики_нолики[event.object.from_id][2])}",
                                                 keyboard=casino.крестики_нолики(casino.карта_крестики_нолики),
                                                 random_id=get_random_id())
                            except:
                                try:
                                    деньги_отправляемые, номер_врага = int(
                                        список_крестики_нолики[event.object.from_id][0]), int(
                                        список_крестики_нолики[event.object.from_id][2])

                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id, chat_id_name), получаем_баланс(номер_врага, chat_id_name)

                                    def действие():
                                        игры_крестики_нолики[
                                            event.object.from_id + список_крестики_нолики[event.object.from_id][
                                                1]] = {1: casino.крестик_1, 2: casino.крестик_2, 3: casino.крестик_3,
                                                       4: casino.крестик_4, 5: casino.крестик_5, 6: casino.крестик_6,
                                                       7: casino.крестик_7, 8: casino.крестик_8, 9: casino.крестик_9}, {
                                                          0: номер_врага}
                                        db.get_balance(event.object.from_user, chat_id_name) - деньги_отправляемые
                                        db.get_balance(номер_врага, chat_id_name) - деньги_отправляемые


                                    проверка_ставки(номер_врага, деньги_отправляемые, действие)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{get_last_name(номер_врага)}, Ходите! Номер игры:{event.object.from_id + номер_врага}",
                                                     keyboard=casino.крестики_нолики(casino.карта_крестики_нолики),
                                                     random_id=get_random_id())

                                except:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, не так вызываете на игру",

                                                     random_id=get_random_id())


                        elif config.крестики_нолики_текст in msg:
                            try:

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name},доиграйте с {get_last_name(список_крестики_нолики[event.object.from_id][2])}",
                                                 keyboard=casino.крестики_нолики(casino.карта_крестики_нолики),
                                                 random_id=get_random_id())
                            except:
                                try:
                                    cумма_ставки = msg.replace(config.крестики_нолики_текст, "").strip()

                                    деньги_отправляемые, номер_счёта_получателя = cумма_ставки, int(
                                        event.object.fwd_messages[0]['from_id'])
                                    список_крестики_нолики[int(номер_счёта_получателя)] = int(деньги_отправляемые), int(
                                        event.object.from_id), int(event.object.from_id), False
                                    список_крестики_нолики[int(event.object.from_id)] = int(деньги_отправляемые), int(
                                        номер_счёта_получателя), int(event.object.from_id), True

                                    def действие():
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"[id{номер_счёта_получателя}|{get_last_name(номер_счёта_получателя)} вас вызывает {last_name}]\n Сумма:{деньги_отправляемые}",
                                                         keyboard=buttons.menu_games_x00.get_keyboard(),
                                                         random_id=get_random_id())

                                    проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие)
                                except:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, не так заполнены поля",

                                                     random_id=get_random_id())
                        elif config.банк_пополнить_текст in msg:
                            сумма = msg.replace(config.банк_пополнить_текст, "").strip()

                            def действие():
                                сумма_с_комиссией = round(int(сумма) - ((int(сумма) / 100) * config.комиссия_банка), 1)
                                db.update_balance(event.object.from_id,
                                                  получаем_баланс(event.object.from_id, chat_id_name) - int(сумма),
                                                  chat_id_name)
                                db.update_bank(event.object.from_id,
                                               получаем_банк(event.object.from_id, chat_id_name) + сумма_с_комиссией,
                                               chat_id_name)
                                db.update_time_bank_procent(event.object.from_id,
                                                            (datetime.now()).strftime(time_format),
                                                            chat_id_name)
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}\nПополнил банк:{сумма_с_комиссией}₽\nКомиссия:{buttons.комиссия_банка}%",
                                                 keyboard=buttons.menu.get_keyboard(),
                                                 random_id=get_random_id())

                            проверка_ставки(event.object.from_id, сумма, действие, True)
                        elif config.банк_снять_текст in msg:

                            сумма = msg.replace(config.банк_снять_текст, "").strip()

                            def действие():

                                накапаные = получаем_сколько_накапал_банк(event.object.from_id, chat_id_name)

                                db.update_balance(event.object.from_id,
                                                  получаем_баланс(event.object.from_id, chat_id_name) + int(сумма),
                                                  chat_id_name)
                                db.update_bank(event.object.from_id,
                                               получаем_банк(event.object.from_id, chat_id_name) - int(сумма),
                                               chat_id_name)
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}\nСнял:{сумма}₽\nПроценты:{накапаные}",
                                                 keyboard=buttons.menu.get_keyboard(),
                                                 random_id=get_random_id())

                            проверка_ставки(event.object.from_id, сумма, действие, True, True)
                        elif config.русская_рулетка_текст == msg:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message="Для того, чтобы играть, напишите:Дуэль сумма",
                                             keyboard=buttons.menu_games_x00.get_keyboard(),
                                             random_id=get_random_id())
                        elif config.принять_дуэль_текст == msg:

                            деньги_отправляемые, номер_врага = int(
                                список_дуэль[event.object.from_id][0]), int(
                                список_дуэль[event.object.from_id][1])

                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                event.object.from_id, chat_id_name), получаем_баланс(номер_врага, chat_id_name)

                            def действие():
                                if random < 50:
                                    список_дуэль[event.object.from_id] = 0
                                    db.update_balance(event.object.from_id, int(
                                        int(баланс_отправителя) - int(
                                            деньги_отправляемые)), chat_id_name)
                                    db.update_balance(номер_врага, int(
                                        int(баланс_получателя) + int(деньги_отправляемые)), chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{get_last_name(номер_врага)}, Победил в дуэли! {деньги_отправляемые}₽",
                                                     keyboard=buttons.menu_games.get_keyboard(),
                                                     random_id=get_random_id())
                                else:
                                    db.update_balance(номер_врага,
                                                      int(int(баланс_получателя) - int(
                                                          деньги_отправляемые)), chat_id_name)
                                    db.update_balance(event.object.from_id, int(
                                        int(баланс_отправителя) + int(деньги_отправляемые)), chat_id_name)

                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, Победил в дуэли! {деньги_отправляемые}₽",
                                                     keyboard=buttons.menu_games.get_keyboard(),
                                                     random_id=get_random_id())
                            проверка_ставки(event.object.from_id, сумма, действие)
                    else:
                        vk.messages.send(peer_id=event.object['peer_id'],
                                     message=f"Я не работаю в личных сообщениях, добавь меня в беседу!",
                                     random_id=get_random_id())



        except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError,requests.exceptions.ConnectionError):
            time.sleep(1)
            print('_______Timeout______')

if __name__ == "__main__":
    main()
