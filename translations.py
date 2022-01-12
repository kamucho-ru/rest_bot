from data import *  # noqa


def print_lines(name, content, level=0):
    type = 'section' if isinstance(content, dict) else 'product'
    if type == 'section':
        result = ' {} '.format('v' if name in translations['rus'].keys() else 'x')
        print('{}{}{}'.format(result, ' ' * level, name))
        for i in content:
            print_lines(i, content[i], level + 1)
    else:
        descr, pict, price = content
        if name in translations['rus'].keys() and descr in translations['rus'].keys():
            result = ' v '
        elif name in translations['rus'].keys():
            result = ' ~ '
        elif descr in translations['rus'].keys():
            result = ' * '
        else:
            result = ' x '
        print('{}{}{} {} [{}]'.format(result, ' ' * (level + 1), price, name, descr))


for x in menu:
    print_lines(x, menu[x])
