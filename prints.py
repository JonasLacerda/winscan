import comtypes
import threading
import comtypes.client as cc
import os
from PIL import Image, ImageEnhance
import tkinter as tk
from tkinter import messagebox
import tempfile
from file_listbox import update_file_list

def list_devices():
    wia = cc.CreateObject("WIA.DeviceManager")
    devices = wia.DeviceInfos

    scanner_names = []
    scanner_ids = []
    for i in range(1, devices.Count + 1):
        device_info = devices.Item(i)
        scanner_names.append(device_info.Properties("Name").Value)
        scanner_ids.append(device_info.DeviceID)
    return scanner_names, scanner_ids

def get_device_manager():
    """Cria e retorna um objeto WIA.DeviceManager."""
    wia = cc.CreateObject("WIA.DeviceManager")
    return wia

def nome_arquivo(name):
    file_path_template = "C:\\Users\\Jonas\\Documents\\Scanned Documents\\?.jpg"
    nome = name.get()
    file_path = file_path_template.replace("?", nome)
    return file_path

def scan_and_save(result_label, scanner_combobox, scanner_ids, file_name_entry, file_listbox):
    result_label.config(text="Escaneando...")
    selected_scanner_index = scanner_combobox.current()
    scanner_id = scanner_ids[selected_scanner_index]

    file_path = nome_arquivo(file_name_entry)

    # Executar a digitalização em uma thread separada
    scanning_thread = threading.Thread(target=scan_image, args=(scanner_id, file_path, result_label, file_listbox))
    scanning_thread.start()

def scan_image(scanner_id, file_path, result_label, file_listbox, quality=50, contrast_factor=1.5, saturation_factor=1.5):
    comtypes.CoInitialize()  # Inicializa COM
    wia = get_device_manager()
    scanner = None
    for device in wia.DeviceInfos:
        if device.DeviceID == scanner_id:
            scanner = device.Connect()
            break

    if scanner is not None:
        item = scanner.Items[1]
        image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")  # Formato JPEG

        # Obter o próximo nome de arquivo disponível
        file_path = get_next_filename(file_path)

        # Save the image to a temporary file
        temp_file_path = os.path.join(os.getcwd(), "temp.jpg")
        image.SaveFile(temp_file_path)

        # Abrir a imagem temporária com Pillow
        img = Image.open(temp_file_path)

        # Ajustar contraste
        contrast_enhancer = ImageEnhance.Contrast(img)
        img_contrast = contrast_enhancer.enhance(contrast_factor)

        # Ajustar saturação
        saturation_enhancer = ImageEnhance.Color(img_contrast)
        img_final = saturation_enhancer.enhance(saturation_factor)

        # Salvar a imagem final
        img_final.save(file_path, quality=quality)

        # Fechar e remover o arquivo temporário
        img.close()
        os.remove(temp_file_path)

        # Atualizar a interface gráfica na thread principal
        result_label.after(0, lambda: result_label.config(text="Digitalização concluída.\nImagem digitalizada e salva em:\n" + file_path))
        result_label.after(0, lambda: update_file_list(file_listbox))

    else:
        result_label.after(0, lambda: messagebox.showerror("Erro", "Nenhum scanner encontrado com o ID especificado."))

def get_next_filename(file_path):
    base_name, extension = os.path.splitext(file_path)
    index = 1
    while os.path.exists(file_path):
        file_path = f"{base_name}({index}){extension}"
        index += 1
    return file_path

