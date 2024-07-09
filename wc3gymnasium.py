import os
import tkinter as tk
from tkinter import ttk
import time
import webbrowser

class Wc3Gymnasium:
    def __init__(self, root):
        self.root = root
        self.root.title("wc3gymnasium")
        self.root.attributes('-topmost', True)  # Keep the window on top
        self.root.geometry("400x300+100+100")  # Set the window size and position
        self.root.resizable(True, True)  # Allow window resizing

        self.root_folder = 'C:\\wc3gymnasium'
        self.start_time = time.time()
        self.running = True
        self.font_size = 12
        self.keybind = None  # Store the current keybind

        self.create_widgets()
        self.update_timer()
        self.show_file_list()

    def open_warcraft_gym_url(self):
        url = "https://warcraft-gym.com/learn-warcraft-3/"
        try:
            webbrowser.open(url, new=2)  # Open in a new tab/window (optional)
        except webbrowser.Error:
            print("Error opening URL. Please check your web browser settings.")

    def create_widgets(self):
        # Create a frame for the list and timer
        self.frame = ttk.Frame(self.root, padding="5")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create a listbox with scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self.frame, height=10, borderwidth=0, highlightthickness=0, yscrollcommand=self.scrollbar.set, font=("Arial", self.font_size))
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.listbox.bind("<Double-1>", self.display_file_content)

        # Create a control frame for back button and font size adjustment
        self.control_frame = ttk.Frame(self.frame)
        self.control_frame.grid(row=0, column=0, pady=(5, 10), sticky=tk.W)

        # Create a back button
        self.back_button = ttk.Button(self.control_frame, text="Builds", command=self.show_file_list, state=tk.DISABLED)
        self.back_button.grid(row=0, column=0, padx=2)

        # Create a button to increase font size
        self.increase_font_button = tk.Button(self.control_frame, text="➕", font=("Arial", 7), command=self.increase_font_size)
        self.increase_font_button.grid(row=0, column=1, padx=2)

        # Create a button to decrease font size
        self.decrease_font_button = tk.Button(self.control_frame, text="➖", font=("Arial", 7), command=self.decrease_font_size)
        self.decrease_font_button.grid(row=0, column=2, padx=5)

        # Create a button for keybind
        self.keybind_button = tk.Button(self.control_frame, text="...", command=self.set_keybind)
        self.keybind_button.grid(row=0, column=3, padx=5)

        # Create a timer frame
        self.timer_frame = ttk.Frame(self.frame)
        self.timer_frame.grid(row=2, column=0, pady=(5, 0), sticky=tk.EW)

        # Create a timer label
        self.timer_label = ttk.Label(self.timer_frame, text="00:00:00", font=("Arial", 12))
        self.timer_label.grid(row=0, column=0, sticky=tk.E)

        # Create a reset timer button
        self.reset_button = tk.Button(self.timer_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, sticky=tk.E, padx=10)

        self.pause_label = tk.Label(self.timer_frame, text="⏯️", font=("Arial", 12), cursor="hand2")
        self.pause_label.grid(row=0, column=1, sticky=tk.E, padx=5)
        self.pause_label.bind("<Button-1>", lambda e: self.pause_timer())

        self.warcraft_gym_button = tk.Button(self.timer_frame, text="GYM!", command=self.open_warcraft_gym_url)
        self.warcraft_gym_button.grid(row=0, column=3, sticky=tk.E, padx=0)

        # Make the window draggable
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<ButtonRelease-1>", self.stop_move)
        self.frame.bind("<B1-Motion>", self.do_move)

    def set_keybind(self):
        self.keybind_button.config(text="...")
        self.keybind_button.unbind("<Key>")
        self.keybind_button.bind("<Key>", self.on_key_press)

    def on_key_press(self, event):
        self.keybind = event.keysym
        self.keybind_button.config(text=self.keybind)
        self.keybind_button.unbind("<Key>")
        self.keybind_button.bind("<Button-1>", lambda e: self.set_keybind())

    def show_file_list(self):
        self.listbox.delete(0, tk.END)
        md_files = [f for f in os.listdir(self.root_folder) if f.endswith('.md')]
        for md_file in md_files:
            self.listbox.insert(tk.END, os.path.splitext(md_file)[0])
        self.back_button.config(text="Builds", state=tk.DISABLED)

    def display_file_content(self, event):
        selected_file = self.listbox.get(self.listbox.curselection())
        with open(os.path.join(self.root_folder, selected_file + '.md'), 'r') as file:
            content = file.read()

        self.listbox.delete(0, tk.END)
        for line in content.splitlines():
            self.listbox.insert(tk.END, line)
        self.back_button.config(text="← Back", state=tk.NORMAL)

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            self.timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
        self.root.after(1000, self.update_timer)

    def reset_timer(self):
        self.start_time = time.time()
        self.running = True

    def pause_timer(self):
        self.running = not self.running

    def increase_font_size(self):
        self.font_size += 1
        self.listbox.config(font=("Arial", self.font_size))

    def decrease_font_size(self):
        self.font_size -= 1
        self.listbox.config(font=("Arial", self.font_size))

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Wc3Gymnasium(root)
    root.mainloop()
