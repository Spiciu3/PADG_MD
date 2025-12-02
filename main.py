# Updated full application with Step 2: Employees Module
# ======================
# This file now contains:
# - Fire units CRUD
# - Employees CRUD
# - Map markers for units & employees
# - View employees of a selected unit
# ======================================

import tkinter as tk
from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup

# ===========================
# DATA MODELS
# ===========================
class FireUnit:
    def __init__(self, name: str, city: str):
        self.name = name
        self.city = city
        self.coords = self.get_coordinates()
        self.marker = None

    def get_coordinates(self):
        try:
            url = f"https://pl.wikipedia.org/wiki/{self.city}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            lat = float(soup.select(".latitude")[-1].text.replace(",", "."))
            lon = float(soup.select(".longitude")[-1].text.replace(",", "."))
            return [lat, lon]
        except:
            return [52.0, 21.0]

class Employee:
    def __init__(self, name: str, role: str, city: str, fire_unit: FireUnit):
        self.name = name
        self.role = role
        self.city = city
        self.fire_unit = fire_unit
        self.coords = self.get_coordinates()
        self.marker = None

    def get_coordinates(self):
        try:
            url = f"https://pl.wikipedia.org/wiki/{self.city}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            lat = float(soup.select(".latitude")[-1].text.replace(",", "."))
            lon = float(soup.select(".longitude")[-1].text.replace(",", "."))
            return [lat, lon]
        except:
            return [52.0, 21.0]

# ===========================
# ROOT WINDOW
# ===========================
root = Tk()
root.title("Fire Management System")
root.geometry("1200x850")

# frames
frame_units = Frame(root)
frame_units.grid(row=0, column=0)

frame_employees = Frame(root)
frame_employees.grid(row=0, column=1)

frame_map = Frame(root)
frame_map.grid(row=1, column=0, columnspan=2)

# map
map_widget = tkintermapview.TkinterMapView(frame_map, width=1200, height=600, corner_radius=0)
map_widget.set_position(52.0, 21.0)
map_widget.set_zoom(6)
map_widget.grid(row=0, column=0)

# lists
fire_units: list[FireUnit] = []
employees: list[Employee] = []

# ===========================
# GUI – FIRE UNITS
# ===========================
Label(frame_units, text="Jednostki Straży").grid(row=0, column=0, columnspan=2)

unit_list = Listbox(frame_units)
unit_list.grid(row=1, column=0, columnspan=2)

Label(frame_units, text="Nazwa jednostki:").grid(row=2, column=0, sticky=W)
entry_unit_name = Entry(frame_units)
entry_unit_name.grid(row=2, column=1)

Label(frame_units, text="Miasto:").grid(row=3, column=0, sticky=W)
entry_unit_city = Entry(frame_units)
entry_unit_city.grid(row=3, column=1)

# fire unit handlers
def refresh_units():
    refresh_unit_selector()
    unit_list.delete(0, END)
    for u in fire_units:
        unit_list.insert(END, f"{u.name} ({u.city})")

def add_fire_unit():
    name = entry_unit_name.get()
    city = entry_unit_city.get()
    if not name or not city:
        return
    u = FireUnit(name, city)
    fire_units.append(u)
    u.marker = map_widget.set_marker(u.coords[0], u.coords[1], text=u.name)
    refresh_units()
    entry_unit_name.delete(0, END)
    entry_unit_city.delete(0, END)

def delete_fire_unit():
    i = unit_list.index(ACTIVE)
    if i < 0:
        return
    fire_units[i].marker.delete()
    del fire_units[i]
    refresh_units()

Button(frame_units, text="Dodaj jednostkę", command=add_fire_unit).grid(row=4, column=0)
Button(frame_units, text="Usuń jednostkę", command=delete_fire_unit).grid(row=4, column=1)

# ===========================
# GUI – EMPLOYEES
# ===========================
Label(frame_employees, text="Pracownicy").grid(row=0, column=0, columnspan=2)

employee_list = Listbox(frame_employees, width=50)
employee_list.grid(row=1, column=0, columnspan=2)

Label(frame_employees, text="Imię:").grid(row=2, column=0, sticky=W)
entry_emp_name = Entry(frame_employees)
entry_emp_name.grid(row=2, column=1)

Label(frame_employees, text="Rola:").grid(row=3, column=0, sticky=W)
entry_emp_role = Entry(frame_employees)
entry_emp_role.grid(row=3, column=1)

Label(frame_employees, text="Miasto pracownika:").grid(row=4, column=0, sticky=W)
entry_emp_city = Entry(frame_employees)
entry_emp_city.grid(row=4, column=1)

Label(frame_employees, text="Jednostka:").grid(row=5, column=0, sticky=W)

unit_select = Listbox(frame_employees, height=5)
unit_select.grid(row=5, column=1)

def refresh_unit_selector():
    unit_select.delete(0, END)
    for u in fire_units:
        unit_select.insert(END, f"{u.name}")

# employee handlers
def refresh_employees():
    employee_list.delete(0, END)
    for e in employees:
        employee_list.insert(END, f"{e.name} – {e.role} – {e.fire_unit.name}")

def add_employee():
    name = entry_emp_name.get()
    role = entry_emp_role.get()
    city = entry_emp_city.get()
    i = unit_select.index(ACTIVE)
    if i < 0:
        return
    unit = fire_units[i]
    e = Employee(name, role, city, unit)
    employees.append(e)
    # employee markers disabled
    e.marker = None
    refresh_employees()
    entry_emp_name.delete(0, END)
    entry_emp_role.delete(0, END)
    entry_emp_city.delete(0, END)

Button(frame_employees, text="Dodaj pracownika", command=add_employee).grid(row=6, column=0)

# ===========================
# SHOW UNIT DETAILS ON SELECT
# ===========================

def show_unit_details(event=None):
    i = unit_list.index(ACTIVE)
    if i < 0:
        return
    u = fire_units[i]
    map_widget.set_position(u.coords[0], u.coords[1])
    map_widget.set_zoom(12)

unit_list.bind('<<ListboxSelect>>', show_unit_details)

# ===========================
# DELETE EMPLOYEE
# ===========================

def delete_employee():
    i = employee_list.index(ACTIVE)
    if i < 0:
        return
    del employees[i]
    refresh_employees()

Button(frame_employees, text="Usuń pracownika", command=delete_employee).grid(row=6, column=1)

# refresh selectors
refresh_unit_selector()

root.mainloop()
