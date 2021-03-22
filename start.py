from datetime import datetime, timedelta
from random import randint
from threading import Thread
import requests
import vk_api
from sqlighter import SQLighter
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import socket
import urllib3
import time
import os

token = vk_api.VkApi(token=str(os.environ.get('BOT_TOKEN')))
long = VkLongPoll(token)
vk = token.get_api()

db = SQLighter('user.db')
время_для_бонуса = 5
размер_бонуса = 1000
определённый_баланс = 10000
мин_ставка_от_определённого_баланса = 1000
time_format = "%Y-%m-%d %H:%M"

def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def получаем_баланс(user_id):
    for баланс in db.get_balance(user_id):
        return баланс[0]

def бонус_по_мск(user_id):
    for время_бонус in db.get_time_bonus(user_id):
        бонус_время = datetime.strptime(время_бонус[0], time_format)+timedelta(hours = 5,minutes = 1)
        return бонус_время
def получаем_время_когда_будет_бонус(user_id):
    for время_бонус in db.get_time_bonus(user_id):
        бонус_время = (datetime.strptime(время_бонус[0], time_format)).strftime(time_format)
        return бонус_время


def bonus(user_id):
    сейчас_время = (datetime.now()).strftime(time_format)

    if получаем_время_когда_будет_бонус(user_id) < сейчас_время:
        db.update_time_bonus(user_id, datetime.now() + timedelta(minutes=время_для_бонуса))
        db.update_bonus(user_id, 1)
        return True
    return False


def получаем_сколько_бонусов_юзера(user_id):
    for бонус in db.get_bonus(user_id):
        return бонус[0]


