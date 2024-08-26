import tkinter as tk
from tkinter import ttk
import requests

# API bilgileri
API_URL = 'https://example.com/api'  # Xtream API URL'nizi buraya ekleyin
USERNAME = 'your_username'
PASSWORD = 'your_password'

def get_channels():
    """ Xtream API'den kanal listesini çeker. """
    try:
        response = requests.get(f'{API_URL}/get_channels', auth=(USERNAME, PASSWORD))
        response.raise_for_status()  # HTTP hatalarını yakalar
        return response.json()
    except requests.RequestException as e:
        print(f"API hatası: {e}")
        return []

def refresh_channels():
    """ Kanal listesini yeniler ve GUI'de gösterir. """
    channels = get_channels()
    for item in channel_listbox.get_children():
        channel_listbox.delete(item)
    for channel in channels:
        channel_listbox.insert('', 'end', values=(channel['name'], channel['url']))

# GUI oluşturma
root = tk.Tk()
root.title("IPTV Uygulaması")
root.geometry("800x600")

# Kanal Listesi
frame = ttk.Frame(root, padding="10")
frame.pack(fill='both', expand=True)

channel_listbox = ttk.Treeview(frame, columns=('Name', 'URL'), show='headings')
channel_listbox.heading('Name', text='Kanal Adı')
channel_listbox.heading('URL', text='Kanal URL')
channel_listbox.pack(fill='both', expand=True)

# Yenile butonu
refresh_button = ttk.Button(root, text="Yenile", command=refresh_channels)
refresh_button.pack(pady="10")

# Uygulamayı çalıştır
refresh_channels()  # Başlangıçta kanalları yükle
root.mainloop()
