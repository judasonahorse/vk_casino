from vk_api.keyboard import VkKeyboard, VkKeyboardColor

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
