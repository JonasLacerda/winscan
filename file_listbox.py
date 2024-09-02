import tkinter as tk
import os

scanned_directory = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\"

def update_file_list(file_listbox):
    file_listbox.delete(0, tk.END)  # Limpar os itens existentes
    files = sorted(os.listdir(scanned_directory), key=lambda x: os.path.getmtime(os.path.join(scanned_directory, x)), reverse=True)
    for filename in files:
        if filename.endswith(".jpg"):
            file_listbox.insert(tk.END, filename)

def selecao(file_listbox, index):
    if file_listbox:
        file_listbox.selection_clear(0, 'end')  # Limpa qualquer seleção existente
        file_listbox.selection_set(index)  # Seleciona o item
        file_listbox.activate(index)  # Ativa o item
        file_listbox.focus()
