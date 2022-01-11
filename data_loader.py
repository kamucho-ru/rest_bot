f = open('menu.csv', 'r')
fileline = f.readline()

menu = {}
veg_menu = {}
meat_menu = {}

trans_rus = {
    'Full menu': 'Всё меню',
    'Veg menu': 'Вегетерианское меню',
    'Meat menu': 'Мясное меню',
}

current_section = None

# print('## Main menu')
# print('menu = {')
while fileline:
    row = fileline.split(';')

    if not row[2]:
        current_section = row[0]
        menu[current_section] = {}
        veg_menu[current_section] = {}
        meat_menu[current_section] = {}
        # print(row[0])
    else:
        is_veg = True if '+' in row[1] else False
        is_drinks = True if current_section == 'Drinks' else False
        product = [is_veg, 'picture_url', row[2]]
        menu[current_section][row[0]] = product
        if is_veg or is_drinks:
            veg_menu[current_section][row[0]] = product
        if not is_veg or is_drinks:
            meat_menu[current_section][row[0]] = product

        # print(f'{row[0]} / {menu[current_section][row[0]]}')

    if row[0] not in trans_rus:
        trans_rus[row[0]] = row[3]

    fileline = f.readline()


# print('## this is translate dict')
# print(''.join([f'{k}:{translations[k]}' for k in translations]))

menu = {
    'Full menu': menu,
    'Veg menu': veg_menu,
    'Meat menu': meat_menu,
}
