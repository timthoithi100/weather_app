import tkinter as tk
from ui import WeatherUI

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modern Weather App")
        self.geometry("800x700")
        self.minsize(600, 700)
        self.configure(bg="#F0F0F0")
        try:
            self.option_add("*Font", "Roboto 10")
        except tk.TclError:
            self.option_add("*Font", "Helvetica 10")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.weather_ui = WeatherUI(self)
        self.weather_ui.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()