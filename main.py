from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup

# --- GLOBAL DATA LISTS ---
stations = []      # jednostki straży
firefighters = []  # pracownicy
fire_events = []   # interwencje

root = Tk()
root.title("Fire Department Manager")
root.geometry("1200x800")

# --- FRAMES ---
frame_list = Frame(root)
frame_form = Frame(root)
frame_details = Frame(root)
frame_map = Frame(root)

frame_list.grid(row=0, column=0)
frame_form.grid(row=0, column=1)
frame_details.grid(row=1, column=0, columnspan=2)
frame_map.grid(row=2, column=0, columnspan=2)

# --- MAP ---
map_widget = tkintermapview.TkinterMapView(frame_map, width=1200, height=600, corner_radius=0)
map_widget.set_position(52.0, 19.0)
map_widget.set_zoom(6)
map_widget.grid(row=0, column=0)

# ------------------------------------------------------
#                   DATA MODELS
# ------------------------------------------------------

class BaseGeoObject:
    def get_coordinates(self, address: str):
        try:
            url = f'https://pl.wikipedia.org/wiki/{address.replace(" ", "_")}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            html = BeautifulSoup(response.text, 'html.parser')
            lat = float(html.select('.latitude')[-1].text.replace(',', '.'))
            lon = float(html.select('.longitude')[-1].text.replace(',', '.'))
            return [lat, lon]
        except:
            return [52.0, 21.0]  # fallback (Warszawa)


class FireStation(BaseGeoObject):
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
        self.coords = self.get_coordinates(address)
        self.marker = map_widget.set_marker(self.coords[0], self.coords[1], text=self.name)


class Firefighter(BaseGeoObject):
    def __init__(self, name: str, rank: str, home_location: str, station_index: int):
        self.name = name
        self.rank = rank
        self.home_location = home_location
        self.station_index = station_index
        self.coords = self.get_coordinates(home_location)
        self.marker = None


class FireEvent(BaseGeoObject):
    def __init__(self, address: str, date: str, station_index: int):
        self.address = address
        self.date = date
        self.station_index = station_index
        self.coords = self.get_coordinates(address)
        self.marker = None

# ------------------------------------------------------
#               LIST AND DETAILS REFRESH
# ------------------------------------------------------

def refresh_list():
    list_box.delete(0, END)
    for s in stations:
        list_box.insert(END, f"Jednostka: {s.name} — {s.address}")


def show_details():
    i = list_box.index(ACTIVE)
    if i < 0 or i >= len(stations):
        return
    station = stations[i]
    label_details_name_value.config(text=station.name)
    label_details_address_value.config(text=station.address)
    map_widget.set_position(station.coords[0], station.coords[1])
    map_widget.set_zoom(13)

# ------------------------------------------------------
#                    ADD STATION
# ------------------------------------------------------

def add_station():
    name = entry_name.get()
    address = entry_address.get()
    if name == '' or address == '':
        return

    s = FireStation(name, address)
    stations.append(s)
    refresh_list()

    entry_name.delete(0, END)
    entry_address.delete(0, END)

# ------------------------------------------------------
#                    DELETE STATION
# ------------------------------------------------------

def delete_station():
    i = list_box.index(ACTIVE)
    if i < 0 or i >= len(stations):
        return

    stations[i].marker.delete()
    stations.pop(i)
    refresh_list()

# ------------------------------------------------------
#                    GUI ELEMENTS
# ------------------------------------------------------

# LIST SECTION
label_list = Label(frame_list, text="Lista jednostek straży pożarnej")
label_list.grid(row=0, column=0, columnspan=2)

list_box = Listbox(frame_list, width=50)
list_box.grid(row=1, column=0, columnspan=2)

button_show = Button(frame_list, text="Pokaż szczegóły", command=show_details)
button_show.grid(row=2, column=0)

button_delete = Button(frame_list, text="Usuń jednostkę", command=delete_station)
button_delete.grid(row=2, column=1)

# FORM SECTION
label_form = Label(frame_form, text="Dodaj nową jednostkę")
label_form.grid(row=0, column=0, columnspan=2)

label_name = Label(frame_form, text="Nazwa jednostki:")
label_name.grid(row=1, column=0, sticky=W)
entry_name = Entry(frame_form)
entry_name.grid(row=1, column=1)

label_address = Label(frame_form, text="Adres jednostki:")
label_address.grid(row=2, column=0, sticky=W)
entry_address = Entry(frame_form)
entry_address.grid(row=2, column=1)

button_add = Button(frame_form, text="Dodaj jednostkę", command=add_station)
button_add.grid(row=3, column=0, columnspan=2)

# DETAILS SECTION
Label(frame_details, text="Szczegóły jednostki:").grid(row=0, column=0)

Label(frame_details, text="Nazwa:").grid(row=1, column=0)
label_details_name_value = Label(frame_details, text="...")
label_details_name_value.grid(row=1, column=1)

Label(frame_details, text="Adres:").grid(row=1, column=2)
label_details_address_value = Label(frame_details, text="...")
label_details_address_value.grid(row=1, column=3)

root.mainloop()
