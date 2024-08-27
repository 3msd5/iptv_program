import tkinter as tk
from tkinter import ttk, filedialog
import vlc
import os
from PIL import Image, ImageTk


def parse_m3u(m3u_data):
    """ M3U verilerini işler ve grupları ve kanalları ayrıştırır. """
    groups = {}
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
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_data = file.read()
                global groups
                groups = parse_m3u(m3u_data)
                update_group_listbox()
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

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
        update_channels(selected_group)

def on_channel_select(event):
    """ Kanal seçildiğinde çağrılır. """
    selection = channel_listbox.selection()
    if selection:
        selected_channel = channel_listbox.item(selection[0])
        channel_name = selected_channel['values'][0]
        channel_url = [c['url'] for g in groups.values() for c in g if c['name'] == channel_name][0]
        play_channel(channel_url)

def play_channel(url):
    """ Verilen URL'den kanalı oynatır. """
    global player, player_window
    player_window = tk.Toplevel(root)
    player_window.title("Video Oynatıcı")
    player_window.geometry("1280x720")
    player_window.configure(bg='black')

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

    controls_frame = tk.Frame(player_window, bg='grey')
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
root.title("IPTV Player Made By MSD")
root.geometry("900x800")

# Set a background color for the main window
root.configure(bg='#e0e0e0')

# Define colors
bg_color = '#e0e0e0'
fg_color = '#333333'
button_color = '#ffffff'
header_color = '#b0b0b0'
listbox_bg = '#ffffff'
listbox_fg = '#333333'


# Create a custom style for ttk widgets
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', background=button_color, foreground=fg_color)
style.configure('TLabel', background=bg_color, foreground=fg_color)
style.configure('TFrame', background=bg_color)
style.configure('Treeview', background=listbox_bg, foreground=listbox_fg)
style.configure('Treeview.Heading', background=header_color, foreground=fg_color)
style.map('TButton', background=[('active', '#999999')])
# Define custom styles for the Treeview headings
style.configure('Treeview.Heading',
                background='#e0e0e0',  # Background color of the heading
                foreground='#333333',  # Text color of the heading
                font=('Helvetica', 12, 'bold'))  # Font settings

style.configure('Treeview',
                background='#333333',  # Background color of the Treeview
                foreground='#000',  # Text color of the Treeview
                rowheight=25)  # Row height of the Treeview

info_frame = ttk.Frame(root, padding="10")
info_frame.pack(fill='x')

load_button = ttk.Button(info_frame, text="M3U Dosyasını Yükle", command=load_m3u_file)
load_button.grid(row=0, columnspan=2, pady=10)

group_frame = ttk.Frame(root)
group_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

group_label = ttk.Label(group_frame, text="Gruplar", font=('Helvetica', 14, 'bold'))
group_label.pack(anchor=tk.W)

group_listbox = tk.Listbox(group_frame, height=25, width=30, bg=listbox_bg, fg=listbox_fg)
group_listbox.pack(fill=tk.BOTH, expand=True)
group_listbox.bind('<<ListboxSelect>>', on_group_select)

channel_frame = ttk.Frame(root)
channel_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

channel_label = ttk.Label(channel_frame, text="Kanallar", font=('Helvetica', 14, 'bold'))
channel_label.pack(anchor=tk.W)

# Create a Treeview without column headings
channel_listbox = ttk.Treeview(channel_frame, columns=('Name',), show='headings')  # Use 'headings' to avoid tree column header
channel_listbox.heading('Name', text='Grup İçi Kanallar')  # Remove heading text
channel_listbox.column('Name', width=600, anchor='w')  # Align text to the left

channel_listbox.pack(fill=tk.BOTH, expand=True)
channel_listbox.bind('<<TreeviewSelect>>', on_channel_select)


groups = {}
update_group_listbox()

root.mainloop()
