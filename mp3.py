import os
import random
import mutagen.mp3 
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pygame import mixer

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Player")
      
        self.root.configure(bg="red")
        
        
       
        
        self.playlist = []
        self.resume_position = 0
        self.is_music_playing = False
       
        self.current_song_index = 0  

        mixer.init()

        self.side_drawer = tk.Frame(root, bg="#333", width=350,)
        self.side_drawer.pack(side=tk.LEFT, fill=tk.Y)

        self.playlistBox = tk.Listbox(self.side_drawer, selectmode=tk.SINGLE, bg="#333", fg="white", selectbackground="#444", height=10, width=30)
        self.playlistBox.pack(pady=10, fill=tk.BOTH, expand=True)
        self.playlistBox.bind("<Double-Button-1>", self.play_selected_song) 

        self.addFolderButton = tk.Button(self.side_drawer, text="Add Folder", command=self.add_folder, bg="black", fg="white", relief=tk.FLAT)
        self.addFolderButton.pack(side=tk.LEFT, pady=5, padx=10, ipadx=2, fill=tk.X)
        self.round_button(self.addFolderButton)

        self.addButton = tk.Button(self.side_drawer, text="Add Music", command=self.add_song, bg="black", fg="white", relief=tk.FLAT)
        self.addButton.pack(side=tk.LEFT, pady=5, padx=10, ipadx=2, fill=tk.X)
        self.round_button(self.addButton)

        self.removeButton = tk.Button(self.side_drawer, text="Remove Music", command=self.remove_song, bg="black", fg="white", relief=tk.FLAT)
        self.removeButton.pack(side=tk.LEFT, pady=5, padx=10, ipadx=2, fill=tk.X)
        self.round_button(self.removeButton)

       

        self.control_frame = tk.Frame(root, bg="black")
        self.control_frame.pack(pady=10)

        self.previousButton = tk.Button(self.control_frame, text="Previous", command=self.play_previous_song, bg="black", fg="white", relief=tk.FLAT)
        self.previousButton.pack(side=tk.LEFT, padx=5)
        self.round_button(self.previousButton)

        self.pause_resumeButton = tk.Button(self.control_frame, text="Pause", command=self.pause_resume_music, bg="black", fg="white", relief=tk.FLAT)
        self.pause_resumeButton.pack(side=tk.LEFT, padx=5)
        self.round_button(self.pause_resumeButton)

        self.nextButton = tk.Button(self.control_frame, text="Next", command=self.play_next_song, bg="black", fg="white", relief=tk.FLAT)
        self.nextButton.pack(side=tk.LEFT, padx=5)
        self.round_button(self.nextButton)

        self.repeatButton = tk.Button(self.control_frame, text="Repeat", command=self.toggle_repeat, bg="black", fg="white", relief=tk.FLAT)
        self.repeatButton.pack(side=tk.LEFT, padx=5)
        self.round_button(self.repeatButton)

        self.shuffleButton = tk.Button(self.control_frame, text="Shuffle", command=self.toggle_shuffle, bg="black", fg="white", relief=tk.FLAT)
        self.shuffleButton.pack(side=tk.LEFT, padx=5)
        self.round_button(self.shuffleButton)

        self.volume_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume, bg="black", fg="white")
        self.volume_slider.set(50)
        self.volume_slider.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.resizable(False, False)
        self.display_time()

        self.repeat = False
        self.shuffle = False

    def get_frames(self, gif):
        try:
            i = 0
            while True:
                gif.seek(i)
                frame = gif.copy()
                if i == 0:
                    duration = gif.info['duration']
                else:
                    duration = 100
                yield (frame, duration)
                i += 1
        except EOFError:
            pass

    def add_song(self):
        path = filedialog.askopenfilename(title="Choose a song", filetypes=[("MP3 files", "*.mp3")])
        if path:
            song_name = self.get_song_name(path)
            self.playlist.append({'path': path, 'name': song_name})
            self.update_playlist_preview()

    def remove_song(self):
        selected_song = self.playlistBox.curselection()
        if selected_song:
            selected_song = int(selected_song[0])
            del self.playlist[selected_song]
            self.update_playlist_preview()

    def add_folder(self):
        folder_path = filedialog.askdirectory(title="Choose a folder")
        if folder_path:
            self.playlist = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(".mp3"):
                    song_name = self.get_song_name(file_path)
                    self.playlist.append({'path': file_path, 'name': song_name})
            self.update_playlist_preview()

    def update_playlist_preview(self):
        self.playlistBox.delete(0, tk.END)
        for song_info in self.playlist:
            self.playlistBox.insert(tk.END, song_info['name'])

    def play_music(self):
        if self.playlist:
            selected_song = self.current_song_index
            mixer.music.load(self.playlist[selected_song]['path'])
            self.resume_position = 0
            mixer.music.play(start=self.resume_position)
            self.is_music_playing = True
            self.display_album_cover(self.playlist[selected_song]['path'])
            self.display_time() 

    def stop_music(self):
        mixer.music.stop()
        self.is_music_playing = False
        self.visualizer_index = 0
        self.visualizer_label.config(image=None)

    def pause_resume_music(self):
        if self.is_music_playing:
            mixer.music.pause()
            self.is_music_playing = False
            self.pause_resumeButton.config(text="Resume")
        else:
            mixer.music.unpause()
            self.is_music_playing = True
            self.pause_resumeButton.config(text="Pause")
            self.display_visualizer_frame()  

    def play_previous_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
            self.play_music()

    def play_next_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
            self.play_music()

    def get_song_name(self, path):
        try:
            audio = mixer.Sound(path)
            return os.path.basename(path)
        except Exception as e:
            print(f"Error while getting song name: {e}")
            return "Unknown"

    def display_album_cover(self, path):
        try:
            self.root.after(self.visualizer_frames[self.visualizer_index][1], self.display_visualizer_frame)
        except Exception as e:
            print(f"Error while displaying album cover: {e}")

    

    def round_button(self, button):
        button.bind("<Enter>", lambda event: button.config(bg="gray"))
        button.bind("<Leave>", lambda event: button.config(bg="black"))

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.repeatButton.config(text="Repeat ON" if self.repeat else "Repeat OFF")

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.shuffleButton.config(text="Shuffle ON" if self.shuffle else "Shuffle OFF")

    def set_volume(self, volume):
        mixer.music.set_volume(int(volume) / 100)

    def display_time(self):
        if self.is_music_playing:
            current_time = mixer.music.get_pos() // 1000
            total_time = mutagen.mp3.MP3(self.playlist[self.current_song_index]['path']).info.length
            formatted_time = f"Time: {current_time // 60}:{current_time % 60:02} / {int(total_time) // 60}:{int(total_time) % 60:02}"
            self.time_label.config(text=formatted_time)
            self.root.after(1000, self.display_time)

    def play_selected_song(self, event):
        self.current_song_index = self.playlistBox.curselection()[0]
        self.play_music()

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3Player(root)
    root.mainloop()
