from setuptools import setup
import py2app

APP = ['Visual_7.0_Full_CSV_to_AE.py']  # Замените 'your_script.py' на имя вашего скрипта
DATA_FILES = []  # Здесь можно указать дополнительные файлы (например, иконку)
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'Icon.icns',  # Если у вас есть иконка, добавьте её здесь
    'includes': ['tkinter', 'csv', 'os', 'logging', 'PIL'],  # Включаем все необходимые библиотеки
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],  # Требуется py2app для сборки
)
