import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tqdm import tqdm
from random import choice
from PIL import Image, ImageTk, ImageOps

class App(threading.Thread):

    def __init__(self, base_image, width, height, *args, **kwargs):
        threading.Thread.__init__(self)
        self.start()
        self._base_image = base_image
        self._height = 800
        self._ratio = width / height
        self._width = int(self._height * self._ratio)

    def callback(self):
        self.close()

    def close(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.geometry(f"{self._width}x{self._height}")

        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        image = self._fit_image(Image.new("RGB", (self._width, self._height), (255, 255, 255)))
        self.canvas = tk.Canvas(self.root, height=self._height, width=self._width)
        self.canvas.pack()
        self.image_on_canvas = self.canvas.create_image((0, 0), anchor=tk.NW, image=image)

        self.root.mainloop()

    def update_image(self):
        image = self._fit_image(Image.open(self._base_image))
        self.canvas.itemconfig(self.image_on_canvas, image=image)
    
    def _fit_image(self, image):
        fitted_image = ImageOps.fit(image, (self._width, self._height))
        self.photo_image = ImageTk.PhotoImage(fitted_image)
        return self.photo_image

class image_progress_tdqm(tqdm):

    def __init__(self, base_image, width, height, show_progress_window=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._with_window = show_progress_window
        if self._with_window:
            self._base_image = str(Path(base_image).absolute())
            self.app = App(base_image=base_image, width=width, height=height)

    def update(self,n=1):
        super().update(n=n)
        
        if self._with_window:
            self.app.update_image()

image_progress = image_progress_tdqm

__all__ = ["image_progress"]


