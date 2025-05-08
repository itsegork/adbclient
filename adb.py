import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk

def display_output(text_widget, output):
    text_widget.insert(tk.END, output + "\n")
    text_widget.yview(tk.END)

def connect_device(text_widget):
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devices = result.stdout.split("\n")[1:]
        connected_devices = [line.split("\t")[0] for line in devices if "device" in line]
        
        if not connected_devices:
            display_output(text_widget, "Нет подключенных устройств. Проверьте ADB и устройство.")
            return None
        
        if len(connected_devices) == 1:
            return connected_devices[0]
        
        root = tk.Tk()
        root.withdraw()
        device_choice = simpledialog.askinteger(
            "Выбор устройства",
            "Выберите устройство по номеру:\n" + "\n".join(f"{i+1}. {dev}" for i, dev in enumerate(connected_devices))
        )
        
        if device_choice and 1 <= device_choice <= len(connected_devices):
            return connected_devices[device_choice - 1]
        else:
            display_output(text_widget, "Неверный выбор устройства.")
            return None
    except Exception as e:
        display_output(text_widget, f"Ошибка при подключении к устройству: {e}")
        return None

def select_files():
    try:
        root = tk.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames(title="Выберите файлы")
        return files
    except Exception as e:
        return []

def select_destination():
    try:
        root = tk.Tk()
        root.withdraw()
        destination = simpledialog.askstring("Путь на Android", "Введите путь для сохранения файлов:", initialvalue="/sdcard/")
        return destination if destination else "/sdcard/"
    except Exception as e:
        return "/sdcard/"

def send_files_to_android(files, destination, device, text_widget):
    for file in files:
        try:
            command = ["adb", "-s", device, "push", file, destination]
            result = subprocess.run(command, capture_output=True, text=True)
            display_output(text_widget, f"{file} -> {result.stdout.strip()}" if result.returncode == 0 else f"Ошибка: {result.stderr.strip()}")
        except Exception as e:
            display_output(text_widget, f"Ошибка при отправке файла {file}: {e}")

def list_files_on_android(device, path, text_widget):
    try:
        command = ["adb", "-s", device, "shell", "ls", path]
        result = subprocess.run(command, capture_output=True, text=True)
        display_output(text_widget, f"Файлы в {path}:\n{result.stdout.strip()}")
    except Exception as e:
        display_output(text_widget, f"Ошибка при просмотре файлов: {e}")

def delete_file_on_android(device, file_path, text_widget):
    try:
        command = ["adb", "-s", device, "shell", "rm", "-r", file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        display_output(text_widget, f"Файл {file_path} удалён." if result.returncode == 0 else f"Ошибка: {result.stderr.strip()}")
    except Exception as e:
        display_output(text_widget, f"Ошибка при удалении файла: {e}")

def pull_file_from_android(device, file_path, destination, text_widget):
    try:
        command = ["adb", "-s", device, "pull", file_path, destination]
        result = subprocess.run(command, capture_output=True, text=True)
        display_output(text_widget, f"Файл {file_path} сохранён в {destination}." if result.returncode == 0 else f"Ошибка: {result.stderr.strip()}")
    except Exception as e:
        display_output(text_widget, f"Ошибка при сохранении файла: {e}")

def start_scrcpy(text_widget):
    try:
        subprocess.Popen(["scrcpy"])
    except Exception as e:
        display_output(text_widget, f"Ошибка при запуске scrcpy: {e}")

def main():
    root = tk.Tk()
    root.title("ADB File Manager")
    root.geometry("600x400")
    
    text_widget = tk.Text(root, height=15, width=80)
    text_widget.pack()

    device = connect_device(text_widget)
    if not device:
        return

    action_var = tk.StringVar(value="send")
    actions = ["send", "list", "delete", "pull", "scrcpy"]
    
    for action in actions:
        tk.Radiobutton(root, text=action.capitalize(), variable=action_var, value=action).pack(anchor=tk.W)
    
    def execute_action():
        action = action_var.get()
        if action == "send":
            selected_files = select_files()
            if selected_files:
                destination_path = select_destination()
                send_files_to_android(selected_files, destination_path, device, text_widget)
        elif action == "list":
            path = simpledialog.askstring("Путь на Android", "Введите путь для просмотра файлов:", initialvalue="/sdcard/")
            list_files_on_android(device, path, text_widget)
        elif action == "delete":
            file_path = simpledialog.askstring("Удаление файла", "Введите путь файла на Android:")
            delete_file_on_android(device, file_path, text_widget)
        elif action == "pull":
            file_path = simpledialog.askstring("Копирование файла", "Введите путь файла на Android:")
            destination = filedialog.askdirectory(title="Выберите папку для сохранения")
            if destination:
                pull_file_from_android(device, file_path, destination, text_widget)
        elif action == "scrcpy":
            start_scrcpy(text_widget)

    tk.Button(root, text="Выполнить", command=execute_action).pack()
    root.mainloop()

if __name__ == "__main__":
    main()
