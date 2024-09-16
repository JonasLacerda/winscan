import comtypes.client as cc
import comtypes
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageEnhance, ImageTk
import os
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def start_observer(file_listbox):
    event_handler = DirectoryEventHandler(file_listbox)
    observer = Observer()
    observer.schedule(event_handler, scanned_directory, recursive=False)
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()
    return observer


def list_devices():
    wia = cc.CreateObject("WIA.DeviceManager")
    devices = wia.DeviceInfos

    scanner_names = []
    for i in range(1, devices.Count + 1):
        device_info = devices.Item(i)
        scanner_names.append(device_info.Properties("Name").Value)

    scanner_ids = [device.DeviceID for device in devices]
    return scanner_names, scanner_ids


def scan_and_save():
    result_label.config(text="escaneando...")
    selected_scanner_index = scanner_combobox.current()
    scanner_id = scanner_ids[selected_scanner_index]

    nome = file_name_entry.get()
    file_path_template = os.path.join(scanned_directory, f"{nome}.jpg")
    file_path = get_next_filename(file_path_template)

    scanning_thread = threading.Thread(target=scan_image, args=(scanner_id, file_path))
    scanning_thread.start()

def get_next_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1

    # Verifica se o arquivo já existe e incrementa o contador até encontrar um nome de arquivo não existente
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1

    return file_path


def scan_image(scanner_id, file_path, quality=50, contrast_factor=1.5, saturation_factor=1.5):
    comtypes.CoInitialize()  # Initialize COM
    wia = cc.CreateObject("WIA.DeviceManager")
    scanner = None
    for device in wia.DeviceInfos:
        if device.DeviceID == scanner_id:
            scanner = device.Connect()
            break

    if scanner is not None:
        item = scanner.Items[1]
        image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")  # JPEG format

        # Get the next available filename
        file_path = get_next_filename(file_path)

        # Save the image to a temporary file
        temp_file_path = os.path.join(os.getcwd(), "temp_image.jpg")

        # Ensure the temporary file name is unique
        counter = 1
        while os.path.exists(temp_file_path):
            temp_file_path = os.path.join(os.getcwd(), f"temp_image_{counter}.jpg")
            counter += 1

        try:
            image.SaveFile(temp_file_path)
        except Exception as e:
            result_label.config(text=f"Erro ao salvar o arquivo temporário: {e}")
            return

        # Open the temporary image with Pillow
        img = Image.open(temp_file_path)

        # Adjust contrast
        contrast_enhancer = ImageEnhance.Contrast(img)
        img_contrast = contrast_enhancer.enhance(contrast_factor)

        # Adjust saturation
        saturation_enhancer = ImageEnhance.Color(img_contrast)
        img_final = saturation_enhancer.enhance(saturation_factor)

        # Save the final image
        img_final.save(file_path, quality=quality)

        # Remove the temporary file
        img.close()
        os.remove(temp_file_path)  # Delete the temporary file
        result_label.config(text="Digitalização concluída.\nImagem digitalizada e salva em:\n" + file_path)
        display_scanned_image(file_path)
        file_listbox.update()
    else:
        result_label.config(text="Nenhum scanner encontrado com o ID especificado.")


def display_scanned_image(file_path):
    global original_scanned_img_tk, scanned_img_canvas, scanned_img_id

    # Abre a imagem
    scanned_img = Image.open(file_path)

    # Redimensiona a imagem para caber dentro do tamanho limite
    scanned_img.thumbnail((1600, 1500))  # Limitar o tamanho para exibição

    # Converte a imagem para o formato suportado pelo Tkinter
    scanned_img_tk = ImageTk.PhotoImage(scanned_img)

    # Limpa qualquer widget existente no canvas
    scanned_img_canvas.delete("all")

    # Adiciona a imagem ao canvas
    scanned_img_id = scanned_img_canvas.create_image(0, 0, anchor="nw", image=scanned_img_tk)

    # Atualiza a largura e a altura do canvas para corresponder ao tamanho da imagem
    scanned_img_canvas.config(scrollregion=scanned_img_canvas.bbox("all"))

    # Mantenha uma referência à imagem original para evitar a coleta de lixo
    original_scanned_img_tk = scanned_img_tk

    # Atualiza a barra de rolagem vertical
    scanned_img_canvas.config(yscrollcommand=scanned_img_scrollbar.set)


