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

vk_session = vk_api.VkApi(token=config.BotToken)  # Обработка access_token
longpoll = VkBotLongPoll(vk_session, config.group_id)  # Данные для работы в сообществе
vk = vk_session.get_api()  # Работа с VK API

db = SQLighter('user.db')

time_format = "%Y-%m-%d %H:%M"
список_дуэль = {'id': 'value'}

основное_меню_текст = "🏠основное меню🏠"
бонус_текст = "🎁бонус🎁"
баланс_текст = "💰баланс💰"

топ_текст = "👑топ👑"
казино_текст = "🎰казино🎰"
игры_текст = "🎉игры🎉"
русская_рулетка_текст = "🔫русская рулетка🔫"
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
menu_ruletka.add_button("принять дуэль", color=VkKeyboardColor.POSITIVE)

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

        if top[3] != None and top[3] != 0:
            i = i + 1
            if i > 5:
                break

            top_list = top_list + "\n" + f"{i}. {top[2]}\n    Баланс:{top[3]}₽\n    Рейтинг:{top[6]}"
    return top_list


def получаем_баланс(user_id,chat_id_name):
    for баланс in db.get_balance(user_id,chat_id_name):
        return баланс[0]


def бонус_по_мск(user_id,chat_id_name):
    for время_бонус in db.get_time_bonus(user_id,chat_id_name):
        бонус_время = datetime.strptime(время_бонус[0], time_format) + timedelta(hours=3, minutes=1)
        return бонус_время


def получаем_время_когда_будет_бонус(user_id,chat_id_name):
    for время_бонус in db.get_time_bonus(user_id,chat_id_name):
        бонус_время = (datetime.strptime(время_бонус[0], time_format)).strftime(time_format)
        return бонус_время


def bonus(user_id,chat_id_name):
    сейчас_время = (datetime.now()).strftime(time_format)

    if получаем_время_когда_будет_бонус(user_id,chat_id_name) < сейчас_время:
        db.update_time_bonus(user_id, datetime.now() + timedelta(minutes=config.время_для_бонуса),chat_id_name)
        db.update_bonus(user_id, 1,chat_id_name)
        return True
    return False


def получаем_сколько_бонусов_юзера(user_id,chat_id_name):
    for бонус in db.get_bonus(user_id,chat_id_name):
        return бонус[0]


def get_last_name(user_id):
    return str(vk.users.get(user_ids=(str(user_id)))[0]['last_name'])  # получение фамилииmsg


def получаем_медали(user_id,chat_id_name):
    for медаль in db.get_medal(user_id,chat_id_name):
        return медаль[0]


