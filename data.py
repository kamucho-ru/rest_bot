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
        '{} [{}] * {} = {} rs.': '{} [{}] * {} = {} rs.',
        '<< back': '<< Назад',
        'Please select ': 'Сделайте ваш выбор ',
        'Select positions for delete or proceed to order': 'Выберите позиции для удаления или перейдите к оформлению заказа',
        'Proceed to order': 'Перейти к оформлению заказа',
        'Order at restaurant': 'Order at restaurant',
        'Takeaway from restaurant': 'Takeaway from restaurant',
        'Delivery': 'Доставка',
        'Go to top menu': 'Вернуться в главное меню',
        'Choose order type': 'Choose order type',
        'Choose payment type': 'Choose payment type',
        'Cash': 'Cash',
        'PhonePe': 'PhonePe',
        'Thank you for your order! Our managers will reach you soon': 'Спасибо за ваш заказ! С вами свяжутся в ближайшее время',
        'Remove 1': 'Убрать 1',
        'Add 1': 'Добавить 1',
    },
    'hin': {},
}

from data_loader import menu, trans_rus

translations['rus'].update(trans_rus)
