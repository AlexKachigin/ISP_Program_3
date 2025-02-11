import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Progressbar
from datetime import datetime
from PIL import Image
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('isp_production.log'), logging.StreamHandler()]
)

# Функция для отображения сообщений
def show_message(title, message):
    messagebox.showinfo(title, message)

# Функция для выбора папки или файла через диалоговое окно
def select_directory_or_file(title, is_directory=True):
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно Tkinter
    if is_directory:
        return filedialog.askdirectory(title=title)
    else:
        return filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])

# Функция для переименования файлов в папке
def rename_files_in_folder(folder_path, start_number=1, prefix='Frame_', suffix='', extension=None):
    if not os.path.exists(folder_path):
        logging.error(f"Папка {folder_path} не существует.")
        show_message("Ошибка", f"Папка {folder_path} не существует.")
        return
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        logging.error(f"В папке {folder_path} нет файлов.")
        show_message("Ошибка", f"В папке {folder_path} нет файлов.")
        return
    
    file_times = []
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        modification_time = os.path.getmtime(file_path)
        file_times.append((file_path, modification_time))
    
    file_times.sort(key=lambda x: x[1])
    
    for i, (file_path, _) in enumerate(file_times, start=start_number):
        file_name = os.path.basename(file_path)
        
        if extension is None:
            _, ext = os.path.splitext(file_name)
        else:
            ext = '.' + extension.lstrip('.')
        
        new_file_name = f"{prefix}{i:03d}{suffix}{ext}"
        new_file_path = os.path.join(folder_path, new_file_name)
        
        try:
            os.rename(file_path, new_file_path)
            logging.info(f"Файл {file_name} переименован в {new_file_name}")
        except Exception as e:
            logging.error(f"Ошибка при переименовании файла {file_name}: {e}")

# Функция для чтения временных меток из CSV файла
def read_timecodes_from_csv(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Файл {file_path} не найден")
        raise FileNotFoundError(f"No such file or directory: '{file_path}'")
    
    timecodes = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'Source In' in row and 'Source Out' in row:
                timecodes.append({
                    'start': row['Source In'],
                    'end': row['Source Out']
                })
    logging.info(f"Содержимое timecodes: {timecodes}")
    return timecodes

# Функция для получения изображений из папки
def get_images_from_folder(image_folder):
    if not os.path.exists(image_folder) or not os.path.isdir(image_folder):
        logging.error(f"Папка изображений {image_folder} не найдена или не является директорией")
        raise FileNotFoundError(f"No such directory: '{image_folder}'")
    
    images = []
    for filename in sorted(os.listdir(image_folder)):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(image_folder, filename)
            logging.info(f"Найдено изображение: {file_path}")
            images.append(file_path)
    logging.info(f"Содержимое images: {images}")
    return images

# Функция для определения пресета по размеру изображения
def determine_preset(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if (width == 794 and height == 1054) or (width == 794 and height == 1060):
                return "Preset_1"
            elif width == 1920 and height == 1080:
                return "Preset_2"
            else:
                logging.warning(f"Неизвестное разрешение изображения {image_path}: {width}x{height}")
                return "Unknown_Preset"
    except Exception as e:
        logging.error(f"Ошибка при определении разрешения изображения {image_path}: {e}")
        return "Unknown_Preset"

# Функция для создания выходного CSV файла
def write_output_csv(timecodes, image_paths, output_file):
    if len(timecodes) != len(image_paths):
        logging.error("Количество временных кодов не совпадает с количеством изображений")
        raise ValueError("Количество временных кодов не совпадает с количеством изображений")
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['start', 'end', 'path', 'preset'])
        writer.writeheader()
        for i, timecode in enumerate(timecodes):
            image_path = image_paths[i]
            preset = determine_preset(image_path)
            writer.writerow({
                'start': timecode['start'],
                'end': timecode['end'],
                'path': image_path,
                'preset': preset
            })
    logging.info(f"Выходной файл CSV успешно создан: {output_file}")

# Главная функция для выполнения всех шагов
def start_processing():
    try:
        # Шаг 1: Выбор папки для переименования файлов
        show_message("Инструкция", "Шаг 1: Выберите папку с файлами для переименования.\n"
                                   "Файлы будут переименованы в формате Frame_001.png, Frame_002.png и т.д.")
        folder_path = select_directory_or_file("Выберите папку с файлами для переименования", is_directory=True)
        if not folder_path:
            logging.error("Папка для переименования не выбрана")
            messagebox.showerror("Ошибка", "Папка для переименования не выбрана. Программа завершена.")
            return
        
        # Шаг 2: Переименование файлов
        show_message("Информация", f"Начинаем переименование файлов в папке:\n{folder_path}\n\n"
                                   f"Файлы будут переименованы с префиксом 'Frame_' и нумерацией.")
        rename_files_in_folder(folder_path)
        show_message("Успех", "Файлы успешно переименованы!")
        
        # Шаг 3: Выбор файла с временными кодами
        show_message("Инструкция", "Шаг 2: Выберите CSV-файл с временными метками.\n"
                                   "Файл должен содержать столбцы 'Source In' и 'Source Out'.")
        timecodes_file = select_directory_or_file("Выберите файл с временными кодами", is_directory=False)
        if not timecodes_file:
            logging.error("Файл временных кодов не выбран")
            messagebox.showerror("Ошибка", "Файл временных кодов не выбран. Программа завершена.")
            return
        
        # Шаг 4: Выбор папки с изображениями
        show_message("Инструкция", "Шаг 3: Выберите папку с изображениями.\n"
                                   "В папке должны находиться изображения в формате .png.")
        images_folder = select_directory_or_file("Выберите папку с изображениями", is_directory=True)
        if not images_folder:
            logging.error("Папка с изображениями не выбрана")
            messagebox.showerror("Ошибка", "Папка с изображениями не выбрана. Программа завершена.")
            return
        
        # Шаг 5: Чтение временных кодов и изображений
        show_message("Инструкция", "Шаг 4: Читаем временные метки и изображения.\n"
                                   "Убедитесь, что количество временных меток соответствует количеству изображений.")
        timecodes = read_timecodes_from_csv(timecodes_file)
        image_paths = get_images_from_folder(images_folder)
        
        if not image_paths:
            logging.error("Изображения не найдены в выбранной папке")
            messagebox.showerror("Ошибка", "Изображения не найдены в выбранной папке. Программа завершена.")
            return
        
        if len(timecodes) != len(image_paths):
            logging.error("Количество временных кодов не совпадает с количеством изображений")
            messagebox.showerror("Ошибка", "Количество временных кодов не совпадает с количеством изображений. Программа завершена.")
            return
        
        # Шаг 6: Создание выходного CSV файла
        show_message("Инструкция", "Шаг 5: Создаем выходной CSV-файл.\n"
                                   "Этот файл будет содержать временные метки, пути к изображениям и их пресеты.")
        output_file = os.path.join(os.path.dirname(timecodes_file), "output.csv")
        write_output_csv(timecodes, image_paths, output_file)
        
        # Шаг 7: Уведомление об успехе
        show_message("Успех", f"CSV файл успешно создан: {output_file}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Создаем графический интерфейс
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ISP Production")
    root.geometry("400x300")
    
    label = tk.Label(root, text="ISP PRODUCTION", font=("Helvetica", 16))
    label.pack(pady=10)
    
    progress = Progressbar(root, orient='horizontal', length=350, mode='determinate')
    progress.pack(pady=10)
    
    button_start = tk.Button(root, text="Начать процесс", command=start_processing)
    button_start.pack(pady=20)
    
    root.mainloop()
