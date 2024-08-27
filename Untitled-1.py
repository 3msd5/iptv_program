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

    return groups


def load_m3u_file():
    """ M3U dosyasını yükler ve içeriğini okur. """
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        print(f"Dosya yolu: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_data = file.read()
                print(f"Dosya içeriği:\n{m3u_data[:500]}...")
                global groups
                groups = parse_m3u(m3u_data)
                print(f"Gruplar: {groups}")
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
            channel_listbox.insert('', 'end', values=(channel['name'],))
    else:
        print(f"Seçilen grup bulunamadı: {group}")


def on_group_select(event):
    """ Ana grup seçildiğinde çağrılır. """
    selection = group_listbox.curselection()
    if selection:
        selected_group = group_listbox.get(selection)
        print(f"Seçilen ana grup: {selected_group}")
        update_channels(selected_group)
    else:
        print("Ana grup seçilmedi.")


def on_channel_select(event):
    """ Kanal seçildiğinde çağrılır. """
    selection = channel_listbox.selection()
    if selection:
        selected_channel = channel_listbox.item(selection[0])
        channel_name = selected_channel['values'][0]
        channel_url = [c['url'] for g in groups.values() for c in g if c['name'] == channel_name][0]
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

    player = vlc.MediaPlayer()

    embed = tk.Frame(player_window, bg='black')
    embed.pack(fill=tk.BOTH, expand=True)

    if os.name == 'nt':  # Windows için
        player.set_hwnd(embed.winfo_id())
    else:
        player.set_xwindow(embed.winfo_id())

    media = vlc.Media(url)
    player.set_media(media)
    player.play()

    controls_frame = tk.Frame(player_window)
    controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

    play_button = ttk.Button(controls_frame, text="▶️", command=play_video)
    play_button.pack(side=tk.LEFT)

    pause_button = ttk.Button(controls_frame, text="⏸️", command=pause_video)
    pause_button.pack(side=tk.LEFT)

    stop_button = ttk.Button(controls_frame, text="■", command=stop_video)
    stop_button.pack(side=tk.LEFT)

    rewind_button = ttk.Button(controls_frame, text="⏪", command=rewind_video)
    rewind_button.pack(side=tk.LEFT)

    forward_button = ttk.Button(controls_frame, text="⏩", command=forward_video)
    forward_button.pack(side=tk.LEFT)

    volume_up_button = ttk.Button(controls_frame, text="🔊+", command=volume_up)
    volume_up_button.pack(side=tk.LEFT)

    volume_down_button = ttk.Button(controls_frame, text="🔊-", command=volume_down)
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
        player.set_time(max(player.get_time() - 10000, 0))


def forward_video():
    """ Video ileri sarar. """
    if player:
        player.set_time(player.get_time() + 10000)


def volume_up():
    """ Ses seviyesini artırır. """
    if player:
        current_volume = player.audio_get_volume()
        player.audio_set_volume(min(current_volume + 10, 100))


def volume_down():
    """ Ses seviyesini düşürür. """
    if player:
        current_volume = player.audio_get_volume()
        player.audio_set_volume(max(current_volume - 10, 0))


def on_player_close():
    """ Video penceresi kapatıldığında çağrılır. """
    global player
    if player:
        player.stop()
        player.release()
    player_window.destroy()


# GUI oluşturma
root = tk.Tk()
root.title("IPTV Uygulaması")
root.geometry("800x600")

style = ttk.Style()
style.theme_use('clam')

root.option_add("*TButton.Font", "Helvetica 12")
root.option_add("*TLabel.Font", "Helvetica 12")
root.option_add("*TEntry.Font", "Helvetica 12")
root.option_add("*Listbox.Font", "Helvetica 12")

info_frame = ttk.Frame(root, padding="10")
info_frame.pack(fill='x')

load_button = ttk.Button(info_frame, text="M3U Dosyasını Yükle", command=load_m3u_file)
load_button.grid(row=0, columnspan=2, pady=10)

group_frame = ttk.Frame(root)
group_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

group_label = ttk.Label(group_frame, text="Gruplar", font=('Helvetica', 14, 'bold'))
group_label.pack(anchor=tk.W)

group_listbox = tk.Listbox(group_frame, height=25, width=30)  # Added width parameter here
group_listbox.pack(fill=tk.BOTH, expand=True)
group_listbox.bind('<<ListboxSelect>>', on_group_select)



channel_frame = ttk.Frame(root)
channel_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

channel_label = ttk.Label(channel_frame, text="Kanallar", font=('Helvetica', 14, 'bold'))
channel_label.pack(anchor=tk.W)

channel_listbox = ttk.Treeview(channel_frame, columns=('Name',), show='headings')
channel_listbox.heading('Name', text='Kanal Adı')
channel_listbox.column('Name', width=600)
channel_listbox.pack(fill=tk.BOTH, expand=True)
channel_listbox.bind('<<TreeviewSelect>>', on_channel_select)

groups = {}
update_group_listbox()

root.mainloop()
