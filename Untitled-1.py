import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def parse_m3u(m3u_data):
    """ M3U verilerini işler ve kanalları ayrıştırır. """
    channels = []
    lines = m3u_data.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF:'):
            channel_info = lines[i].split(',', 1)[-1]
            i += 1
            if i < len(lines) and not lines[i].startswith('#'):
                url = lines[i]
                channels.append({'name': channel_info, 'url': url})
        i += 1
    return channels

def load_m3u_file():
    """ M3U dosyasını yükler ve içeriğini okur. """
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_data = file.read()
                print(f"Dosya içeriği:\n{m3u_data[:500]}...")  # İlk 500 karakteri yazdır
                return parse_m3u(m3u_data)
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
    return []

def refresh_channels():
    """ Kanal listesini yeniler ve GUI'de gösterir. """
    channels = load_m3u_file()
    if channels:
        for item in channel_listbox.get_children():
            channel_listbox.delete(item)
        for channel in channels:
            channel_listbox.insert('', 'end', values=(channel['name'], channel['url']))
        print(f"Kanal verileri başarıyla yüklendi: {len(channels)} kanal")
    else:
        print("Kanal verisi yüklenemedi.")

# GUI oluşturma
root = tk.Tk()
root.title("IPTV Uygulaması")
root.geometry("800x600")

# M3U Dosyası Yükleme
info_frame = ttk.Frame(root, padding="10")
info_frame.pack(fill='x')

load_button = ttk.Button(info_frame, text="M3U Dosyasını Yükle", command=refresh_channels)
load_button.grid(row=0, columnspan=2, pady=10)

# Kanal Listesi
frame = ttk.Frame(root, padding="10")
frame.pack(fill='both', expand=True)

channel_listbox = ttk.Treeview(frame, columns=('Name', 'URL'), show='headings')
channel_listbox.heading('Name', text='Kanal Adı')
channel_listbox.heading('URL', text='Kanal URL')
channel_listbox.pack(fill='both', expand=True)

# Uygulamayı çalıştır
root.mainloop()
