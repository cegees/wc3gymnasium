import sys
import os
import customtkinter as ctk
import time
import webbrowser
import markdown2
from tkinter import Text, font as tkfont
import re
from bs4 import BeautifulSoup

class Wc3Gymnasium:
    def __init__(self, root):
        self.root = root
        self.root.title("wc3gymnasium")
        self.root.attributes('-topmost', True)
        self.root.geometry("400x300+100+100")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root_folders = ['C:\\wc3gymnasium']
        if getattr(sys, 'frozen', False):
            print("Running as compiled exe")
            self.application_path = os.path.dirname(sys.executable)
        else:
            print("Running as script")
            self.application_path = os.path.dirname(os.path.abspath(__file__))
        
        print(f"Application path: {self.application_path}")
        self.root_folders.append(self.application_path)
        print(f"Root folders: {self.root_folders}")

        # Set the icon
        icon_path = os.path.join(self.application_path, 'peonmyicon.ico')
        if not os.path.exists(icon_path):
            icon_path = 'C:\\wc3gymnasium\\peonmyicon.ico'
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Icon not found at {icon_path}")


        # Add the directory of the executable (or script) to root_folders
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        self.root_folders.append(application_path)


        self.start_time = time.time()
        self.running = True
        self.paused_time = 0
        self.font_size = 12
        self.keybind = None
        self.overlay_mode = False
        self.waiting_for_keybind = False

        self.create_widgets()
        self.update_timer()
        self.show_file_list()
        self.root.bind("<KeyPress>", self.handle_keypress)

    def create_widgets(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # Listbox (now above other frames)
        self.listbox = Text(self.frame, font=("Arial Narrow", self.font_size), wrap="word")
        self.listbox.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind("<Double-1>", self.display_file_content)
        self.listbox.configure(state="disabled", cursor="arrow")

        self.listbox.tag_configure("h1", font=("Arial Narrow", self.font_size + 8, "bold"))
        self.listbox.tag_configure("h2", font=("Arial Narrow", self.font_size + 6, "bold"))
        self.listbox.tag_configure("h3", font=("Arial Narrow", self.font_size + 4, "bold"))
        self.listbox.tag_configure("bold", font=("Arial Narrow", self.font_size, "bold"))
        self.listbox.tag_configure("italic", font=("Arial Narrow", self.font_size, "italic"))
        self.listbox.tag_configure("bullet", lmargin1=20, lmargin2=30)
        self.listbox.tag_configure("code", font=("Courier", self.font_size), background="#f0f0f0")

        # Control frame
        self.control_frame = ctk.CTkFrame(self.frame)
        self.control_frame.pack(fill=ctk.X, padx=5, pady=5)

        self.back_button = ctk.CTkButton(self.control_frame, text="Builds", command=self.show_file_list, width=50)
        self.back_button.pack(side=ctk.LEFT, padx=2)

        self.increase_font_button = ctk.CTkButton(self.control_frame, text="➕", command=self.increase_font_size, width=30)
        self.increase_font_button.pack(side=ctk.LEFT, padx=2)

        self.decrease_font_button = ctk.CTkButton(self.control_frame, text="➖", command=self.decrease_font_size, width=30)
        self.decrease_font_button.pack(side=ctk.LEFT, padx=2)

        self.transparency_slider = ctk.CTkSlider(self.control_frame, from_=0.1, to=1.0, command=self.change_transparency)
        self.transparency_slider.set(1.0)
        self.transparency_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)

        # Timer frame
        self.timer_frame = ctk.CTkFrame(self.frame)
        self.timer_frame.pack(fill=ctk.X, padx=5, pady=5)

        self.timer_label = ctk.CTkLabel(self.timer_frame, text="00:00:00", font=("Arial Narrow", 12))
        self.timer_label.pack(side=ctk.LEFT, padx=5)

        self.pause_label = ctk.CTkLabel(self.timer_frame, text="⏯️", font=("Arial", 14))
        self.pause_label.pack(side=ctk.LEFT, padx=5)
        self.pause_label.bind("<Button-1>", lambda e: self.pause_timer())

        self.reset_label = ctk.CTkLabel(self.timer_frame, text="🔄", font=("Arial", 14))
        self.reset_label.pack(side=ctk.LEFT, padx=5)
        self.reset_label.bind("<Button-1>", lambda e: self.reset_timer())

        self.keybind_button = ctk.CTkButton(self.timer_frame, text="⌨️", command=self.start_keybind_listen, width=30)
        self.keybind_button.pack(side=ctk.LEFT, padx=5)

        self.warcraft_gym_button = ctk.CTkButton(self.timer_frame, text="GYM!", command=self.open_warcraft_gym_url, width=40)
        self.warcraft_gym_button.pack(side=ctk.LEFT, padx=5)

        self.appearance_label = ctk.CTkLabel(self.timer_frame, text="☯", font=("Consolas", 16))
        self.appearance_label.pack(side=ctk.RIGHT, padx=5)
        self.appearance_label.bind("<Button-1>", lambda e: self.toggle_appearance_mode())

        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<ButtonRelease-1>", self.stop_move)
        self.frame.bind("<B1-Motion>", self.do_move)

    def start_keybind_listen(self):
        self.waiting_for_keybind = True
        self.keybind_button.configure(text="Press a key")

    def handle_keypress(self, event):
        if self.waiting_for_keybind:
            self.keybind = event.keysym
            self.waiting_for_keybind = False
            self.keybind_button.configure(text=f"{self.keybind}")
        elif self.keybind and event.keysym == self.keybind:
            self.toggle_overlay_mode()

    def toggle_overlay_mode(self):
        self.overlay_mode = not self.overlay_mode
        if self.overlay_mode:
            self.control_frame.pack_forget()
            self.timer_frame.pack_forget()
            self.root.attributes('-alpha', 0.5)
            self.remove_title_bar()
        else:
            self.control_frame.pack(fill=ctk.X, padx=5, pady=5)
            self.timer_frame.pack(fill=ctk.X, padx=5, pady=5)
            self.root.attributes('-alpha', 1.0)
            self.restore_title_bar()

    def remove_title_bar(self):
        self.root.overrideredirect(True)
        self.root.update()

    def restore_title_bar(self):
        self.root.overrideredirect(False)
        self.root.update()

    def open_warcraft_gym_url(self):
        url = "https://warcraft-gym.com/learn-warcraft-3/"
        try:
            webbrowser.open(url, new=2)
        except webbrowser.Error:
            print("Error opening URL. Please check your web browser settings.")


    def show_file_list(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", ctk.END)
        md_files = []
        for folder in self.root_folders:
            print(f"Checking folder: {folder}")
            try:
                folder_files = [f for f in os.listdir(folder) if f.endswith('.md')]
                print(f"Files found in {folder}: {folder_files}")
                md_files.extend([os.path.join(folder, f) for f in folder_files])
            except FileNotFoundError:
                print(f"Folder not found: {folder}")
            except Exception as e:
                print(f"Error accessing {folder}: {str(e)}")
        
        print(f"All MD files found: {md_files}")
        for md_file in md_files:
            self.listbox.insert(ctk.END, os.path.splitext(os.path.basename(md_file))[0] + "\n")
        self.listbox.configure(state="disabled")
        self.back_button.configure(text="Builds", state=ctk.DISABLED)

    def display_file_content(self, event):
        index = self.listbox.index(f"@{event.x},{event.y}")
        line = self.listbox.get(f"{index} linestart", f"{index} lineend")
        if line.strip():  # Ensure we're not clicking on an empty line
            for folder in self.root_folders:
                file_path = os.path.join(folder, line.strip() + '.md')
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    self.apply_markdown_styles(content)
                    self.back_button.configure(text="← Back", state=ctk.NORMAL)
                    break

    def apply_markdown_styles(self, content):
        html = markdown2.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", ctk.END)
        
        def process_element(element, parent_tags=None):
            if parent_tags is None:
                parent_tags = []

            if isinstance(element, str):
                if element.strip():
                    tags = set(parent_tags)
                    if 'h1' in tags:
                        self.listbox.insert(ctk.END, element, 'h1')
                    elif 'h2' in tags:
                        self.listbox.insert(ctk.END, element, 'h2')
                    elif 'h3' in tags:
                        self.listbox.insert(ctk.END, element, 'h3')
                    elif 'strong' in tags:
                        self.listbox.insert(ctk.END, element, 'bold')
                    elif 'em' in tags:
                        self.listbox.insert(ctk.END, element, 'italic')
                    elif 'code' in tags:
                        self.listbox.insert(ctk.END, element, 'code')
                    else:
                        self.listbox.insert(ctk.END, element)
            elif element.name:
                new_tags = parent_tags + [element.name]
                if element.name in ['h1', 'h2', 'h3']:
                    self.listbox.insert(ctk.END, '\n')
                elif element.name == 'p':
                    self.listbox.insert(ctk.END, '\n')
                elif element.name == 'li':
                    self.listbox.insert(ctk.END, '• ', 'bullet')
                for child in element.children:
                    process_element(child, new_tags)
                if element.name in ['h1', 'h2', 'h3', 'p', 'li']:
                    self.listbox.insert(ctk.END, '\n')

        process_element(soup)
        
        content = self.listbox.get("1.0", ctk.END)
        content = re.sub(r'\n{3,}', '\n\n', content)
        self.listbox.delete("1.0", ctk.END)
        self.listbox.insert(ctk.END, content)
        
        self.listbox.configure(state="disabled")

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            self.timer_label.configure(text=f"{hours:02}:{minutes:02}:{seconds:02}")
        self.root.after(1000, self.update_timer)

    def reset_timer(self):
        self.start_time = time.time()
        self.running = True
        self.paused_time = 0

    def pause_timer(self):
        if self.running:
            self.running = False
            self.paused_time = time.time() - self.start_time
        else:
            self.running = True
            self.start_time = time.time() - self.paused_time

    def increase_font_size(self):
        self.font_size += 1
        self.update_font_size()

    def decrease_font_size(self):
        if self.font_size > 8:
            self.font_size -= 1
        self.update_font_size()

    def update_font_size(self):
        self.listbox.configure(font=("Arial Narrow", self.font_size))
        self.listbox.tag_configure("h1", font=("Arial Narrow", self.font_size + 8, "bold"))
        self.listbox.tag_configure("h2", font=("Arial Narrow", self.font_size + 6, "bold"))
        self.listbox.tag_configure("h3", font=("Arial Narrow", self.font_size + 4, "bold"))
        self.listbox.tag_configure("bold", font=("Arial Narrow", self.font_size, "bold"))
        self.listbox.tag_configure("italic", font=("Arial Narrow", self.font_size, "italic"))
        self.listbox.tag_configure("code", font=("Courier", self.font_size), background="#f0f0f0")
        
        content = self.listbox.get("1.0", ctk.END)
        if content.strip():
            self.apply_markdown_styles(content)

    def change_transparency(self, value):
        self.root.attributes('-alpha', float(value))

    def toggle_appearance_mode(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.listbox.configure(bg="white", fg="black")
        else:
            ctk.set_appearance_mode("Dark")
            self.listbox.configure(bg="black", fg="white")

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
    root = ctk.CTk()
    app = Wc3Gymnasium(root)
    root.mainloop()