import requests
from bs4 import BeautifulSoup
import pickle
import folium
import random

class User:
    def __init__(self, name: str, location: str, posts: int, img_url: str):
        self.name = name
        self.location = location
        self.posts = posts
        self.img_url = img_url
        self.coords = self.get_coordinates()

def save_data(data, filename="users.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_data(filename="users.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


def user_info(users_data: list) -> None:
    for user in users_data:
        print(f"Twój znajomy {user['name']} z miejscowości {user['location']} "
              f"opublikował {user['posts']} postów.")


def add_user(users_data: list) -> None:
    name = input("Podaj imię nowego znajomego: ")
    location = input("Podaj nazwę miejscowości: ")
    posts = int(input("Podaj liczbę postów: "))
    users_data.append({"name": name, "location": location, "posts": posts})
    print("Dodano użytkownika.")


def remove_user(users_data: list) -> None:
    tmp_name = input("Podaj imię użytkownika do usunięcia: ")
    for user in users_data:
        if user['name'] == tmp_name:
            users_data.remove(user)
            print("Usunięto użytkownika.")
            return
    print("Nie znaleziono takiego użytkownika.")


def update_user(users_data: list) -> None:
    tmp_name = input("Podaj imię użytkownika do aktualizacji: ")
    for user in users_data:
        if user['name'] == tmp_name:
            user['name'] = input("Nowe imię: ")
            user['location'] = input("Nowa miejscowość: ")
            user['posts'] = int(input("Nowa liczba postów: "))
            print("Zaktualizowano użytkownika.")
            return
    print("Nie znaleziono takiego użytkownika.")


def get_coordinates(city_name: str) -> list:
    url = f'https://pl.wikipedia.org/wiki/{city_name}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response_html = BeautifulSoup(response.text, 'html.parser')
    latitude = float(response_html.select('.latitude')[1].text.replace(',', '.'))
    longitude = float(response_html.select('.longitude')[1].text.replace(',', '.'))
    return [latitude, longitude]


def get_map(users_data: list) -> None:
    for user in users_data:
        user['img_url'] = f"https://randomuser.me/api/portraits/women/{random.randint(0, 99)}.jpg"

    m = folium.Map(location=[52.0, 19.0], zoom_start=6)

    for user in users_data:
        popup = (
            f"Użytkownik: <b>{user['name']}</b><br>"
            f"Liczba postów: {user['posts']}<br>"
            f"<img src=\"{user['img_url']}\" width=\"100\" alt=\"zdjęcie\"/>"
        )
        folium.Marker(
            location=get_coordinates(user['location']),
            tooltip=f"{user['name']} ({user['location']})",
            popup=popup,
            icon=folium.Icon(icon="user"),
        ).add_to(m)

    m.save("notatnik.html")
    print("Mapa wygenerowana i zapisana jako notatnik.html")


if __name__ == "__main__":
    users_data: list = []
    add_user(users_data)
    remove_user(users_data)