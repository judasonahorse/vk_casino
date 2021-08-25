from datetime import datetime, timedelta
from random import randint
import requests
import vk_api
from sqlighter import SQLighter
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
import socket
import urllib3
import time
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import config
import math

vk_session = vk_api.VkApi(token=config.BotToken)  # Обработка access_token
longpoll = VkBotLongPoll(vk_session, config.group_id)  # Данные для работы в сообществе
vk = vk_session.get_api()  # Работа с VK API

db = SQLighter('user.db')

time_format = "%Y-%m-%d %H:%M:%S"
список_дуэль = {'id': 'value'}
список_крестики_нолики = {'id': 'value'}
игры_крестики_нолики = {}

банк_снять_текст = "банк снять"
банк_пополнить_текст = "банк пополнить"
основное_меню_текст = "основное меню"
бонус_текст = "бонус"
баланс_текст = "баланс"
дуэль_текст = "дуэль"
принять_дуэль_текст = "дуэль принять"
топ_текст = "топ"
казино_текст = "казино"
крестики_нолики_принять_текст = "принять крестики нолики"
игры_текст = "игры"
русская_рулетка_текст = "русская рулетка"
перевести_текст = "перевести"
крестики_нолики_текст = "кр"
комиссия_банка = 20
проценты_банк = 0.05
menu_top = VkKeyboard(one_time=False, inline=True)
menu_top.add_button(основное_меню_текст, color=VkKeyboardColor.NEGATIVE)

menu = VkKeyboard(one_time=False, inline=True)
menu.add_button(бонус_текст, color=VkKeyboardColor.POSITIVE)
menu.add_button(баланс_текст, color=VkKeyboardColor.POSITIVE)
menu.add_line()
menu.add_button(топ_текст, color=VkKeyboardColor.POSITIVE)
menu.add_button(игры_текст, color=VkKeyboardColor.NEGATIVE)

menu_games = VkKeyboard(one_time=False, inline=True)
menu_games.add_button(казино_текст, color=VkKeyboardColor.NEGATIVE)
menu_games.add_line()
menu_games.add_button(русская_рулетка_текст, color=VkKeyboardColor.NEGATIVE)

menu_ruletka = VkKeyboard(one_time=False, inline=True)
menu_ruletka.add_button(основное_меню_текст, color=VkKeyboardColor.NEGATIVE)
menu_ruletka.add_line()
menu_ruletka.add_button(принять_дуэль_текст, color=VkKeyboardColor.POSITIVE)

