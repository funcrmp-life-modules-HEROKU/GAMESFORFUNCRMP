"""
    🏠 FunAddress - Генератор случайных адресов
    
    Этот модуль генерирует случайные адреса для разных стран
    с координатами, IP-адресами и дополнительной информацией.
    
"""

__version__ = (1, 0, 0)

# meta developer: @zymoyhold
# requires: none

import random
from .. import loader, utils

@loader.tds
class FunAddressMod(loader.Module):
    """FUNADDRESS - генератор адресов"""
    
    strings = {"name": "FunAddress"}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    @loader.command()
    async def address(self, message):
        """Случайный адрес"""
        country = random.choice(["Россия", "Украина", "США"])
        
        if country == "Россия":
            address = self._get_russian_address()
        elif country == "Украина":
            address = self._get_ukrainian_address()
        else:
            address = self._get_usa_address()
        
        await utils.answer(message, address)
    
    def _get_russian_address(self):
        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
        city = random.choice(cities)
        street = random.choice(["Ленина", "Советская", "Мира", "Центральная", "Молодежная"])
        house = random.randint(1, 150)
        apartment = random.randint(1, 250)
        
        coords = {
            "Москва": [55.7558, 37.6173],
            "Санкт-Петербург": [59.9343, 30.3351],
            "Новосибирск": [55.0084, 82.9357],
            "Екатеринбург": [56.8389, 60.6057],
            "Казань": [55.7961, 49.1064],
        }
        
        if city in coords:
            lat, lon = coords[city]
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
        else:
            lat = random.uniform(55.0, 56.0)
            lon = random.uniform(37.0, 38.0)
        
        ip = f"77.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        
        districts = ['Центральный', 'Северный', 'Южный', 'Западный', 'Восточный']
        district = random.choice(districts)
        
        text = f"""
СЛУЧАЙНЫЙ АДРЕС В РОССИИ

Город: {city}
Адрес: ул. {street}, д. {house}, кв. {apartment}
Индекс: {random.randint(100000, 199999)}
Страна: Россия

Координаты:
Широта: {lat:.6f}
Долгота: {lon:.6f}
Карты: https://maps.google.com/?q={lat},{lon}

IP адрес: {ip}
Район: {district}

Автор: @zymoyhold
Спонсор: @funcrmp
"""
        return text
    
    def _get_ukrainian_address(self):
        cities = ["Киев", "Харьков", "Одесса", "Днепр", "Львов"]
        city = random.choice(cities)
        street = random.choice(["Хрещатик", "Соборна", "Незалежності", "Шевченка", "Франка"])
        house = random.randint(1, 150)
        apartment = random.randint(1, 250)
        
        coords = {
            "Киев": [50.4501, 30.5234],
            "Харьков": [49.9935, 36.2304],
            "Одесса": [46.4825, 30.7233],
            "Днепр": [48.4647, 35.0462],
            "Львов": [49.8425, 24.0322],
        }
        
        if city in coords:
            lat, lon = coords[city]
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
        else:
            lat = random.uniform(48.0, 50.0)
            lon = random.uniform(30.0, 36.0)
        
        ip = f"91.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        
        districts = ['Центральный', 'Подільський', 'Шевченківський', 'Дарницький', 'Соломянський']
        district = random.choice(districts)
        
        text = f"""
СЛУЧАЙНЫЙ АДРЕС В УКРАИНЕ

Місто: {city}
Адреса: вул. {street}, буд. {house}, кв. {apartment}
Поштовий індекс: {random.randint(1000, 99999):05d}
Країна: Україна

Координати:
Широта: {lat:.6f}
Довгота: {lon:.6f}
Карти: https://maps.google.com/?q={lat},{lon}

IP адреса: {ip}
Район: {district}

Автор: @zymoyhold
Спонсор: @funcrmp
"""
        return text
    
    def _get_usa_address(self):
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        city = random.choice(cities)
        street = random.choice(["Main St", "Broadway", "Park Ave", "Washington St", "Maple St"])
        house = random.randint(100, 9999)
        apartment = f"Apt {random.randint(1, 500)}"
        
        coords = {
            "New York": [40.7128, -74.0060],
            "Los Angeles": [34.0522, -118.2437],
            "Chicago": [41.8781, -87.6298],
            "Houston": [29.7604, -95.3698],
            "Phoenix": [33.4484, -112.0740],
        }
        
        if city in coords:
            lat, lon = coords[city]
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
        else:
            lat = random.uniform(25.0, 49.0)
            lon = random.uniform(-125.0, -66.0)
        
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        
        address_line = f"{house} {street}, {apartment}"
        
        text = f"""
RANDOM ADDRESS IN USA

City: {city}
Address: {address_line}
ZIP Code: {random.randint(10000, 99999)}
Country: United States

Coordinates:
Latitude: {lat:.6f}
Longitude: {lon:.6f}
Maps: https://maps.google.com/?q={lat},{lon}

IP Address: {ip}
Area: {random.choice(['Downtown', 'Uptown', 'Midtown', 'Suburbs', 'Financial District'])}

Author: @zymoyhold
Sponsor: @funcrmp
"""
        return text