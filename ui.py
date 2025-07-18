import tkinter as tk
from tkinter import ttk, StringVar
import datetime
from weather_api import get_coordinates, get_weather_data, parse_weather_data, get_weather_description
from PIL import Image, ImageTk
import os

class WeatherUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#F0F0F0")
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.location_name = "Mombasa"
        self.current_unit = "celsius" # Default unit
        self.tile_labels = {}
        self.daily_forecast_widgets = []
        self.search_city_var = StringVar(self)
        self.search_city_var.set(self.location_name)
        self.unit_var = StringVar(self, value=self.current_unit) # To manage radiobutton selection

        self.weather_icon_map = {
            0: "0.png",
            1: "1.png",
            2: "2.png",
            3: "3.png",
            45: "45.png",
            48: "45.png",
            51: "51.png",
            53: "51.png",
            55: "51.png",
            56: "51.png",
            57: "51.png",
            61: "61.png",
            63: "61.png",
            65: "61.png",
            66: "61.png",
            67: "61.png",
            71: "71.png",
            73: "71.png",
            75: "71.png",
            77: "71.png",
            80: "80.png",
            81: "80.png",
            82: "80.png",
            85: "71.png",
            86: "71.png",
            95: "95.png",
            96: "95.png",
            99: "95.png"
        }
        self.loaded_icons = {}
        self._load_weather_icons()

        self.setup_styles()
        self.create_widgets()
        self.load_weather_data()

    def _load_weather_icons(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.join(base_dir, "icons")
        
        for code, filename in self.weather_icon_map.items():
            try:
                img_path = os.path.join(icon_dir, filename)
                img = Image.open(img_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.loaded_icons[code] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                self.loaded_icons[code] = None
            except Exception as e:
                self.loaded_icons[code] = None

        try:
            default_icon_path = os.path.join(icon_dir, "default.png")
            default_img = Image.open(default_icon_path)
            default_img = default_img.resize((50, 50), Image.Resampling.LANCZOS)
            self.loaded_icons["default"] = ImageTk.PhotoImage(default_img)
        except FileNotFoundError:
            self.loaded_icons["default"] = None
        except Exception as e:
            self.loaded_icons["default"] = None

    def get_icon_for_code(self, weather_code):
        icon = self.loaded_icons.get(weather_code)
        if icon is None:
            return self.loaded_icons.get("default")
        return icon

    def setup_styles(self):
        self.master.style = ttk.Style()
        self.master.style.theme_use('clam')
        self.master.style.configure("TFrame", background="#F0F0F0")
        self.master.style.configure("Tile.TFrame",
                                    background="#FFFFFF",
                                    borderwidth=0,
                                    relief="flat",
                                    padding=10,
                                    bordercolor="#E0E0E0",
                                    borderradius=8)
        self.master.style.configure("TileLabel.TLabel",
                                    background="#FFFFFF",
                                    foreground="#888888",
                                    font=("Roboto", 10))
        self.master.style.configure("TileValue.TLabel",
                                    background="#FFFFFF",
                                    foreground="#333333",
                                    font=("Roboto", 16, "bold"))
        self.master.style.configure("DailyForecast.TFrame",
                                    background="#FFFFFF",
                                    borderwidth=0,
                                    relief="flat",
                                    padding=(10, 5),
                                    bordercolor="#E0E0E0",
                                    borderradius=8)
        self.master.style.configure("DailyDay.TLabel",
                                    background="#FFFFFF",
                                    foreground="#333333",
                                    font=("Roboto", 11, "bold"))
        self.master.style.configure("DailyTemp.TLabel",
                                    background="#FFFFFF",
                                    foreground="#555555",
                                    font=("Roboto", 11))
        self.master.style.configure("DailyDesc.TLabel",
                                    background="#FFFFFF",
                                    foreground="#888888",
                                    font=("Roboto", 9))
        self.master.style.configure("Search.TEntry",
                                    fieldbackground="#FFFFFF",
                                    foreground="#333333",
                                    font=("Roboto", 12))
        self.master.style.configure("Search.TButton",
                                    background="#4CAF50",
                                    foreground="white",
                                    font=("Roboto", 10, "bold"),
                                    padding=(5, 5))
        self.master.style.map("Search.TButton",
                              background=[('active', '#66BB6A')])
        self.master.style.configure("Unit.TRadiobutton",
                                    background="#F0F0F0",
                                    foreground="#555555",
                                    font=("Roboto", 10, "bold"))
        self.master.style.map("Unit.TRadiobutton",
                              background=[('active', '#F0F0F0')])

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)

        self.search_frame = ttk.Frame(self, style="TFrame")
        self.search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15), padx=5)
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_city_var, style="Search.TEntry")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", self.perform_search)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.perform_search, style="Search.TButton")
        self.search_button.grid(row=0, column=1, sticky="e")

        self.header_frame = ttk.Frame(self, style="TFrame")
        self.header_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.header_frame.grid_rowconfigure(0, weight=1)
        self.header_frame.grid_rowconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=0) # For units toggle

        self.location_label = ttk.Label(self.header_frame, text="Loading Location...",
                                        font=("Roboto", 28, "bold"),
                                        background="#F0F0F0",
                                        foreground="#333333")
        self.location_label.grid(row=0, column=0, pady=(10, 0), sticky="s", columnspan=2)

        self.current_temp_label = ttk.Label(self.header_frame, text="--°C",
                                            font=("Roboto", 60, "bold"),
                                            background="#F0F0F0",
                                            foreground="#333333")
        self.current_temp_label.grid(row=1, column=0, pady=(0, 10), sticky="n")

        self.current_weather_icon_label = ttk.Label(self.header_frame, background="#F0F0F0")
        self.current_weather_icon_label.grid(row=1, column=1, sticky="nw", padx=(0, 10), pady=(0,10))

        # Units Toggle
        self.unit_frame = ttk.Frame(self.header_frame, style="TFrame")
        self.unit_frame.grid(row=1, column=2, sticky="ne", padx=(0,10), pady=(0,10))

        self.celsius_radio = ttk.Radiobutton(self.unit_frame, text="°C", variable=self.unit_var, value="celsius",
                                             command=self.toggle_units, style="Unit.TRadiobutton")
        self.celsius_radio.pack(anchor="e")
        self.fahrenheit_radio = ttk.Radiobutton(self.unit_frame, text="°F", variable=self.unit_var, value="fahrenheit",
                                                command=self.toggle_units, style="Unit.TRadiobutton")
        self.fahrenheit_radio.pack(anchor="e")
        
        self.description_label = ttk.Label(self, text="Loading description...",
                                            font=("Roboto", 16),
                                            background="#F0F0F0",
                                            foreground="#555555")
        self.description_label.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky="n")

        self.daily_forecast_container = ttk.Frame(self, style="DailyForecast.TFrame")
        self.daily_forecast_container.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=5)

        self.tiles_frame = ttk.Frame(self, style="TFrame")
        self.tiles_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10), padx=5)
        self.tiles_frame.grid_columnconfigure(0, weight=1)
        self.tiles_frame.grid_columnconfigure(1, weight=1)

        self.tile_labels["rain_rate"] = self.create_tile(self.tiles_frame, "Rain Rate", "0 mm", row=0, col=0)
        self.tile_labels["humidity"] = self.create_tile(self.tiles_frame, "Humidity", "0%", row=0, col=1)
        self.tile_labels["current_temp_tile"] = self.create_tile(self.tiles_frame, "Feels Like", "--°C", row=1, col=0)
        self.tile_labels["uv_index"] = self.create_tile(self.tiles_frame, "UV Index", "--", row=1, col=1)
        self.tile_labels["air_quality"] = self.create_tile(self.tiles_frame, "Air Quality (PM2.5)", "--", row=2, col=0)
        self.tile_labels["sunrise"] = self.create_tile(self.tiles_frame, "Sunrise", "--:-- AM", row=2, col=1)
        self.tile_labels["sunset"] = self.create_tile(self.tiles_frame, "Sunset", "--:-- PM", row=3, col=0)
        self.tile_labels["wind_speed"] = self.create_tile(self.tiles_frame, "Wind Speed", "-- km/h", row=3, col=1)

    def create_tile(self, parent_frame, label_text, value_text, row, col):
        tile_frame = ttk.Frame(parent_frame, style="Tile.TFrame")
        tile_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        tile_frame.grid_columnconfigure(0, weight=1)
        label = ttk.Label(tile_frame, text=label_text, style="TileLabel.TLabel")
        label.pack(pady=(0, 2), anchor="w")
        value = ttk.Label(tile_frame, text=value_text, style="TileValue.TLabel")
        value.pack(pady=(0, 0), anchor="w")
        return value

    def clear_daily_forecast(self):
        for widget in self.daily_forecast_widgets:
            widget.destroy()
        self.daily_forecast_widgets.clear()

    def set_loading_state(self):
        self.master.config(cursor="watch")
        self.location_label.config(text="Loading...")
        self.current_temp_label.config(text="--°")
        self.description_label.config(text="Fetching weather data...")
        self.current_weather_icon_label.config(image=self.get_icon_for_code(None))
        self.current_weather_icon_label.image = self.get_icon_for_code(None)
        self.clear_daily_forecast()
        for key in self.tile_labels:
            self.tile_labels[key].config(text="--")
        self.search_button.config(state="disabled")
        self.search_entry.config(state="disabled")
        self.celsius_radio.config(state="disabled")
        self.fahrenheit_radio.config(state="disabled")
        self.update_idletasks()

    def reset_ui_state(self):
        self.master.config(cursor="")
        self.search_button.config(state="enabled")
        self.search_entry.config(state="enabled")
        self.celsius_radio.config(state="enabled")
        self.fahrenheit_radio.config(state="enabled")

    def toggle_units(self):
        selected_unit = self.unit_var.get()
        if self.current_unit != selected_unit:
            self.current_unit = selected_unit
            self.set_loading_state()
            self.after(100, self.load_weather_data)

    def perform_search(self, event=None):
        search_term = self.search_city_var.get().strip()
        if search_term:
            self.location_name = search_term
            self.set_loading_state()
            self.after(100, self.load_weather_data)
        else:
            self.description_label.config(text="Please enter a city name.")
            self.reset_ui_state()

    def load_weather_data(self):
        try:
            lat, lon, display_location = get_coordinates(self.location_name)
            if lat and lon:
                weather_data, air_quality_data = get_weather_data(lat, lon, timezone="auto", temperature_unit=self.current_unit)
                if weather_data and air_quality_data:
                    parsed_data = parse_weather_data(weather_data, air_quality_data)
                    self.update_ui(parsed_data, display_location)
                else:
                    self.description_label.config(text="Could not fetch weather data. API issue or no data.")
                    self.current_temp_label.config(text="--°")
                    self.current_weather_icon_label.config(image=self.get_icon_for_code(None))
                    self.current_weather_icon_label.image = self.get_icon_for_code(None)
                    self.clear_daily_forecast()
                    for key in self.tile_labels:
                        self.tile_labels[key].config(text="--")
            else:
                self.location_label.config(text=f"Location not found.")
                self.description_label.config(text="Please check location name or try another.")
                self.current_temp_label.config(text="--°")
                self.current_weather_icon_label.config(image=self.get_icon_for_code(None))
                self.current_weather_icon_label.image = self.get_icon_for_code(None)
                self.clear_daily_forecast()
                for key in self.tile_labels:
                    self.tile_labels[key].config(text="--")
        except Exception as e:
            self.description_label.config(text=f"An error occurred: {e}")
            self.current_temp_label.config(text="--°")
            self.current_weather_icon_label.config(image=self.get_icon_for_code(None))
            self.current_weather_icon_label.image = self.get_icon_for_code(None)
            self.clear_daily_forecast()
            for key in self.tile_labels:
                self.tile_labels[key].config(text="--")
        finally:
            self.reset_ui_state()

    def update_ui(self, parsed_data, display_location):
        current = parsed_data['current']
        daily = parsed_data['daily']
        air_quality = parsed_data['air_quality']

        unit_symbol = "°C" if self.current_unit == "celsius" else "°F"

        self.location_label.config(text=display_location.split(',')[0].strip())
        self.current_temp_label.config(text=f"{current['temp']:.0f}{unit_symbol}")
        self.description_label.config(text=current['description'].capitalize())

        current_weather_code = current.get('weather_code')
        current_icon = self.get_icon_for_code(current_weather_code)
        self.current_weather_icon_label.config(image=current_icon)
        self.current_weather_icon_label.image = current_icon

        self.clear_daily_forecast()
        self.daily_forecast_container.grid_columnconfigure("all", weight=0)

        for i, day in enumerate(daily[:7]):
            day_frame = ttk.Frame(self.daily_forecast_container, style="TFrame", padding=5)
            day_frame.grid(row=0, column=i, sticky="nsew", padx=2, pady=5)
            self.daily_forecast_container.grid_columnconfigure(i, weight=1)
            
            day_name = day['dt'].strftime('%a')
            temp_max = f"{day['temp_max']:.0f}" if day['temp_max'] is not None else "--"
            temp_min = f"{day['temp_min']:.0f}" if day['temp_min'] is not None else "--"
            description = day['description']
            
            daily_weather_code = day.get('weather_code')
            daily_icon = self.get_icon_for_code(daily_weather_code)
            
            icon_label = ttk.Label(day_frame, image=daily_icon, background="#FFFFFF")
            icon_label.image = daily_icon
            icon_label.pack()

            ttk.Label(day_frame, text=day_name, style="DailyDay.TLabel").pack()
            ttk.Label(day_frame, text=f"{temp_max}{unit_symbol}/{temp_min}{unit_symbol}", style="DailyTemp.TLabel").pack()
            ttk.Label(day_frame, text=description, style="DailyDesc.TLabel", wraplength=70, justify=tk.CENTER).pack()
            
            self.daily_forecast_widgets.append(day_frame)

        self.tile_labels["rain_rate"].config(text=f"{current['rain_rate']:.1f} mm" if current['rain_rate'] is not None else "0.0 mm")
        self.tile_labels["humidity"].config(text=f"{current['humidity']:.0f}%" if current['humidity'] is not None else "--%")
        self.tile_labels["current_temp_tile"].config(text=f"{current['feels_like']:.0f}{unit_symbol}" if current['feels_like'] is not None else "--°")
        self.tile_labels["uv_index"].config(text=f"{current['uvi']:.1f}" if current['uvi'] is not None else "--")

        if air_quality and air_quality.get('pm2_5') is not None:
            self.tile_labels["air_quality"].config(text=f"{air_quality['pm2_5']:.1f} µg/m³")
        else:
            self.tile_labels["air_quality"].config(text="N/A")

        sunrise_time = current['sunrise'].strftime('%I:%M %p') if current['sunrise'] else "--:-- AM"
        sunset_time = current['sunset'].strftime('%I:%M %p') if current['sunset'] else "--:-- PM"
        self.tile_labels["sunrise"].config(text=sunrise_time)
        self.tile_labels["sunset"].config(text=sunset_time)
        self.tile_labels["wind_speed"].config(text=f"{current.get('wind_speed', '--'):.1f} km/h")