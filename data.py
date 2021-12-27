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
        'Hot dishes': {
            'Pulao': ['Rice, pork, veges & spices', 'picture_url', 230],
            'Soup': ['Pea sou, veggies', 'picture_url', 50],
            'French fries': ['Fried potatoes', 'picture_url', 50],
        },
        'Salads': {
            'Olivie': {
                'Olivie (chicken)': ['Olivie with chicken', 'picture_url', 140],
                'Olivie (tofu)': ['Olivie with tofu', 'picture_url', 140],
            },
            'Achik chuchuk': ['Marinated onion with tomatoes', 'picture_url', 100],
            'Spring': ['Cabbage, carrot, onion', 'picture_url', 100],
            'Beetroot&garlic': ['Beetroot, garlic, mayonese', 'picture_url', 100],
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
