
from datetime import datetime, timedelta
from random import randint
import requests
import vk_api
from sqlighter import SQLighter
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import socket
import urllib3
import time
import re
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

token = vk_api.VkApi(token="9054c46ab1a41e7c186228248b386f18edeca458e3992126d34270b262f710be1b180fa2f176dbb51212d")
long = VkLongPoll(token)
vk = token.get_api()

db = SQLighter('user.db')
время_для_бонуса = 5
размер_бонуса = 1000
определённый_баланс = 10000
мин_ставка_от_определённого_баланса = 1000
time_format = "%Y-%m-%d %H:%M"
admin_id = 243793518





menu = VkKeyboard(one_time=False, inline=True)
menu.add_button("Бонус", color="positive")
menu.add_line()
menu.add_button("Баланс", color="positive")
menu.add_line()
menu.add_button("Мой номер", color="positive")
menu.add_line()
menu.add_button("Казино", color=VkKeyboardColor.NEGATIVE)

menu_kazino = VkKeyboard(one_time=False, inline=True)
menu_kazino.add_button("Основное Меню", color=VkKeyboardColor.NEGATIVE)
menu_kazino.add_line()
menu_kazino.add_button("Казино процент 20", color="positive")
menu_kazino.add_line()
menu_kazino.add_button("Казино процент 40", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button("Казино процент 60", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button("Казино процент 80", color=VkKeyboardColor.POSITIVE)
menu_kazino.add_line()
menu_kazino.add_button("Казино процент 100", color=VkKeyboardColor.POSITIVE)


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
        бонус_время = datetime.strptime(время_бонус[0], time_format) + timedelta(hours=3, minutes=1)
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

                if event.type == VkEventType.MESSAGE_NEW:

                    время_на_которое_обновится_бонус = (datetime.now() + timedelta(minutes=время_для_бонуса)).strftime(
                        time_format)

                    random = randint(0, 100)
                    if event.to_me:

                        last_name = str(
                            vk.users.get(user_ids=(str(event.user_id)))[0]['last_name'])  # получение фамилии
                        msg = str(event.text.lower()).replace("[club201483157|@d1slor] ","")

                        if db.subscriber_exists(event.user_id):
                            db.update_firstname(event.user_id, last_name)
                        else:
                            db.add_subscriber(event.user_id)
                            db.update_firstname(event.user_id, last_name)
                        if 'основное меню' == msg:
                            vk.messages.send(peer_id=event.peer_id, message=f"{last_name}, держи основное меню", keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())


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
                            if 'казино' == msg:
                                vk.messages.send(peer_id=event.peer_id, message=f"{last_name}, держи меню казино",
                                                 keyboard=menu_kazino.get_keyboard(),
                                                 random_id=get_random_id())

                            if получаем_баланс(event.user_id) is None:
                                db.update_balance(event.user_id, размер_бонуса)



                            msg = str(msg).replace('казино', '').replace(' ', '')

                            ставочные_деньги = msg

                            def stavka( ставочные_деньги):
                                if int(получаем_баланс(event.user_id)) == 0 or ставочные_деньги == 0:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, нет денег или ставка равна 0",
                                                     random_id=get_random_id())

                                if int(ставочные_деньги) < 25:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, мин ставка 25₽",
                                                     random_id=get_random_id())


                                elif int(получаем_баланс(event.user_id)) > определённый_баланс and int(
                                        ставочные_деньги) < мин_ставка_от_определённого_баланса and int(
                                    ставочные_деньги) < int(получаем_баланс(event.user_id)):
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, мин ставка: {мин_ставка_от_определённого_баланса}",
                                                     random_id=get_random_id())


                                elif int(ставочные_деньги) < int(получаем_баланс(event.user_id)) or int(
                                        ставочные_деньги) == int(получаем_баланс(event.user_id)):

                                    if random < 65:

                                        db.update_balance(event.user_id,
                                                          int(получаем_баланс(event.user_id)) + (int(
                                                              ставочные_деньги) + (int(ставочные_деньги) / 100) * 25))
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name} выиграл:\n {str(получаем_баланс(event.user_id))} ₽",
                                                         random_id=get_random_id())


                                    else:

                                        db.update_balance(event.user_id,
                                                          int(получаем_баланс(event.user_id)) - int(ставочные_деньги))

                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, проиграл: {str(получаем_баланс(event.user_id))}₽",
                                                         random_id=get_random_id())



                                else:
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=last_name + ", у вас нет столько :) ",
                                                     random_id=get_random_id())
                            if isint(ставочные_деньги):
                                stavka(ставочные_деньги)
                            elif "процент" in msg:
                                msg = msg.replace("процент","").replace(" ","")
                                if isint(msg):
                                    процент_от_ставки = (float(получаем_баланс(event.user_id))/100)*float(msg)
                                    stavka(процент_от_ставки)



                        if 'мой номер' == msg:
                            vk.messages.send(peer_id=event.peer_id,
                                             message=last_name + ", ваш номер: " + str(event.user_id),
                                             random_id=get_random_id())
                        if 'выдать' in msg:
                            if event.user_id == admin_id:
                                команда_выдать = str(msg).replace('выдать', '').split()
                                try:
                                    деньги_отправляемые = команда_выдать[1]
                                except:
                                    vk.messages.send(peer_id=event.peer_id,message=f"{last_name} сумма указана не верно",random_id=get_random_id())
                                    
                                try:
                                     номер_счёта_получателя = команда_выдать[0]
                                except:
                                    vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name} счёт получателя был указан неверно",
                                                         random_id=get_random_id())
                                     

                                if isint(номер_счёта_получателя) and isint(деньги_отправляемые):
                                    if db.subscriber_exists(номер_счёта_получателя):
                                        баланс_получателя = получаем_баланс(номер_счёта_получателя)
                                        if баланс_получателя is None:
                                            db.update_balance(event.user_id, размер_бонуса)
                                        db.update_balance(номер_счёта_получателя,
                                                          int(баланс_получателя) + int(деньги_отправляемые))
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, перевёл на " + номер_счёта_получателя + " " + деньги_отправляемые + "₽",
                                                         random_id=get_random_id())

                                    else:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name}, такого счёта нет",
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
                                try:
                                    деньги_отправляемые = команда_перевода[1]
                                except:
                                    vk.messages.send(peer_id=event.peer_id,message=f"{last_name} сумма указана не верно",random_id=get_random_id())
                                    
                                try:
                                     номер_счёта_получателя = команда_перевода[0]
                                except:
                                     vk.messages.send(peer_id=event.peer_id,
                                                         message=f"{last_name} счёт получателя был указан неверно",
                                                         random_id=get_random_id())


                                if isint(номер_счёта_получателя) and isint(деньги_отправляемые):
                                    if db.subscriber_exists(номер_счёта_получателя):

                                        if int(номер_счёта_получателя) != int(event.user_id):
                                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                                event.user_id), получаем_баланс(номер_счёта_получателя)
                                            if баланс_отправителя is None:
                                                db.update_balance(event.user_id, размер_бонуса)
                                            if баланс_получателя is None:
                                                db.update_balance(event.user_id, размер_бонуса)
                                            if баланс_отправителя <= деньги_отправляемые:
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=f"{last_name}, у вас столько денег нет",
                                                                 random_id=get_random_id())
                                            else:
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
                                    db.update_bonus(event.user_id, 0)
                                    db.update_balance(event.user_id, размер_бонуса)

                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=f"{last_name}, первый бонус: 1000",
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
