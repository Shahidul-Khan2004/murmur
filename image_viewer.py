import tkinter as tk
from PIL import Image, ImageTk
import os
from image_selector import VALID_IMG_EXT
import io

def make_thumb(path, thumb_w: int, thumb_h: int):
    img = Image.open(path)
    img = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

def show_image(data: str | bytes):
    if type(data) is str:
        img = Image.open(data)
        img.show()
    elif type(data) is bytes:
        image_file = io.BytesIO(data)
        img = Image.open(image_file)
        img.show()

class GridImageViewer:
    # States
    image_paths: list[str]
    thumbnails: list = []
    page: int = 0

    # Config-related
    thumb_h: int
    thumb_w: int
    per_page: int = 5

    # UI-Related
    root: tk.Tk
    grid_frame: tk.Frame
    prev_btn: tk.Button
    next_btn: tk.Button

    def __init__(self, img_dir: str, thumb_w=150, thumb_h=150, per_page=5, title="Posted Images"):
        image_paths = [
            os.path.join(img_dir, f)
            for f in os.listdir(img_dir)
            if f.lower().endswith(VALID_IMG_EXT)
        ]
        image_paths.sort(key=lambda p: os.path.getctime(p))
        self.image_paths = image_paths

        self.thumb_h = thumb_h
        self.thumb_w = thumb_w
        self.per_page = per_page

        self.root = tk.Tk()
        self.root.title(title)

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(padx=10, pady=10, expand=True)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack()

        self.prev_btn = tk.Button(nav_frame, text="Previous", command=self.prev_page)
        self.next_btn = tk.Button(nav_frame, text="Next", command=self.next_page)
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        self.next_btn.pack(side=tk.RIGHT, padx=10)

        self.show_page()
        self.root.geometry("800x600")
        self.root.mainloop()

    def show_page(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.thumbnails = []

        start = self.page * self.per_page
        end = start + self.per_page
        paths = self.image_paths[start:end]

        r, c = 0, 0
        for p in paths:
            thumb = make_thumb(p, self.thumb_w, self.thumb_h)
            self.thumbnails.append(thumb)

            btn = tk.Button(
                self.grid_frame,
                image=thumb,
                command=lambda pp=p: self.on_image_clicked(pp)
            )
            btn.grid(row=r, column=c, padx=5, pady=5)

            c += 1
            if c >= 3:
                c = 0
                r += 1

        self.update_nav()

    def next_page(self):
        if (self.page + 1) * self.per_page < len(self.image_paths):
            self.page += 1
        self.show_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
        self.show_page()

    def update_nav(self):
        self.prev_btn.config(state=tk.NORMAL if self.page > 0 else tk.DISABLED)
        self.next_btn.config(
            state=tk.NORMAL if (self.page + 1) * self.per_page < len(self.image_paths) else tk.DISABLED
        )
    
    def on_image_clicked(self, path: str):
        img = Image.open(path)
        img.show()