menu_kazino = VkKeyboard(one_time=False, inline=True)
menu_kazino.add_button(основное_меню_текст, color=VkKeyboardColor.NEGATIVE)
menu_kazino.add_line()
menu_kazino.add_button(f"{казино_текст} процент 20", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button(f"{казино_текст} процент 40", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button(f"{казино_текст} процент 60", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button(f"{казино_текст} процент 80", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button(f"{казино_текст} процент 100", color=VkKeyboardColor.POSITIVE)

menu_games_x00 = VkKeyboard(one_time=False, inline=True)
menu_games_x00.add_button(крестики_нолики_принять_текст, color=VkKeyboardColor.NEGATIVE)

крестик_1 = "1️⃣"
крестик_2 = "2⃣"
крестик_3 = "3⃣"
крестик_4 = "4⃣"
крестик_5 = "5⃣"
крестик_6 = "6⃣"
крестик_7 = "7⃣"
крестик_8 = "8⃣"
крестик_9 = "9⃣"
карта_крестики_нолики = {1: крестик_1, 2: крестик_2, 3: крестик_3, 4: крестик_4, 5: крестик_5, 6: крестик_6,
                         7: крестик_7, 8: крестик_8, 9: крестик_9}


def крестики_нолики(карта_крестики_нолики):
    menu_games_x0 = VkKeyboard(one_time=False, inline=True)
    menu_games_x0.add_button(карта_крестики_нолики[1], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[2], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[3], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_line()
    menu_games_x0.add_button(карта_крестики_нолики[4], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[5], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[6], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_line()
    menu_games_x0.add_button(карта_крестики_нолики[7], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[8], color=VkKeyboardColor.POSITIVE)
    menu_games_x0.add_button(карта_крестики_нолики[9], color=VkKeyboardColor.POSITIVE)
    return menu_games_x0.get_keyboard()


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
                    (получаем_банк(id, chat_id_name) / 100) * (проценты_банк * сколько_прошло_после_вклада)), 1)
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
                        db.create_table_for_game(game_id_name)
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
                                                         keyboard=menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(деньги_отправляемые) < 0 or int(деньги_отправляемые) == 0:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, жулик нельзя переводить меньше 0 или 0",
                                                         keyboard=menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(баланс_отправителя) < int(деньги_отправляемые) and исключение2 == False:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, у вас столько денег нет",
                                                         keyboard=menu.get_keyboard(),
                                                         random_id=get_random_id())
                                    elif int(деньги_отправляемые) > int(
                                            получаем_банк(event.object.from_id, chat_id_name)) and исключение2 == True:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, у вас столько денег нет",
                                                         keyboard=menu.get_keyboard(),
                                                         random_id=get_random_id())


                                    else:
                                        действие()

                                else:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, нельзя переводить себе",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())


                            else:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, такого счёта нет",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())

                        if msg == крестик_1 or msg == крестик_2 or msg == крестик_3 or msg == крестик_4 or msg == крестик_5 or msg == крестик_6 or msg == крестик_7 or msg == крестик_8 or msg == крестик_9:
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
                                    if игра[1] != крестик_1 and игра[2] != крестик_2  and игра[3] != крестик_3  and игра[4] != крестик_4 and игра[5] != крестик_5  and игра[6] != крестик_6 and игра[7] != крестик_7 and игра[8] != крестик_8 and игра[9] != крестик_9:
                                        return True
                                    False


                                def кто_выйграл2(игра):
                                    if ничья( игры_крестики_нолики[event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]) is True:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"Ничья!",
                                                         keyboard=крестики_нолики(карта_крестики_нолики),
                                                         random_id=get_random_id())
                                        return True



                                    elif кто_выйграл(крестик, игры_крестики_нолики[event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]) is True:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{last_name}, Победил! {деньги_отправляемые}₽",
                                                         keyboard=крестики_нолики(карта_крестики_нолики),
                                                         random_id=get_random_id())
                                        return True


                                    elif кто_выйграл(нолик, игры_крестики_нолики[event.object.from_id + список_крестики_нолики[event.object.from_id][1]][0]) is True:
                                        vk.messages.send(peer_id=event.object['peer_id'],
                                                         message=f"{список_крестики_нолики[event.object.from_id][1]}, Победил! {деньги_отправляемые}₽",
                                                         keyboard=крестики_нолики(карта_крестики_нолики),
                                                         random_id=get_random_id())

                                        return True

                                    return False

                                def обнуление_игры():
                                    игрок = список_крестики_нолики[event.object.from_id][1]



                                    print(1)
                                    игры_крестики_нолики[event.object.from_id + список_крестики_нолики[event.object.from_id][1]] = 0

                                    print( игры_крестики_нолики[event.object.from_id + список_крестики_нолики[event.object.from_id][1]])
                                    список_крестики_нолики[игрок] = 0
                                    print(3)
                                    список_крестики_нолики[event.object.from_id] = 0
                                    print(4)

                                if event.object.from_id == игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]][1][0]:
                                    if список_крестики_нолики[event.object.from_id][3] is True:

                                        игра[номер_ячейки] = крестик

                                        if not кто_выйграл2(игры_крестики_нолики[event.object.from_id +
                                                                                 список_крестики_нолики[
                                                                                     event.object.from_id][1]]):
                                            игры_крестики_нолики[
                                                event.object.from_id + список_крестики_нолики[event.object.from_id][1]][
                                                1][0]= список_крестики_нолики[event.object.from_id][1]
                                            vk.messages.send(peer_id=event.object['peer_id'],
                                                             message=f"{get_last_name(список_крестики_нолики[event.object.from_id][1])},Ходите! {деньги_отправляемые}₽",
                                                             keyboard=крестики_нолики(карта_крестики_нолики),
                                                             random_id=get_random_id())

                                        else:
                                            обнуление_игры()
                                    elif список_крестики_нолики[event.object.from_id][3] is False:

                                        игра[номер_ячейки] = нолик
                                        if not кто_выйграл2(игры_крестики_нолики[event.object.from_id +
                                                                                 список_крестики_нолики[
                                                                                     event.object.from_id][1]]):
                                            игры_крестики_нолики[
                                                event.object.from_id + список_крестики_нолики[event.object.from_id][1]][
                                                1][0]= список_крестики_нолики[event.object.from_id][1]
                                            vk.messages.send(peer_id=event.object['peer_id'],
                                                             message=f"{get_last_name(список_крестики_нолики[event.object.from_id][1])},Ходите!",
                                                             keyboard=крестики_нолики(карта_крестики_нолики),
                                                             random_id=get_random_id())
                                        else:
                                            обнуление_игры()
                                else:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name},не ваш ход!",
                                                     keyboard=крестики_нолики(карта_крестики_нолики),
                                                     random_id=get_random_id())
                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, Игры такой нет",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())






                    if крестики_нолики_принять_текст == msg:
                        try:

                            деньги_отправляемые, номер_врага = int(
                                список_крестики_нолики[event.object.from_id][0]), int(
                                список_крестики_нолики[event.object.from_id][2])

                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                event.object.from_id, chat_id_name), получаем_баланс(номер_врага, chat_id_name)

                            def действие():
                                карта_крестики_нолики_to =  {1: крестик_1, 2: крестик_2, 3: крестик_3, 4: крестик_4, 5: крестик_5, 6: крестик_6,
                         7: крестик_7, 8: крестик_8, 9: крестик_9}
                                игры_крестики_нолики[
                                    event.object.from_id + список_крестики_нолики[event.object.from_id][1]] =карта_крестики_нолики_to,{0: номер_врага}

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{get_last_name(номер_врага)}, Ходите! Номер:{event.object.from_id + номер_врага}",
                                                 keyboard=крестики_нолики(карта_крестики_нолики),
                                                 random_id=get_random_id())

                            проверка_ставки(номер_врага, деньги_отправляемые, действие)
                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name}, Не ломай!",
                                             random_id=get_random_id())





                    elif крестики_нолики_текст in msg:
                        try:
                            cумма_ставки = msg.replace(крестики_нолики_текст, "").strip()

                            деньги_отправляемые, номер_счёта_получателя = cумма_ставки, int(
                                event.object.fwd_messages[0]['from_id'])

                            список_крестики_нолики[int(номер_счёта_получателя)] = int(деньги_отправляемые), int(
                                event.object.from_id), int(event.object.from_id), False
                            список_крестики_нолики[int(event.object.from_id)] = int(деньги_отправляемые), int(
                                номер_счёта_получателя), int(event.object.from_id), True

                            def действие():
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"[id{номер_счёта_получателя}|{get_last_name(номер_счёта_получателя)} вас вызывает {last_name}]\n Сумма:{деньги_отправляемые}",
                                                 keyboard=menu_games_x00.get_keyboard(),
                                                 random_id=get_random_id())

                            проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие)
                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"[{last_name}, иди нахуй не ломай бота",
                                             keyboard=menu_games_x00.get_keyboard(),
                                             random_id=get_random_id())



                    elif банк_пополнить_текст in msg:

                        сумма = msg.replace(банк_пополнить_текст, "").strip()

                        def действие():
                            сумма_с_комиссией = round(int(сумма) - ((int(сумма) / 100) * комиссия_банка), 1)
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
                                             message=f"{last_name}\nПополнил банк:{сумма_с_комиссией}₽\nКомиссия:{комиссия_банка}%",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())

                        проверка_ставки(event.object.from_id, сумма, действие, True)
                    elif банк_снять_текст in msg:

                        сумма = msg.replace(банк_снять_текст, "").strip()

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
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())

                        проверка_ставки(event.object.from_id, сумма, действие, True, True)

                    elif русская_рулетка_текст == msg:
                        vk.messages.send(peer_id=event.object['peer_id'],
                                         message="Для того, чтобы играть, напишите:Дуэль сумма",
                                         keyboard=menu_games.get_keyboard(),
                                         random_id=get_random_id())
                    elif принять_дуэль_текст == msg:
                        try:
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
                                                     keyboard=menu_games.get_keyboard(),
                                                     random_id=get_random_id())
                                else:
                                    db.update_balance(номер_врага,
                                                      int(int(баланс_получателя) - int(
                                                          деньги_отправляемые)), chat_id_name)
                                    db.update_balance(event.object.from_id, int(
                                        int(баланс_отправителя) + int(деньги_отправляемые)), chat_id_name)

                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, Победил в дуэли! {деньги_отправляемые}₽",
                                                     keyboard=menu_games.get_keyboard(),
                                                     random_id=get_random_id())

                            проверка_ставки(номер_врага, деньги_отправляемые, действие)








                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name}, игра не найдена",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                    elif дуэль_текст in msg:
                        try:
                            cумма_ставки = msg.replace(дуэль_текст, "").split()
                            деньги_отправляемые, номер_счёта_получателя = cумма_ставки[0], int(
                                event.object.fwd_messages[0]['from_id'])

                            def действие():
                                список_дуэль[int(номер_счёта_получателя)] = int(деньги_отправляемые), int(
                                    event.object.from_id)

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"[id{номер_счёта_получателя}|{get_last_name(номер_счёта_получателя)} вас вызывает {last_name}]\n Сумма:{деньги_отправляемые}",
                                                 keyboard=menu_ruletka.get_keyboard(),
                                                 random_id=get_random_id())

                            проверка_ставки(номер_счёта_получателя, cумма_ставки[0], действие)
                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name} сумма ставки неверна",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())


                    elif основное_меню_текст == msg:
                        vk.messages.send(peer_id=event.object['peer_id'], message=основное_меню_текст,
                                         keyboard=menu.get_keyboard(),
                                         random_id=get_random_id()
                                         )
                    elif игры_текст == msg:
                        vk.messages.send(peer_id=event.object['peer_id'], message=игры_текст,
                                         keyboard=menu_games.get_keyboard(),
                                         random_id=get_random_id())
                    elif баланс_текст == msg:

                        if получаем_баланс(event.object.from_id, chat_id_name) is None:
                            db.update_balance(event.object.from_id, config.размер_бонуса, chat_id_name)

                        if int(получаем_баланс(event.object.from_id, chat_id_name)) == 0 and int(
                                получаем_банк(event.object.from_id, chat_id_name)) == 0:
                            vk.messages.send(peer_id=event.object['peer_id'], message=f"{last_name}, нет денег(",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                        else:
                            рейтинг_гетаем = рейтинг()
                            проценты = получаем_сколько_накапал_банк(event.object.from_id, chat_id_name)

                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name}\nБаланс: {получаем_баланс(event.object.from_id, chat_id_name)}₽\nВаш Банк:{получаем_банк(event.object.from_id, chat_id_name)}₽\nПроценты:{проценты}₽\nМиллионы: {рейтинг_гетаем}",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                    elif казино_текст in msg:

                        if казино_текст == msg or "казино" == msg:
                            vk.messages.send(peer_id=event.object['peer_id'], message=казино_текст,
                                             keyboard=menu_kazino.get_keyboard(),
                                             random_id=get_random_id())

                        if получаем_баланс(event.object.from_id, chat_id_name) is None:
                            db.update_balance(event.object.from_id, config.размер_бонуса, chat_id_name)

                        ставочные_деньги = msg = msg.replace('казино', '')

                        def play(ставочные_деньги):
                            if int(получаем_баланс(event.object.from_id,
                                                   chat_id_name)) == 0 or ставочные_деньги == 0:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, нет денег или ставка равна 0",
                                                 random_id=get_random_id())

                            elif int(ставочные_деньги) < 25:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, мин ставка 25₽",
                                                 random_id=get_random_id())


                            elif int(получаем_баланс(event.object.from_id,
                                                     chat_id_name)) > config.определённый_баланс and int(
                                ставочные_деньги) < config.мин_ставка_от_определённого_баланса and int(
                                ставочные_деньги) < int(получаем_баланс(event.object.from_id, chat_id_name)):
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, мин ставка: {config.мин_ставка_от_определённого_баланса}",
                                                 random_id=get_random_id())


                            elif int(ставочные_деньги) < int(
                                    получаем_баланс(event.object.from_id, chat_id_name)) or int(
                                ставочные_деньги) == int(получаем_баланс(event.object.from_id, chat_id_name)):
                                итоги_ставки_отправлены = False

                                def шанс_и_значения(шанс, коэф, шанс_проигрышный, итоги_ставки_отправлены):

                                    if random < шанс and итоги_ставки_отправлены is False:
                                        def message(выйгрышь_или_проигрышь):
                                            рейтинг_гетаем = рейтинг()
                                            vk.messages.send(peer_id=event.object['peer_id'],
                                                             message=f"{last_name} {выйгрышь_или_проигрышь} x{коэф}:\nБаланс:{str(получаем_баланс(event.object.from_id, chat_id_name))} ₽\nМиллионы:{рейтинг_гетаем}",
                                                             keyboard=menu_kazino.get_keyboard(),
                                                             random_id=get_random_id())

                                        if шанс > шанс_проигрышный:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,
                                                                                  chat_id_name)) + (int(float(
                                                                  int(ставочные_деньги) * коэф)) - int(
                                                                  ставочные_деньги)), chat_id_name)

                                            message("выйграл")
                                            return True


                                        elif random == 0:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,
                                                                                  chat_id_name)) - int(
                                                                  ставочные_деньги), chat_id_name)
                                            message("проиграл")
                                            return True

                                        else:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,
                                                                                  chat_id_name)) - ((
                                                                      int(ставочные_деньги) - (
                                                                  int(float(int(ставочные_деньги) * коэф))))),
                                                              chat_id_name)
                                            message("проиграл")
                                            return True
                                        return False

                                if шанс_и_значения(5, 0, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(20, 0.5, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(66, 1.1, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(80, 1.5, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(97, 2, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(99, 5, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True
                                elif шанс_и_значения(100, 10, 65, итоги_ставки_отправлены):
                                    итоги_ставки_отправлены = True

                            else:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=last_name + ", у вас нет столько :) ",
                                                 random_id=get_random_id())

                        if isint(ставочные_деньги):
                            play(ставочные_деньги)
                        elif "процент" in msg:
                            msg = msg.replace("процент", "").replace(" ", "")
                            if isint(msg):
                                процент_от_ставки = int(float(
                                    (float(получаем_баланс(event.object.from_id, chat_id_name)) / 100) * float(
                                        msg)))
                                play(процент_от_ставки)
                    elif перевести_текст in msg:
                        if f'{перевести_текст} всё' in msg:

                            try:
                                номер_счёта_получателя = int(
                                    event.object.fwd_messages[0]['from_id'])
                                деньги_отправляемые = получаем_баланс(event.object.from_id, chat_id_name)

                                def действие():
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id, chat_id_name), получаем_баланс(номер_счёта_получателя,
                                                                                             chat_id_name)
                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) - int(деньги_отправляемые),
                                                      chat_id_name)
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id, chat_id_name), получаем_баланс(номер_счёта_получателя,
                                                                                             chat_id_name)
                                    db.update_balance(номер_счёта_получателя,
                                                      int(баланс_получателя) + int(деньги_отправляемые),
                                                      chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, перевёл на {get_last_name(номер_счёта_получателя)} {str(деньги_отправляемые)} ₽",
                                                     random_id=get_random_id())

                                проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие, False)
                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name} сумма или счёт указаны неверно ",
                                                 random_id=get_random_id())
                        else:
                            сумма_перевода = str(msg).replace(перевести_текст, '').split()
                            try:
                                деньги_отправляемые, номер_счёта_получателя = сумма_перевода[0], int(
                                    event.object.fwd_messages[0]['from_id'])

                                def действие():
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id, chat_id_name), получаем_баланс(номер_счёта_получателя,
                                                                                             chat_id_name)

                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) - int(деньги_отправляемые),
                                                      chat_id_name)
                                    db.update_balance(номер_счёта_получателя,
                                                      int(баланс_получателя) + int(деньги_отправляемые),
                                                      chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, перевёл на {get_last_name(номер_счёта_получателя)} {деньги_отправляемые}₽",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())

                                проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие)

                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name} сумма или счёт указаны неверно ",
                                                 random_id=get_random_id())
                    elif бонус_текст == msg:
                        if получаем_баланс(event.object.from_id, chat_id_name) is None or int(
                                получаем_баланс(event.object.from_id, chat_id_name)) < 25 and получаем_банк(
                            event.object.from_id, chat_id_name) == 0:
                            время_на_которое_обновится_бонус = (
                                    datetime.now() + timedelta(minutes=config.время_для_бонуса)).strftime(
                                time_format)
                            if получаем_сколько_бонусов_юзера(event.object.from_id, chat_id_name) is None:
                                db.update_time_bonus(event.object.from_id, время_на_которое_обновится_бонус,
                                                     chat_id_name)
                                db.update_bonus(event.object.from_id, 0, chat_id_name)
                                db.update_balance(event.object.from_id, config.первый_бонус, chat_id_name)

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}\nПервый Бонус: {config.первый_бонус}",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())

                            elif получаем_сколько_бонусов_юзера(event.object.from_id, chat_id_name) == 0:

                                if bonus(event.object.from_id, chat_id_name) is not True:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name} , бонус след: {бонус_по_мск(event.object.from_id, chat_id_name)}",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())

                            elif получаем_сколько_бонусов_юзера(event.object.from_id, chat_id_name) == 1:
                                db.update_bonus(event.object.from_id, 0, chat_id_name)
                                db.update_balance(event.object.from_id, config.размер_бонуса, chat_id_name)
                                db.update_time_bonus(event.object.from_id, время_на_которое_обновится_бонус,
                                                     chat_id_name)
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}\nБонус: {config.размер_бонуса}",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())

                        else:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name},вы не можете получить бонус",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                    elif топ_текст == msg:
                        vk.messages.send(peer_id=event.object['peer_id'],
                                         message=f"👑 ТОП ОБЩИЙ 👑{получаем_топ_общий(chat_id_name)}",
                                         keyboard=menu_top.get_keyboard(),
                                         random_id=get_random_id())
                else:
                    vk.messages.send(peer_id=event.object['peer_id'],
                                     message=f"Я не работаю в личных сообщениях, добавь меня в беседу!",
                                     random_id=get_random_id())


        except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError,requests.exceptions.ConnectionError):
            time.sleep(1)
            print('_______Timeout______')


if __name__ == "__main__":
    main()
