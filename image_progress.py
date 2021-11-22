import threading
import time
import tkinter as tk
from pathlib import Path
from random import choice
from tkinter import ttk

from PIL import Image, ImageOps, ImageTk
from tqdm import tqdm


class ThreadingWindow(threading.Thread):
    """Wrapper class for TK that allows using it in a thread an call actions outsidenthe mainoop"""

    def __init__(self, width, height, *args, **kwargs):
        threading.Thread.__init__(self)
        self.start()
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

    def update_image(self, base_image):
        """Update the window canvas with a new image"""
        image = self._fit_image(Image.open(base_image))
        self.canvas.itemconfig(self.image_on_canvas, image=image)
    
    def _fit_image(self, image):
        """Fit the image to the window size"""
        fitted_image = ImageOps.fit(image, (self._width, self._height))
        self.photo_image = ImageTk.PhotoImage(fitted_image)
        return self.photo_image


class image_progress(tqdm):
    """tqdm implementation that update the image in the window
    
    It is in lower snake case to mimic tqdm progress
    """

    def __init__(self, base_image, width, height, show_progress_window=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_image = base_image
        
        self._with_window = show_progress_window
        
        if self._with_window:
            self._base_image = str(Path(base_image).absolute())
            self.app = ThreadingWindow(width=width, height=height)

    def update(self,n=1):
        super().update(n=n)
        
        if self._with_window:
            self.app.update_image(self._base_image)

__all__ = ["image_progress"]
