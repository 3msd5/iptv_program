import tkinter as tk
from tkinter import ttk, filedialog
import vlc
import os


def parse_m3u(m3u_data):
    """ M3U verilerini işler ve grupları ve kanalları ayrıştırır. """
    groups = {}
    current_group = None

    lines = m3u_data.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            channel_info = line.split(',', 1)[-1]
            url_index = i + 1
            if url_index < len(lines) and not lines[url_index].startswith('#'):
                url = lines[url_index]
                group_info = line.split('group-title="', 1)[-1].split('"', 1)[0]

                if group_info not in groups:
                    groups[group_info] = []

                groups[group_info].append({'name': channel_info, 'url': url})
        # Handle additional lines or metadata if necessary

    return groups


def load_m3u_file():
    """ M3U dosyasını yükler ve içeriğini okur. """
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        print(f"Dosya yolu: {file_path}")  # Dosya yolunu kontrol et
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_data = file.read()
                print(f"Dosya içeriği:\n{m3u_data[:500]}...")  # İlk 500 karakteri yazdır
                global groups
                groups = parse_m3u(m3u_data)
                print(f"Gruplar: {groups}")  # Ayrıştırılan grupları yazdır
                update_group_listbox()
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
    else:
        print("Dosya seçilmedi.")


def update_group_listbox():
    """ Ana grup listbox'ını günceller. """
    group_listbox.delete(0, tk.END)
    for group in groups:
        group_listbox.insert(tk.END, group)


def update_channels(group):
    """ Seçilen grup ve alt gruptaki kanalları günceller. """
    channel_listbox.delete(*channel_listbox.get_children())
    if group in groups:
        channels = groups[group]
        for channel in channels:
            channel_listbox.insert('', 'end', values=(channel['name'], channel['url']))
    else:
        print(f"Seçilen grup bulunamadı: {group}")


def on_group_select(event):
    """ Ana grup seçildiğinde çağrılır. """
    selection = group_listbox.curselection()
    if selection:
        selected_group = group_listbox.get(selection)
        print(f"Seçilen ana grup: {selected_group}")  # Seçilen grubu yazdır
        update_channels(selected_group)
    else:
        print("Ana grup seçilmedi.")


def on_channel_select(event):
    """ Kanal seçildiğinde çağrılır. """
    selection = channel_listbox.selection()
    if selection:
        selected_channel = channel_listbox.item(selection[0])
        channel_name = selected_channel['values'][0]
        channel_url = selected_channel['values'][1]
        print(f"Seçilen Kanal: {channel_name}")
        print(f"URL: {channel_url}")
        play_channel(channel_url)
    else:
        print("Kanal seçilmedi.")


def play_channel(url):
    """ Verilen URL'den kanalı oynatır. """
    global player, player_window
    player_window = tk.Toplevel(root)
    player_window.title("Video Oynatıcı")
    player_window.geometry("800x600")

    # VLC video oynatıcıyı başlat
    player = vlc.MediaPlayer()

    # Video oynatıcıyı GUI'ye entegre et
    embed = tk.Frame(player_window, bg='black')
    embed.pack(fill=tk.BOTH, expand=True)

    # VLC video penceresi
    if os.name == 'nt':  # Windows için
        player.set_hwnd(embed.winfo_id())
    else:
        player.set_xwindow(embed.winfo_id())

    # Medyayı yükle ve oynat
    media = vlc.Media(url)
    player.set_media(media)
    player.play()

    # Kontrol çubuğunu oluştur
    controls_frame = tk.Frame(player_window)
    controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

    play_button = tk.Button(controls_frame, text="▶️", command=play_video)
    play_button.pack(side=tk.LEFT)

    pause_button = tk.Button(controls_frame, text="⏸️", command=pause_video)
    pause_button.pack(side=tk.LEFT)

    stop_button = tk.Button(controls_frame, text="■", command=stop_video)
    stop_button.pack(side=tk.LEFT)

    rewind_button = tk.Button(controls_frame, text="⏪", command=rewind_video)
    rewind_button.pack(side=tk.LEFT)

    forward_button = tk.Button(controls_frame, text="⏩", command=forward_video)
    forward_button.pack(side=tk.LEFT)

    volume_up_button = tk.Button(controls_frame, text="🔊+", command=volume_up)
    volume_up_button.pack(side=tk.LEFT)

    volume_down_button = tk.Button(controls_frame, text="🔊-", command=volume_down)
    volume_down_button.pack(side=tk.LEFT)

    player_window.protocol("WM_DELETE_WINDOW", on_player_close)


def play_video():
    """ Video oynatmayı başlatır. """
    if player:
        player.play()


def pause_video():
    """ Video oynatmayı duraklatır. """
    if player:
        player.pause()


def stop_video():
    """ Video oynatmayı durdurur. """
    if player:
        player.stop()


def rewind_video():
    """ Video geri sarar. """
    if player:
        player.set_time(max(player.get_time() - 10000, 0))  # 10 saniye geri sarar


def forward_video():
    """ Video ileri sarar. """
    if player:
        player.set_time(player.get_time() + 10000)  # 10 saniye ileri sarar


def volume_up():
    """ Ses seviyesini artırır. """
    if player:
        current_volume = player.audio_get_volume()
        player.audio_set_volume(min(current_volume + 10, 100))  # Ses seviyesini %100'ü aşmayacak şekilde artırır


def volume_down():
    """ Ses seviyesini düşürür. """
    if player:
        current_volume = player.audio_get_volume()
        player.audio_set_volume(max(current_volume - 10, 0))  # Ses seviyesini %0'ın altına düşürmez


def on_player_close():
    """ Video penceresi kapatıldığında çağrılır. """
    global player
    if player:
        player.stop()  # Video oynatıcıyı durdur
        player.release()  # Kaynakları serbest bırak
    player_window.destroy()  # Pencereyi kapat


# GUI oluşturma
root = tk.Tk()
root.title("IPTV Uygulaması")
root.geometry("800x600")

# M3U Dosyası Yükleme
info_frame = ttk.Frame(root, padding="10")
info_frame.pack(fill='x')

load_button = ttk.Button(info_frame, text="M3U Dosyasını Yükle", command=load_m3u_file)
load_button.grid(row=0, columnspan=2, pady=10)

# Ana Grup Listesi
group_listbox = tk.Listbox(root)
group_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
group_listbox.bind('<<ListboxSelect>>', on_group_select)

# Kanal Listesi
channel_listbox = ttk.Treeview(root, columns=('Name', 'URL'), show='headings')
channel_listbox.heading('Name', text='Kanal Adı')
channel_listbox.heading('URL', text='Kanal URL')
channel_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
channel_listbox.bind('<<TreeviewSelect>>', on_channel_select)

# Başlangıçta grup ve kanal listelerini güncelle
groups = {}
update_group_listbox()

# Uygulamayı çalıştır
root.mainloop()
