import random
import string
from datetime import datetime, timedelta
from .. import loader, utils

@loader.tds
class FunPasta(loader.Module):
    """🎭 Генератор данных FUNCRMP!"""
    
    strings = {"name": "FakeID"}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    @loader.command()
    async def pasta(self, message):
        """Сгенерировать полные фейковые данные"""
        # Основные данные
        first_name = random.choice([
            "James", "John", "Robert", "Michael", "William",
            "David", "Richard", "Joseph", "Thomas", "Charles",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth",
            "Barbara", "Susan", "Jessica", "Sarah", "Karen"
        ])
        
        last_name = random.choice([
            "Smith", "Johnson", "Williams", "Brown", "Jones",
            "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"
        ])
        
        # Страна и город
        countries = ["USA", "UK", "Canada", "Australia", "Germany", "France"]
        country = random.choice(countries)
        
        cities = {
            "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "UK": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds"],
            "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
            "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
            "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
            "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"]
        }
        
        city = random.choice(cities[country])
        
        # Адрес
        street = random.choice(["Main St", "Oak St", "Maple Ave", "Park Rd", "Broadway"])
        house = random.randint(100, 9999)
        apartment = f"Apt {random.randint(1, 500)}"
        
        # Телефон
        phone = self._generate_phone(country)
        
        # Email
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,99)}@example.com"
        
        # Банковская карта
        card = self._generate_credit_card()
        
        # Дата рождения
        birth_date = self._generate_birth_date()
        
        # IP адрес
        ip = self._generate_ip(country)
        
        # Координаты
        lat, lon = self._generate_coordinates(country, city)
        
        # Формирование результата
        result = f"""
🎭 **FAKE IDENTITY GENERATED**

👤 **PERSONAL INFO:**
Name: {first_name} {last_name}
Birth Date: {birth_date}
Age: {datetime.now().year - int(birth_date.split('-')[0])}

📍 **LOCATION:**
Country: {country}
City: {city}
Address: {house} {street}, {apartment}
Coordinates: {lat:.6f}, {lon:.6f}

📞 **CONTACTS:**
Phone: {phone}
Email: {email}
IP Address: {ip}

💳 **FINANCIAL:**
Bank Card: {card['number']}
Expires: {card['expiry']}
CVV: {card['cvv']}
Bank: {card['bank']}

🌐 **DIGITAL:**
Username: {first_name.lower()}_{last_name.lower()}
Password: {self._generate_password()}
User Agent: {self._generate_user_agent()}

📅 **GENERATED:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        await utils.answer(message, result)
    
    def _generate_phone(self, country):
        """Генерация номера телефона"""
        formats = {
            "USA": f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            "UK": f"+44 {random.randint(7000,7999)} {random.randint(100000,999999)}",
            "Canada": f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            "Australia": f"+61 {random.randint(400,499)} {random.randint(100000,999999)}",
            "Germany": f"+49 {random.randint(151,179)} {random.randint(1000000,9999999)}",
            "France": f"+33 {random.randint(6,7)} {random.randint(10000000,99999999)}",
        }
        return formats.get(country, f"+{random.randint(1,99)} {random.randint(1000000000,9999999999)}")
    
    def _generate_credit_card(self):
        """Генерация банковской карты (Luhn algorithm)"""
        banks = [
            {"name": "Visa", "prefix": "4", "length": 16},
            {"name": "MasterCard", "prefix": "5", "length": 16},
            {"name": "American Express", "prefix": "3", "length": 15},
        ]
        
        bank = random.choice(banks)
        
        # Генерация номера с алгоритмом Луна
        card_number = bank['prefix']
        for _ in range(bank['length'] - 1):
            card_number += str(random.randint(0, 9))
        
        # Применяем алгоритм Луна
        card_number = self._luhn_checksum(card_number)
        
        # Срок действия
        month = random.randint(1, 12)
        year = random.randint(2024, 2030)
        
        # CVV
        cvv = str(random.randint(100, 999))
        
        return {
            'number': ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)]),
            'expiry': f"{month:02d}/{year}",
            'cvv': cvv,
            'bank': bank['name']
        }
    
    def _luhn_checksum(self, card_number):
        """Алгоритм Луна для валидного номера карты"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        
        # Вычисляем контрольную цифру
        checksum %= 10
        if checksum != 0:
            checksum = 10 - checksum
        
        # Заменяем последнюю цифру
        card_number = card_number[:-1] + str(checksum)
        return card_number
    
    def _generate_birth_date(self):
        """Генерация даты рождения (18-65 лет)"""
        current_year = datetime.now().year
        year = random.randint(current_year - 65, current_year - 18)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    def _generate_ip(self, country):
        """Генерация IP адреса"""
        ip_ranges = {
            "USA": ["104.", "107.", "108.", "162.", "198."],
            "UK": ["81.", "82.", "86.", "92.", "146."],
            "Canada": ["24.", "70.", "72.", "96.", "142."],
            "Australia": ["101.", "103.", "110.", "112.", "120."],
            "Germany": ["78.", "79.", "85.", "91.", "93."],
            "France": ["78.", "79.", "86.", "90.", "91."],
        }
        
        prefix = random.choice(ip_ranges.get(country, ["192.", "10."]))
        return f"{prefix}{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    
    def _generate_coordinates(self, country, city):
        """Генерация координат"""
        # Примерные координаты столиц
        capitals = {
            "USA": [38.9072, -77.0369],  # Washington DC
            "UK": [51.5074, -0.1278],    # London
            "Canada": [45.4215, -75.6972], # Ottawa
            "Australia": [-35.2802, 149.1310], # Canberra
            "Germany": [52.5200, 13.4050], # Berlin
            "France": [48.8566, 2.3522],   # Paris
        }
        
        if city in capitals:
            lat, lon = capitals[city]
        elif country in capitals:
            lat, lon = capitals[country]
        else:
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)
        
        # Немного рандомизируем
        lat += random.uniform(-1, 1)
        lon += random.uniform(-1, 1)
        
        return lat, lon
    
    def _generate_password(self):
        """Генерация пароля"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(12))
    
    def _generate_user_agent(self):
        """Генерация User-Agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        ]
        return random.choice(agents)