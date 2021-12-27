langs = [
    ('Русский', 'set_rus_lang'),
    ('English', 'set_eng_lang'),
    # ('Hindi', 'set_hin_lang'),
    # ('Uzbek', 'set_uzb_lang'),
]

translations = {
    'rus': {
        'Cart: {} items = {} rs.': 'Корзина: {} шт = {} руп.',
        '{}, {} items * {} rs. = {} rs.': '{}, {} шт * {} руп. = {} руп.',
        '<< back <<': '<< Назад <<',
        'Please select ': 'Сделайте ваш выбор ',
        'Select positions for delete or proceed to order':
            'Выберите позиции для удаления или перейдите к оформлению заказа',
        'Proceed to order': 'Перейти к оформлению заказа',
        'Under construction. Please back later...': 'В разработке. Попробуйте повторить позже...',
        'Go to top menu': 'Вернуться в главное меню',
    },
    'hin': {

    },
}

drinks = {
    'Tea': {
        'Black': ['Plain black tea', 'picture_url', 50],
        'Milk': ['Tea with milk', 'picture_url', 50],
        'Masala': ['Masala tea', 'picture_url', 50],
    },
    'Coffee': {
        'Black': ['Plain black coffee', 'picture_url', 50],
        'Milk': ['Coffee with milk', 'picture_url', 50],
        'Masala': ['Masala coffee', 'picture_url', 50],
    },
    'Combucha': ['Contain tea & sugar', 'picture_url', 50],
}

menu = {
    'Full menu': {
        'Breakfast': {
            'Omelette eggs': ['Eggs', 'picture_url', 100],
            'Omelette eggs & milk': ['Eggs, milk', 'picture_url', 120],
            'Teremok': ['eggs, tomatoes, olives, cheese, greens, mushrooms', 'picture_url', 160],
            'spring roll': ['rice paper, veggies, chicken', 'picture_url', 60],
            'vietnam spring roll': ['papaya, carrot, cucumber, chicken, eggs', 'picture_url', 60],
            'Parotra from chief': ['egg, tomatoe, cheese, greens, onion', 'picture_url', 60],
            'Parota egg roll tofu': ['Eggs, tofu, ', 'picture_url', 140],
            'Parota egg roll chicken': ['Eggs, chicken, ', 'picture_url', 140],
            'Pakoda Cheese': ['Smoked', 'picture_url', 150],
        },
        'Hot dishes': {
            'Pulao pork': ['Rice, pork, veges & spices', 'picture_url', 230],
            'Pulao tofu': ['Rice, tofu, veges & spices', 'picture_url', 230],
            'Rice': ['Plain rice', 'picture_url', 60],
            'Kazan Kabab': ['Rice and veggies', 'picture_url', 180],
            'Mushed potatoes': ['Plain', 'picture_url', 80],
            'Mushed potatoes & cutlets': ['with chicken cutlet', 'picture_url', 160],
            'Pasta': ['Plain', 'picture_url', 80],
            'Pasta chicken': ['Pasta with chicken', 'picture_url', 230],
            'Pasta mushrooms': ['Pasta with mushrooms', 'picture_url', 210],
            'Pasta prawns': ['Pasta with prawns', 'picture_url', 230],
            'Chow Mein': ['Noodles with veggies', 'picture_url', 230],
            'Chow Mein chicken': ['Noodles with veggies and chicken', 'picture_url', 230],
            'Dumplings': ['Potatoe, mushrooms', 'picture_url', 210],
            'Dumplings tofu': ['Potatoe, mushrooms, tofu', 'picture_url', 230],
            'Dumplings chicken': ['Potatoe, mushrooms, chicken', 'picture_url', 230],
        },
        'Soups': {
            'Veg hot\'n\'sour': ['Plain rice', 'picture_url', 60],
            'tomatoe cream': ['Plain rice', 'picture_url', 60],
            'mushroom cream': ['Plain rice', 'picture_url', 60],
            'Borsh chicken': ['Plain rice', 'picture_url', 180],
            'Okroshka': ['Plain rice', 'picture_url', 180],
            'Chalop': ['Plain rice', 'picture_url', 180],
            'Pea tofu': ['Plain rice', 'picture_url', 200],
            'Pea chicken': ['Plain rice', 'picture_url', 200],
            'Pea ribs': ['from chief', 'picture_url', 250],
            'Chicken': ['Chicken, noodles and paneer', 'picture_url', 180],
            'Pumpkin': ['Plain rice', 'picture_url', 180],
        },
        'Salads': {
            'Olivie (chicken)': ['Chicken, green pea, potatoe, eggs, greens', 'picture_url', 140],
            'Olivie (tofu)': ['Tofu, green pea, potatoe, eggs, greens', 'picture_url', 140],
            'Spring': ['Marinated cabbage, carrot, onion', 'picture_url', 100],
            'Achik chuchuk': ['Marinated onion with tomatoes', 'picture_url', 100],
            'Beetroot & garlic': ['Beetroot, garlic, mayonese', 'picture_url', 100],
            'Greece\'s': ['Beetroot, garlic, mayonese', 'picture_url', 160],
            'Caesar': ['Parmezane', 'picture_url', 180],
        },

        'Drinks': drinks,
    },
    'Veg menu': {
        'Hot dishes': {
            'Soup': ['Pea sou, veggies', 'picture_url', 50],
            'French fries': ['Fried potatoes', 'picture_url', 50],
        },
        'Salads': {
            'Olivie (tofu)': ['Olivie with tofu', 'picture_url', 140],
            'Achik chuchuk': ['Marinated onion with tomatoes', 'picture_url', 100],
            'Spring': ['Cabbage, carrot, onion', 'picture_url', 100],
            'Beetroot&garlic': ['Beetroot, garlic, mayonese', 'picture_url', 100],
        },
        'Drinks': drinks,
    },
    'Drinks': drinks
}
