import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageEnhance, ImageTk
from prints import list_devices, get_device_manager, scan_and_save, nome_arquivo
from file_listbox import update_file_list, selecao
import os

original_scanned_img_tk = None
scanned_img_label = None 

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
    scanned_img_scrollbar.config(command=scanned_img_canvas.yview)

def sort_files_by_date(files):
    # Função para classificar arquivos por data
    return sorted(files, key=lambda x: os.path.getmtime(os.path.join(scanned_directory, x)), reverse=True)

def rename_selected_file(event=None):
    def submit_new_name(event=None):
        new_name = new_name_entry.get()
        new_window.destroy()
        # Adiciona a extensão .jpg se não estiver presente no novo nome do arquivo
        if not new_name.endswith(".jpg"):
            new_name += ".jpg"

        new_file_path = os.path.join(scanned_directory, new_name)
        os.rename(old_file_path, new_file_path)
        update_file_list(file_listbox)
        selecao(file_listbox, index)

    # Função para renomear o arquivo selecionado
    index = file_listbox.curselection()[0]
    old_filename = file_listbox.get(index)
    old_file_path = os.path.join(scanned_directory, old_filename)

    # Extrai o nome do arquivo sem a extensão
    old_filename_without_extension = os.path.splitext(old_filename)[0]

    # Cria uma nova janela de diálogo personalizada
    new_window = tk.Toplevel(window)
    new_window.title("Renomear Arquivo")

    # Calcula a posição da janela para ficar abaixo do centro da tela
    window.update_idletasks()  # Necessário para calcular o tamanho da janela corretamente
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 300
    window_height = 100
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2) + 100
    new_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    tk.Label(new_window, text=f"Novo nome para {old_filename_without_extension}:").pack(pady=10)

    # Cria um frame para alinhar a entrada e o botão na mesma linha
    entry_button_frame = tk.Frame(new_window)
    entry_button_frame.pack(pady=5)

    new_name_entry = tk.Entry(entry_button_frame)
    new_name_entry.pack(side=tk.LEFT, padx=5)
    new_name_entry.insert(0, old_filename_without_extension)
    new_name_entry.selection_range(0, tk.END)  # Seleciona o texto no campo de entrada
    new_name_entry.focus_set()  # Define o foco no campo de entrada
    new_name_entry.bind("<Return>", submit_new_name)  # Vincula o evento Enter ao campo de entrada

    tk.Button(entry_button_frame, text="Renomear", command=submit_new_name).pack(side=tk.LEFT, padx=5)


# Create the tkinter window
window = tk.Tk()
# Maximizar a janela
window.state('zoomed')
window.title("Scanner do Jonas atoa")
window.iconbitmap("C:\\Users\\Jonas\\Desktop\\scanner\\scannerpy\\midia\\icone.ico")
window.grid_columnconfigure(1, minsize=550)
window.grid_rowconfigure(1, minsize=440)

# Frame para conter os widgets do scanner
scanner_frame = tk.Frame(window)
scanner_frame.grid(row=0, column=0, padx=7, pady=0)

# Scanner Combobox
scanner_label = tk.Label(scanner_frame, text="Selecionar o Scanner:")
scanner_label.grid(row=0, column=0, sticky="n")
scanner_names, scanner_ids = list_devices()
scanner_combobox = ttk.Combobox(scanner_frame, values=scanner_names, state="readonly")
scanner_combobox.grid(row=1, column=0, sticky="n")
scanner_combobox.current(0)  # Seleciona o primeiro item da lista após a criação

scanner_combobox.grid(row=1, column=0, sticky="n")

# Função para atualizar o combobox
def update_scanner_list():
    scanner_names, scanner_ids = list_devices()  # Atualiza a lista de scanners
    scanner_combobox['values'] = scanner_names  # Atualiza os valores do combobox
    scanner_combobox.current(0)  # Seleciona o primeiro item da lista

update_button = tk.Button(scanner_frame, text="🔄", font=("Segoe UI Emoji", 12), command=update_scanner_list)
update_button.grid(row=1, column=1, sticky="n")

# File Name Entry
file_name_label = tk.Label(scanner_frame, text="Nome do arquivo:")
file_name_label.grid(row=2, column=0, pady=0, sticky="n")
file_name_entry = tk.Entry(scanner_frame)
file_name_entry.insert(0, "img")
file_name_entry.grid(row=3, column=0, pady=0, sticky="n")

def file_path():
    name = nome_arquivo(file_name_entry)
    return name