# Função para atualizar o combobox
def update_scanner_list():
    scanner_names, scanner_ids = list_devices()  # Atualiza a lista de scanners
    scanner_combobox['values'] = scanner_names  # Atualiza os valores do combobox
    scanner_combobox.current(0)  # Seleciona o primeiro item da lista

# Define FileListBox class
class FileListBox:
    def __init__(self, parent, directory, *args, **kwargs):
        self.directory = directory
        self.file_listbox = tk.Listbox(parent, height=35, *args, **kwargs)
        self.file_listbox.grid(row=0, column=3, rowspan=5, padx=7, pady=7)
        self.scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.scrollbar.grid(row=0, column=4, rowspan=5, sticky='ns')
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_select)

    def update(self):
        self.file_listbox.delete(0, tk.END)
        files = sorted(os.listdir(self.directory), key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
        for filename in files:
            if filename.endswith(".jpg"):
                self.file_listbox.insert(tk.END, filename)

    def select_first_item(self):
        if self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)
            self.file_listbox.activate(0)
            self.file_listbox.focus()
            self.on_select()

    def on_select(self, event=None):
        index = self.file_listbox.curselection()
        if index:
            filename = self.file_listbox.get(index[0])
            file_path = os.path.join(self.directory, filename)
            display_scanned_image(file_path)
        else:
            result_label.config(text="Nenhum arquivo selecionado.")

    def get_selected_file(self):
        index = self.file_listbox.curselection()
        if index:
            return self.file_listbox.get(index[0])
        return None

    def delete_selected_file(self):
        selected_file = self.get_selected_file()
        if selected_file:
            confirmation = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir '{selected_file}'?")
            if confirmation:
                file_path = os.path.join(self.directory, selected_file)
                os.remove(file_path)
                self.update()
                self.select_first_item()

    def rename_selected_file(event=None):
        old_filename = file_listbox.get_selected_file()
        if old_filename:
            old_file_path = os.path.join(scanned_directory, old_filename)
            old_filename_without_extension = os.path.splitext(old_filename)[0]

            new_window = tk.Toplevel(window)
            new_window.title("Renomear Arquivo")
            window.update_idletasks()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            window_width = 300
            window_height = 100
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2) + 100
            new_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            tk.Label(new_window, text=f"Novo nome para {old_filename_without_extension}:").pack(pady=10)

            entry_button_frame = tk.Frame(new_window)
            entry_button_frame.pack(pady=5)

            new_name_entry = tk.Entry(entry_button_frame)
            new_name_entry.pack(side=tk.LEFT, padx=5)
            new_name_entry.insert(0, old_filename_without_extension)
            new_name_entry.selection_range(0, tk.END)
            new_name_entry.focus_set()

            def submit_new_name(event=None):
                new_name = new_name_entry.get()
                new_window.destroy()
                if not new_name.endswith(".jpg"):
                    new_name += ".jpg"
                new_file_path = os.path.join(scanned_directory, new_name)
                os.rename(old_file_path, new_file_path)
                file_listbox.update()

                # Seleciona o item renomeado e rola para ele
                window.after(50, lambda: select_renamed_item(new_name))

            def select_renamed_item(new_name):
                print(new_name)
                index = None
                for i, item in enumerate(file_listbox.file_listbox.get(0, tk.END)):
                    if item == new_name:
                        index = i
                        break

                if index is not None:
                    print(index)
                    file_listbox.file_listbox.selection_set(index)
                    file_listbox.file_listbox.activate(index)
                    file_listbox.file_listbox.see(index)


            new_name_entry.bind("<Return>", submit_new_name)
            tk.Button(entry_button_frame, text="Renomear", command=submit_new_name).pack(side=tk.LEFT, padx=5)

class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, file_listbox):
        super().__init__()
        self.file_listbox = file_listbox
        self.is_navigating = False  # Flag para identificar navegação

    def on_modified(self, event):
        # Se estiver navegando na lista, ignorar o evento de modificação
        if self.is_navigating:
            return
        
        # Código original que atualiza o file_listbox
        self.update_file_listbox()

    def update_file_listbox(self):
        # Atualize a lista de arquivos no listbox
        self.file_listbox.delete(0, tk.END)
        for filename in os.listdir(scanned_directory):
            self.file_listbox.insert(tk.END, filename)