def main():
    while True:
        try:
            for event in long.listen():

                время_на_которое_обновится_бонус = (datetime.now() + timedelta(minutes=время_для_бонуса)).strftime(
                    time_format)

                if event.type == VkEventType.MESSAGE_NEW:
                    random = randint(0, 100)
                    if event.to_me:

                        last_name = str(
                            vk.users.get(user_ids=(str(event.user_id)))[0]['last_name'])  # получение фамилии
                        msg = event.text.lower()

                        if db.subscriber_exists(event.user_id):
                            db.update_firstname(event.user_id, last_name)
                        else:
                            db.add_subscriber(event.user_id)
                            db.update_firstname(event.user_id, last_name)

                        if 'баланс' == msg:

                            if получаем_баланс(event.user_id) is None:
                                db.update_balance(event.user_id, размер_бонуса)

                            if int(получаем_баланс(event.user_id)) == 0:
                                vk.messages.send(peer_id=event.peer_id, message=f"{last_name}, нет денег(",
                                                 random_id=get_random_id())
                            else:
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=f"{last_name}, ваш баланс: " + str(
                                                     получаем_баланс(event.user_id)) + "₽",
                                                 random_id=get_random_id())
                        if 'казино' in msg:
                            msg = str(msg).replace('казино', '').replace(' ', '')
                            if "все" == str(msg) or "всё" == str(msg):
                                if получаем_баланс(event.user_id) is None:
                                    db.update_balance(event.user_id, размер_бонуса)
                                    ставочные_деньги = размер_бонуса
                                else:
                                    ставочные_деньги = получаем_баланс(event.user_id)

                            else:
                                ставочные_деньги = msg

                            if isint(ставочные_деньги):

                                if получаем_баланс(event.user_id) is None:
                                    db.update_balance(event.user_id, размер_бонуса)

                                if int(получаем_баланс(event.user_id)) == 0 or ставочные_деньги == 0:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, нет денег или ставка равна 0",
                                                     random_id=get_random_id())

                                elif int(ставочные_деньги) < 50:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, ставка меньше 50₽",
                                                     random_id=get_random_id())


                                elif int(получаем_баланс(event.user_id)) > определённый_баланс and int(
                                        ставочные_деньги) < мин_ставка_от_определённого_баланса and int(
                                    ставочные_деньги) < int(получаем_баланс(event.user_id)):
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, мин ставка: {мин_ставка_от_определённого_баланса}",
                                                     random_id=get_random_id())


                                elif int(ставочные_деньги) < int(получаем_баланс(event.user_id)) or int(
                                        ставочные_деньги) == int(получаем_баланс(event.user_id)):

                                    if random > 40:

                                        db.update_balance(event.user_id,
                                                          int(получаем_баланс(event.user_id)) + (int(
                                                              ставочные_деньги) + (int(ставочные_деньги) / 100) * 25))
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name} выиграл: {str(получаем_баланс(event.user_id))} ₽ .",
                                                         random_id=get_random_id())


                                    else:

                                        db.update_balance(event.user_id,
                                                          int(получаем_баланс(event.user_id)) - int(ставочные_деньги))

                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, проиграл: {str(получаем_баланс(event.user_id))}₽ .",
                                                         random_id=get_random_id())



                                else:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=last_name + ", у вас нет столько :) ",
                                                     random_id=get_random_id())

                        if 'мой номер' == msg:
                            vk.messages.send(peer_id=event.peer_id,
                                             message=last_name + ", ваш номер: " + str(event.user_id),
                                             random_id=get_random_id())
                        if 'перевести' in msg:

                            if 'перевести все' in msg:
                                номер_счёта_получателя = str(msg).replace('перевести все', '').replace(" ", "")
                                if isint(номер_счёта_получателя):
                                    деньги_отправляемые = получаем_баланс(event.user_id)
                                    if db.subscriber_exists(номер_счёта_получателя):
                                        if деньги_отправляемые is None:
                                            db.update_balance(event.user_id, размер_бонуса)
                                        if int(номер_счёта_получателя) != int(event.user_id):
                                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                                event.user_id), получаем_баланс(номер_счёта_получателя)
                                            db.update_balance(event.user_id,
                                                              int(баланс_отправителя) - int(деньги_отправляемые))
                                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                                event.user_id), получаем_баланс(номер_счёта_получателя)
                                            db.update_balance(номер_счёта_получателя,
                                                              int(баланс_получателя) + int(деньги_отправляемые))
                                            vk.messages.send(peer_id=event.peer_id,
                                                             message=f"{last_name}, перевёл на {str(номер_счёта_получателя)} {str(деньги_отправляемые)} ₽",
                                                             random_id=get_random_id())
                                        else:
                                            vk.messages.send(peer_id=event.peer_id,
                                                             message=f"{last_name}, нельзя переводить себе",
                                                             random_id=get_random_id())
                                    else:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, такого счёта нет",
                                                         random_id=get_random_id())


                            else:
                                команда_перевода = str(msg).replace('перевести', '').split()
                                деньги_отправляемые, номер_счёта_получателя = команда_перевода[1], команда_перевода[0]

                                if isint(номер_счёта_получателя) and isint(деньги_отправляемые):
                                    if db.subscriber_exists(номер_счёта_получателя):
                                        if int(номер_счёта_получателя) != int(event.user_id):
                                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                                event.user_id), получаем_баланс(номер_счёта_получателя)
                                            db.update_balance(event.user_id,
                                                              int(баланс_отправителя) - int(деньги_отправляемые))
                                            db.update_balance(номер_счёта_получателя,
                                                              int(баланс_получателя) + int(деньги_отправляемые))
                                            vk.messages.send(peer_id=event.peer_id,
                                                             message=f"{last_name}, перевёл на " + номер_счёта_получателя + " " + деньги_отправляемые + "₽",
                                                             random_id=get_random_id())
                                    else:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, такого счёта нет",
                                                         random_id=get_random_id())

                        if 'бонус' == msg:
                            if получаем_баланс(event.user_id) is None or int(получаем_баланс(event.user_id)) == 0:

                                if получаем_сколько_бонусов_юзера(event.user_id) is None:
                                    db.update_time_bonus(event.user_id, время_на_которое_обновится_бонус)

                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, первый бонус: {бонус_по_мск(event.user_id)}",
                                                     random_id=get_random_id())

                                elif получаем_сколько_бонусов_юзера(event.user_id) == 0:

                                    if bonus(event.user_id) is not True:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name} , бонус след: {бонус_по_мск(event.user_id)}",
                                                         random_id=get_random_id())

                                if получаем_сколько_бонусов_юзера(event.user_id) == 1:
                                    db.update_bonus(event.user_id, 0)
                                    db.update_balance(event.user_id, размер_бонуса)
                                    db.update_time_bonus(event.user_id, время_на_которое_обновится_бонус)
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, бонус: {размер_бонуса}",
                                                     random_id=get_random_id())

                            else:
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=f"{last_name},вы не можете получить бонус",
                                                 random_id=get_random_id())







        except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError):
            time.sleep(1)
            print('_______Timeout______')


if __name__ == "__main__":
    main()