# Scan and Save Button
def process_scan():
    # Função que processa todas as ações em sequência
    scan_and_save(result_label, scanner_combobox, scanner_ids, file_name_entry, file_listbox)
    file_path = os.path.join("C:\\Users\\Jonas\\Documents\\Scanned Documents", f"{file_name_entry.get()}.jpg")
    display_scanned_image(file_path)
    

scan_button = tk.Button(scanner_frame, text="Scan e salvar", command=process_scan)

scan_button.grid(row=4, column=0, pady=7, sticky="n")


atalho_label = tk.Label(window, text="Seleciona o aqruivo e aperte F2 para renomear\npara excluir aperte delete\nF3 para escanear o arquivo\nCriador: Jonas")
atalho_label.grid(row=5, column=0, padx=7, pady=7)

# Result Label
result_label = tk.Label(window, text="", width=53, height=5)
result_label.grid(row=5, column=1, padx=7, pady=7, columnspan=2)

# Scanned Image Canvas
scanned_img_canvas = tk.Canvas(window, width=900, height=500)
scanned_img_canvas.grid(row=0, column=1, rowspan=3, padx=3, pady=3)

# Carregar e exibir a imagem no Canvas
image_path = "C:\\Users\\Jonas\\Desktop\\scanner\\scannerpy\\midia\\deathscan.jpg"
scanned_img = Image.open(image_path)
scanned_img.thumbnail((1800, 1500))  # Limitar o tamanho para exibição
scanned_img_tk = ImageTk.PhotoImage(scanned_img)

# Adicionar a imagem ao Canvas
scanned_img_id = scanned_img_canvas.create_image(0, 0, anchor="nw", image=scanned_img_tk)

# Configurar a barra de rolagem
scanned_img_scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=scanned_img_canvas.yview)
scanned_img_scrollbar.grid(row=0, column=2, rowspan=3, sticky='ns')
scanned_img_canvas.config(yscrollcommand=scanned_img_scrollbar.set)


Trow = 5

# Listbox to display scanned files
scanned_directory = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\"
file_listbox = tk.Listbox(window, height=35)
file_listbox.grid(row=0, column=3, rowspan = Trow, padx=7, pady=7)

# Add a scrollbar to the listbox
scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=file_listbox.yview)
scrollbar.grid(row=0, column=4, rowspan = Trow, sticky='ns')
file_listbox.config(yscrollcommand=scrollbar.set)


def delete_selected_file():
    # Obter o índice do item selecionado na lista
    selected_index = file_listbox.curselection()
    if selected_index:
        # Obter o nome do arquivo selecionado
        file_name = file_listbox.get(selected_index)
        # Confirmar a exclusão do arquivo
        confirmation = tk.messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir '{file_name}'?")
        if confirmation:
            # Construir o caminho completo do arquivo
            file_path = os.path.join("C:\\Users\\Jonas\\Documents\\Scanned Documents\\", file_name)
            # Excluir o arquivo
            os.remove(file_path)
            # Atualizar a lista de arquivos
            update_file_list(file_listbox)

def on_leave(event):
    # Restore original image size on mouse leave
    global original_scanned_img_tk, scanned_img_label
    scanned_img_label.config(image=original_scanned_img_tk)
    scanned_img_label.image = original_scanned_img_tk


# Crie um frame para conter os botões
button_frame = tk.Frame(window)
button_frame.grid(row=5, column=3, padx=5, pady=5)

# Botão Renomear
rename_button = tk.Button(button_frame, text="Renomear", command=rename_selected_file)
rename_button.grid(row=0, column=0, padx=5, pady=5)

# Botão Excluir
delete_button = tk.Button(button_frame, text="Excluir", command=delete_selected_file)
delete_button.grid(row=0, column=1, padx=5, pady=5)

# Initial update of the file list
update_file_list(file_listbox)

# Bind a function to the listbox to display image when clicked
def on_select(event):
    index = file_listbox.curselection()[0]
    filename = file_listbox.get(index)
    file_path = os.path.join(scanned_directory, filename)
    display_scanned_image(file_path)

file_listbox.bind("<<ListboxSelect>>", on_select)

#evento do mouse em cima da imagem
def on_mouse_wheel(event):
    """Manipula o evento de rolagem do mouse."""
    if scanned_img_canvas.winfo_containing(event.x_root, event.y_root) == scanned_img_canvas:
        scanned_img_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind F2 key to rename the selected file
window.bind("<F2>", rename_selected_file)
window.bind("<Delete>", lambda event: delete_selected_file())
window.bind("<F3>", lambda event: process_scan())
window.bind_all("<MouseWheel>", on_mouse_wheel)

# Run the tkinter event loop
window.mainloop()