def main():

    while True:

        try:

            for event in longpoll.listen():
                random = randint(0, 100)
                if event.type == VkBotEventType.MESSAGE_NEW:
                    chat_id_name = f"id{event.object['peer_id']}id"
                    db.create_table_for_char(chat_id_name)
                    last_name = get_last_name(event.object.from_id)

                    msg = str(event.object['text'].lower()).replace("[club201483157|@d1slor] ", "")

                    if not db.subscriber_exists(event.object.from_id,chat_id_name):
                        db.add_subscriber(event.object.from_id,chat_id_name)
                        db.update_firstname(event.object.from_id, last_name,chat_id_name)


                    def рейтинг():
                        медали = получаем_медали(event.object.from_id,chat_id_name)
                        if получаем_баланс(event.object.from_id,chat_id_name) != None:
                            if получаем_баланс(event.object.from_id,chat_id_name) > 1000000000:
                                на_сколько_повысился = медали + (
                                        получаем_баланс(event.object.from_id,chat_id_name) / 1000000000)
                                db.update_medal(event.object.from_id, на_сколько_повысился,chat_id_name)
                                db.update_balance(event.object.from_id, 5000,chat_id_name)
                                return на_сколько_повысился
                        return медали

                    def проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие):
                        if db.subscriber_exists(номер_счёта_получателя,chat_id_name):

                            if int(номер_счёта_получателя) != int(event.object.from_id):
                                баланс_отправителя, баланс_получателя = получаем_баланс(
                                    event.object.from_id,chat_id_name), получаем_баланс(номер_счёта_получателя,chat_id_name)
                                if баланс_отправителя is None:
                                    db.update_balance(event.object.from_id, config.размер_бонуса,chat_id_name)
                                elif баланс_получателя is None:
                                    db.update_balance(номер_счёта_получателя, config.размер_бонуса,chat_id_name)
                                elif int(деньги_отправляемые) < 0 or int(деньги_отправляемые) == 0:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, жулик нельзя переводить меньше 0 или 0",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())
                                elif int(баланс_отправителя) < int(деньги_отправляемые) or int(
                                        баланс_получателя) < int(деньги_отправляемые):
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

                    if русская_рулетка_текст == msg or "русская рулетка" == msg:
                        vk.messages.send(peer_id=event.object['peer_id'],
                                         message="Для того, чтобы играть, напишите: Вызвать на Дуэль сумма",
                                         keyboard=menu_games.get_keyboard(),
                                         random_id=get_random_id())
                    if "вызвать на дуэль" in msg:
                        try:
                            сумма_ставки = msg.replace("вызвать на дуэль", "").split()
                            деньги_отправляемые, номер_счёта_получателя = сумма_ставки[0], int(
                                event.object.fwd_messages[0]['from_id'])

                            def действие():
                                список_дуэль[int(номер_счёта_получателя)] = int(деньги_отправляемые), int(
                                    event.object.from_id)

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"[id{номер_счёта_получателя}|{get_last_name(номер_счёта_получателя)} вас вызывает {last_name}] на дуэль \n Сумма:{деньги_отправляемые}",
                                                 keyboard=menu_ruletka.get_keyboard(),
                                                 random_id=get_random_id())

                            проверка_ставки(номер_счёта_получателя, сумма_ставки[0], действие)
                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name} ставка введена неверно",
                                             keyboard=menu_ruletka.get_keyboard(),
                                             random_id=get_random_id())

                    if "принять дуэль" == msg:
                        try:
                            деньги_отправляемые, номер_врага = int(
                                список_дуэль[event.object.from_id][0]), int(
                                список_дуэль[event.object.from_id][1])
                            список_дуэль[event.object.from_id] = 0
                            баланс_отправителя, баланс_получателя = получаем_баланс(
                                event.object.from_id,chat_id_name), получаем_баланс(номер_врага,chat_id_name)

                            def действие():
                                if random < 50:
                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) - int(
                                                          деньги_отправляемые),chat_id_name)
                                    db.update_balance(номер_врага,
                                                      int(баланс_получателя) + int(деньги_отправляемые),chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{get_last_name(номер_врага)}, Победил в дуэли! {event.object.from_id} {деньги_отправляемые}₽",
                                                     keyboard=menu_games.get_keyboard(),
                                                     random_id=get_random_id())
                                else:
                                    db.update_balance(номер_врага,
                                                      int(баланс_получателя) - int(
                                                          деньги_отправляемые),chat_id_name)
                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) + int(деньги_отправляемые),chat_id_name)

                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, Победил в дуэли! {номер_врага} {деньги_отправляемые}₽",
                                                     keyboard=menu_games.get_keyboard(),
                                                     random_id=get_random_id())

                            проверка_ставки(номер_врага, деньги_отправляемые, действие)








                        except:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name}, игра не найдена",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())

                    if 'основное меню' == msg or основное_меню_текст == msg:
                        vk.messages.send(peer_id=event.object['peer_id'], message=основное_меню_текст,
                                         keyboard=menu.get_keyboard(),
                                         random_id=get_random_id()
                                         )
                    if игры_текст == msg or 'игры' == msg:
                        vk.messages.send(peer_id=event.object['peer_id'], message=игры_текст,
                                         keyboard=menu_games.get_keyboard(),
                                         random_id=get_random_id())
                    if баланс_текст == msg or "баланс" == msg:

                        if получаем_баланс(event.object.from_id,chat_id_name) is None:
                            db.update_balance(event.object.from_id, config.размер_бонуса,chat_id_name)

                        if int(получаем_баланс(event.object.from_id,chat_id_name)) == 0:
                            vk.messages.send(peer_id=event.object['peer_id'], message=f"{last_name}, нет денег(",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                        else:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name}, ваш баланс: {получаем_баланс(event.object.from_id,chat_id_name)}₽\n"
                                                     f"ваш рейтинг: {получаем_медали(event.object.from_id,chat_id_name)}",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                    if казино_текст in msg or "казино" in msg:

                        if казино_текст == msg or "казино" == msg:
                            vk.messages.send(peer_id=event.object['peer_id'], message=казино_текст,
                                             keyboard=menu_kazino.get_keyboard(),
                                             random_id=get_random_id())

                        if получаем_баланс(event.object.from_id,chat_id_name) is None:
                            db.update_balance(event.object.from_id, config.размер_бонуса,chat_id_name)

                        ставочные_деньги = msg = msg.replace('казино', '').replace("🎰", "")

                        def play(ставочные_деньги):
                            if int(получаем_баланс(event.object.from_id,chat_id_name)) == 0 or ставочные_деньги == 0:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, нет денег или ставка равна 0",
                                                 random_id=get_random_id())

                            elif int(ставочные_деньги) < 25:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, мин ставка 25₽",
                                                 random_id=get_random_id())


                            elif int(получаем_баланс(event.object.from_id,chat_id_name)) > config.определённый_баланс and int(
                                    ставочные_деньги) < config.мин_ставка_от_определённого_баланса and int(
                                ставочные_деньги) < int(получаем_баланс(event.object.from_id,chat_id_name)):
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, мин ставка: {config.мин_ставка_от_определённого_баланса}",
                                                 random_id=get_random_id())


                            elif int(ставочные_деньги) < int(получаем_баланс(event.object.from_id,chat_id_name)) or int(
                                    ставочные_деньги) == int(получаем_баланс(event.object.from_id,chat_id_name)):
                                def шанс_и_значения(шанс, коэф, шанс_проигрышный):

                                    if random < шанс:
                                        def message():
                                            vk.messages.send(peer_id=event.object['peer_id'],
                                                             message=f"{last_name} выпал x{коэф}:\n {str(получаем_баланс(event.object.from_id,chat_id_name))} ₽\n {рейтинг()}",
                                                             keyboard=menu_kazino.get_keyboard(),
                                                             random_id=get_random_id())

                                        if шанс < шанс_проигрышный:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,chat_id_name)) - (
                                                                      int(ставочные_деньги) * коэф),chat_id_name)
                                            message()
                                            return True

                                        elif random == 0:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,chat_id_name)) - (
                                                                  int(ставочные_деньги)),chat_id_name)
                                            message()
                                            return True
                                        else:
                                            db.update_balance(event.object.from_id,
                                                              int(получаем_баланс(event.object.from_id,chat_id_name)) + (
                                                                      int(ставочные_деньги) * коэф),chat_id_name)
                                            message()
                                            return True
                                    return False

                                if шанс_и_значения(10, 0, 65):
                                    print("")
                                elif шанс_и_значения(30, 0.5, 65):
                                    print("")
                                elif шанс_и_значения(65, 1.2, 65):
                                    print("")
                                elif шанс_и_значения(80, 1.5, 65):
                                    print("")
                                elif шанс_и_значения(92, 2, 65):
                                    print("")
                                elif шанс_и_значения(97, 5, 65):
                                    print("")
                                elif шанс_и_значения(100, 10, 65):
                                    print("")








                            else:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=last_name + ", у вас нет столько :) ",
                                                 random_id=get_random_id())

                        if isint(ставочные_деньги):
                            play(ставочные_деньги)
                        elif "процент" in msg:
                            msg = msg.replace("процент", "").replace(" ", "")
                            if isint(msg):
                                процент_от_ставки = (float(получаем_баланс(event.object.from_id,chat_id_name)) / 100) * float(msg)
                                play(процент_от_ставки)

                    if 'перевести' in msg:

                        if 'перевести все' in msg or 'перевести всё' in msg:

                            try:
                                номер_счёта_получателя = int(
                                    event.object.fwd_messages[0]['from_id'])
                                деньги_отправляемые = получаем_баланс(event.object.from_id)

                                def действие():
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id,chat_id_name), получаем_баланс(номер_счёта_получателя,chat_id_name)
                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) - int(деньги_отправляемые),chat_id_name)
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id,chat_id_name), получаем_баланс(номер_счёта_получателя,chat_id_name)
                                    db.update_balance(номер_счёта_получателя,
                                                      int(баланс_получателя) + int(деньги_отправляемые),chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, перевёл на {str(номер_счёта_получателя)} {str(деньги_отправляемые)} ₽",
                                                     random_id=get_random_id())

                                проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие)
                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name} сумма или счёт указаны неверно ",
                                                 random_id=get_random_id())

                        else:
                            сумма_перевода = str(msg).replace('перевести', '').split()
                            try:
                                деньги_отправляемые, номер_счёта_получателя = сумма_перевода[0], int(
                                    event.object.fwd_messages[0]['from_id'])

                                def действие():
                                    баланс_отправителя, баланс_получателя = получаем_баланс(
                                        event.object.from_id,chat_id_name), получаем_баланс(номер_счёта_получателя,chat_id_name)

                                    db.update_balance(event.object.from_id,
                                                      int(баланс_отправителя) - int(деньги_отправляемые),chat_id_name)
                                    db.update_balance(номер_счёта_получателя,
                                                      int(баланс_получателя) + int(деньги_отправляемые),chat_id_name)
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name}, перевёл на {номер_счёта_получателя} {деньги_отправляемые}₽",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())

                                проверка_ставки(номер_счёта_получателя, деньги_отправляемые, действие)

                            except:
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name} сумма или счёт указаны неверно ",
                                                 random_id=get_random_id())
                    if бонус_текст == msg or "бонус" == msg:
                        if получаем_баланс(event.object.from_id,chat_id_name) is None or int(
                                получаем_баланс(event.object.from_id),chat_id_name) < 25:
                            время_на_которое_обновится_бонус = (
                                    datetime.now() + timedelta(minutes=config.время_для_бонуса)).strftime(
                                time_format)
                            if получаем_сколько_бонусов_юзера(event.object.from_id,chat_id_name) is None:
                                db.update_time_bonus(event.object.from_id, время_на_которое_обновится_бонус,chat_id_name)
                                db.update_bonus(event.object.from_id, 0,chat_id_name)
                                db.update_balance(event.object.from_id, config.первый_бонус,chat_id_name)

                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, первый бонус: {config.первый_бонус}",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())

                            elif получаем_сколько_бонусов_юзера(event.object.from_id,chat_id_name) == 0:

                                if bonus(event.object.from_id,chat_id_name) is not True:
                                    vk.messages.send(peer_id=event.object['peer_id'],
                                                     message=f"{last_name} , бонус след: {бонус_по_мск(event.object.from_id,chat_id_name)}",
                                                     keyboard=menu.get_keyboard(),
                                                     random_id=get_random_id())

                            if получаем_сколько_бонусов_юзера(event.object.from_id,chat_id_name) == 1:
                                db.update_bonus(event.object.from_id, 0,chat_id_name)
                                db.update_balance(event.object.from_id, config.размер_бонуса,chat_id_name)
                                db.update_time_bonus(event.object.from_id, время_на_которое_обновится_бонус,chat_id_name)
                                vk.messages.send(peer_id=event.object['peer_id'],
                                                 message=f"{last_name}, бонус: {config.размер_бонуса}",
                                                 keyboard=menu.get_keyboard(),
                                                 random_id=get_random_id())

                        else:
                            vk.messages.send(peer_id=event.object['peer_id'],
                                             message=f"{last_name},вы не можете получить бонус",
                                             keyboard=menu.get_keyboard(),
                                             random_id=get_random_id())
                    if топ_текст == msg or "топ" == msg:
                        vk.messages.send(peer_id=event.object['peer_id'],
                                         message=f"👑 ТОП ОБЩИЙ 👑{получаем_топ_общий(chat_id_name)}",
                                         keyboard=menu_top.get_keyboard(),
                                         random_id=get_random_id())

        except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError):
            time.sleep(1)
            print('_______Timeout______')


if __name__ == "__main__":
    main()
