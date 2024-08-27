import tkinter as tk
from tkinter import ttk, filedialog
import vlc
import os

def parse_m3u(m3u_data):
    #M3U verilerini ayırma
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
    #M3U okuma ve yükleme
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_data = file.read()
                global groups
                groups = parse_m3u(m3u_data)
                update_group_listbox()
                save_file_path(file_path)  # Kaydet dosya yolunu
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

def save_file_path(file_path):
    #M3U dosya yolunu txt ile kaydeder
    with open('last_m3u_file.txt', 'w') as file:
        file.write(file_path)

def load_saved_file_path():
    #txt ye kaydedilen yeri okur
    if os.path.exists('last_m3u_file.txt'):
        with open('last_m3u_file.txt', 'r') as file:
            file_path = file.read().strip()
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        m3u_data = f.read()
                        global groups
                        groups = parse_m3u(m3u_data)
                        update_group_listbox()
                except Exception as e:
                    print(f"Dosya okuma hatası: {e}")

def update_group_listbox():

    group_listbox.delete(0, tk.END)
    for group in groups:
        group_listbox.insert(tk.END, group)

def update_channels(group):

    channel_listbox.delete(*channel_listbox.get_children())
    if group in groups:
        channels = groups[group]
        for channel in channels:
            channel_listbox.insert('', 'end', values=(channel['name'],))
    else:
        print(f"Seçilen grup bulunamadı: {group}")

def on_group_select(event):

    selection = group_listbox.curselection()
    if selection:
        selected_group = group_listbox.get(selection)
        update_channels(selected_group)

def on_channel_select(event):

    selection = channel_listbox.selection()
    if selection:
        selected_channel = channel_listbox.item(selection[0])
        channel_name = selected_channel['values'][0]
        #Find the URL from the group and channel list
        channel_url = next((c['url'] for g in groups.values() for c in g if c['name'] == channel_name), None)
        if channel_url:
            play_channel(channel_url, channel_name)
        else:
            print(f"Error: URL for channel '{channel_name}' not found.")

def format_time(milliseconds):
    seconds = int(milliseconds / 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"


def play_channel(url, channel_name):
    global player, player_window, progress_slider, volume_slider, update_progress_id, elapsed_label, duration_label

    #Create new window for video playback
    player_window = tk.Toplevel(root)
    player_window.title(f"{channel_name}")  # Set window title dynamically
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

    #Set initial volume to 75
    initial_volume = 75
    player.audio_set_volume(initial_volume)

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

    #Add progress and volume sliders
    progress_slider = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=300, bg='lightgrey',
                               sliderlength=15)
    progress_slider.pack(side=tk.LEFT, padx=5)
    progress_slider.bind("<ButtonRelease-1>", set_movie_time)  # Handle slider release to set time

    volume_slider = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=150, bg='lightgrey',
                             sliderlength=15)
    volume_slider.set(initial_volume)  # Set initial value of volume slider to 75
    volume_slider.pack(side=tk.LEFT, padx=5)
    volume_slider.bind("<Motion>", update_volume_slider)

    #Add time labels
    elapsed_label = tk.Label(controls_frame, text="00:00:00", bg='grey', fg='white')
    elapsed_label.pack(side=tk.LEFT, padx=5)

    duration_label = tk.Label(controls_frame, text="00:00:00", bg='grey', fg='white')
    duration_label.pack(side=tk.LEFT, padx=5)

    #Update every 500 milliseconds
    update_progress_id = player_window.after(500, update_progress_slider)

    player_window.protocol("WM_DELETE_WINDOW", on_player_close)


def update_progress_slider():

    if player:
        total_time = player.get_length()
        current_time = player.get_time()
        if total_time > 0:
            progress_slider.set((current_time / total_time) * 100)
            elapsed_label.config(text=format_time(current_time))
            duration_label.config(text=format_time(total_time))
        # Update progress slider periodically
        global update_progress_id
        update_progress_id = player_window.after(500, update_progress_slider)

def set_movie_time(event):
    """ Slider'dan seçilen zamana video zamanını ayarlar. """
    if player:
        total_time = player.get_length()
        new_time = (progress_slider.get() / 100) * total_time
        player.set_time(int(new_time))

def update_volume_slider(event):
    """ Volume slider'ı günceller. """
    if player:
        volume = volume_slider.get()
        player.audio_set_volume(volume)

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
        new_volume = min(current_volume + 10, 100)
        player.audio_set_volume(new_volume)
        volume_slider.set(new_volume)

def volume_down():
    """ Ses seviyesini düşürür. """
    if player:
        current_volume = player.audio_get_volume()
        new_volume = max(current_volume - 10, 0)
        player.audio_set_volume(new_volume)
        volume_slider.set(new_volume)

def on_player_close():
    """ Video penceresi kapatıldığında çağrılır. """
    global player, update_progress_id
    if player:
        player.stop()
        player.release()
    player_window.after_cancel(update_progress_id)
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
                background='#ffffff',  # Background color of the Treeview
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
load_saved_file_path()  # Load previously saved M3U file path

root.mainloop()