# Define other functions here (e.g., scan_image, display_scanned_image, etc.)

# Initialize the Tkinter window
window = tk.Tk()
window.state('zoomed')
window.title("Scanner Win")
window.iconbitmap("C:\\Users\\Jonas\\Desktop\\scanner\\scannerpy\\icone.ico")

window.grid_columnconfigure(1, minsize=550)
window.grid_rowconfigure(1, minsize=440)

scanner_frame = tk.Frame(window)
scanner_frame.grid(row=0, column=0, padx=7, pady=0)

scanner_names, scanner_ids = list_devices()
scanner_combobox = ttk.Combobox(scanner_frame, values=scanner_names, state="readonly")
scanner_combobox.grid(row=1, column=0, sticky="n")
scanner_combobox.current(0)

update_button = tk.Button(scanner_frame, text="🔄", font=("Segoe UI Emoji", 12), command=update_scanner_list)
update_button.grid(row=1, column=1, sticky="n")

file_name_entry = tk.Entry(scanner_frame)
file_name_entry.insert(0, "img")
file_name_entry.grid(row=3, column=0, pady=0, sticky="n")

scan_button = tk.Button(scanner_frame, text="Scan e salvar", command=scan_and_save)
scan_button.grid(row=4, column=0, pady=7, sticky="n")

atalho_label = tk.Label(window, text="Seleciona o aqruivo e aperte F2 para renomear\npara excluir aperte delete\nF3 para escanear o arquivo\nCriador: Jonas")
atalho_label.grid(row=5, column=0, padx=7, pady=7)

result_label = tk.Label(window, text="", width=53, height=5)
result_label.grid(row=5, column=1, padx=7, pady=7, columnspan=2)

scanned_img_canvas = tk.Canvas(window, width=900, height=500)
scanned_img_canvas.grid(row=0, column=1, rowspan=3, padx=3, pady=3)

# Configurar a barra de rolagem
scanned_img_scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=scanned_img_canvas.yview)
scanned_img_scrollbar.grid(row=0, column=2, rowspan=3, sticky='ns')
scanned_img_canvas.config(yscrollcommand=scanned_img_scrollbar.set)

scanned_directory = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\"
file_listbox = FileListBox(window, scanned_directory)

# Crie um frame para conter os botões
button_frame = tk.Frame(window)
button_frame.grid(row=5, column=3, padx=5, pady=5)

# Botão Renomear
rename_button = tk.Button(button_frame, text="Renomear", command=lambda: file_listbox.rename_selected_file())
rename_button.grid(row=0, column=0, padx=5, pady=5)

# Botão Excluir
delete_button = tk.Button(button_frame, text="Excluir", command=file_listbox.delete_selected_file)
delete_button.grid(row=0, column=1, padx=5, pady=5)

def delete_selected_file():
    file_listbox.delete_selected_file()

def rename_selected_file(event=None):
    file_listbox.rename_selected_file()

def on_select(event):
    # Ativar a flag antes de navegar
    file_listbox.event_handler.is_navigating = True
    
    # Aqui vai o código para lidar com a seleção
    selection_index = file_listbox.curselection()
    if selection_index:
        file_name = file_listbox.get(selection_index)
        # Seu código para abrir ou exibir a imagem selecionada
    
    # Desativar a flag após a navegação
    file_listbox.event_handler.is_navigating = False


# Inicialize o observador
observer = start_observer(file_listbox)

def on_closing():
    observer.stop()
    observer.join()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)


#evento do mouse em cima da imagem
def on_mouse_wheel(event):
    if scanned_img_canvas.winfo_containing(event.x_root, event.y_root) == scanned_img_canvas:
        scanned_img_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

window.bind("<F2>", rename_selected_file)
window.bind("<Delete>", lambda event: delete_selected_file())
window.bind("<F3>", lambda event: scan_and_save())
window.bind_all("<MouseWheel>", on_mouse_wheel)

file_listbox.update()

window.mainloop()
