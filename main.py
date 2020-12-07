import PySimpleGUI as sg
from gost.gost3411 import GOST3411


def get_hash(val):
    g = GOST3411(val)
    return g.hash()

# print('Результат:', get_hash(b'This is message, length=32 bytes'))

layout = [
    [sg.Text('File'), sg.InputText(key='-FILENAME-'), sg.FileBrowse()],
    [sg.Input(size=(88, 1), key='-INPUT-')],
    [sg.Output(size=(88, 20), key='-OUTPUT-')],
    [sg.Text('Максин И.П. ПИбд-41')],
    [sg.Text('Вариант 13. ГОСТ Р 34.11')],
    [sg.Button('Хэш'), sg.Cancel()]
]
window = sg.Window('Lab2 Максин', layout)
while True:
    event, values = window.read()
    if event in (None, 'Exit', 'Cancel'):
        break
    if event == 'Хэш':
        filename = values['-FILENAME-']
        value = ''
        if filename:
            with open(filename, 'rb') as f:
                value = f.read()
        else:
            value = str.encode(values['-INPUT-'])

        window['-OUTPUT-'].update(get_hash(value))
