import os
import tkinter as tk

scanned_directory = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\"

def update_file_list(file_listbox):
    file_listbox.delete(0, tk.END)  # Limpar os itens existentes
    scanned_directory = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\"
    # Obter uma lista de arquivos no diretório ordenados por data de modificação, com os mais recentes primeiro
    files = sorted(os.listdir(scanned_directory), key=lambda x: os.path.getmtime(os.path.join(scanned_directory, x)), reverse=True)
    # Adicionar os arquivos à lista
    for filename in files:
        if filename.endswith(".jpg"):
            file_listbox.insert(tk.END, filename)

def selecao(file_listbox, index):
    if file_listbox:
        first_item = file_listbox.get(0)
        full_path = os.path.join(scanned_directory, first_item)
        #display_scanned_image(full_path)
        file_listbox.selection_clear(0, 'end')      # Limpa qualquer seleção existente
        file_listbox.selection_set(index)           # Seleciona o primeiro item
        file_listbox.activate(index)                # Ativa o primeiro item
        file_listbox.focus() 