"""
    🎭 FunPasta - Реалистичный генератор фейковых данных
    Исправленная логика с реалистичными данными
"""

__version__ = (2, 1, 0)

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from .. import loader, utils

@loader.tds
class FunPastaMod(loader.Module):
    """🎭 Реалистичный генератор фейковых данных"""
    
    strings = {
        "name": "FunPasta",
        "help": "Генерация реалистичных фейковых данных",
        "generated": "🎭 Сгенерирована новая личность\n\n{data}",
        "error": "❌ Ошибка генерации",
        "clear": "✅ Кэш модуля очищен"
    }
    
    # Реалистичные данные с логической согласованностью
    RUSSIAN_NAMES = {
        "male": [
            "Александр", "Алексей", "Андрей", "Антон", "Артем",
            "Борис", "Вадим", "Валентин", "Валерий", "Василий",
            "Виктор", "Виталий", "Владимир", "Владислав", "Вячеслав",
            "Геннадий", "Георгий", "Григорий", "Даниил", "Денис",
            "Дмитрий", "Евгений", "Егор", "Иван", "Игорь",
            "Илья", "Кирилл", "Константин", "Леонид", "Максим",
            "Михаил", "Никита", "Николай", "Олег", "Павел",
            "Петр", "Роман", "Сергей", "Станислав", "Тимур"
        ],
        "female": [
            "Александра", "Алена", "Алина", "Анастасия", "Ангелина",
            "Анна", "Валентина", "Валерия", "Варвара", "Вера",
            "Вероника", "Виктория", "Галина", "Дарья", "Диана",
            "Ева", "Евгения", "Екатерина", "Елена", "Елизавета",
            "Ирина", "Карина", "Кира", "Кристина", "Лариса",
            "Лидия", "Любовь", "Людмила", "Марина", "Мария",
            "Надежда", "Наталья", "Оксана", "Ольга", "Полина",
            "Светлана", "София", "Татьяна", "Юлия", "Яна"
        ]
    }
    
    # Реальные русские фамилии с правильными окончаниями
    RUSSIAN_SURNAMES = {
        "male": [
            "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев",
            "Петров", "Соколов", "Михайлов", "Новиков", "Федоров",
            "Морозов", "Волков", "Алексеев", "Лебедев", "Семенов",
            "Егоров", "Павлов", "Козлов", "Степанов", "Николаев",
            "Орлов", "Андреев", "Макаров", "Никитин", "Захаров",
            "Зайцев", "Соловьев", "Борисов", "Яковлев", "Григорьев",
            "Романов", "Воробьев", "Сергеев", "Кириллов", "Максимов",
            "Поляков", "Виноградов", "Ковалев", "Белов", "Медведев"
        ],
        "female": [
            "Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева",
            "Петрова", "Соколова", "Михайлова", "Новикова", "Федорова",
            "Морозова", "Волкова", "Алексеева", "Лебедева", "Семенова",
            "Егорова", "Павлова", "Козлова", "Степанова", "Николаева",
            "Орлова", "Андреева", "Макарова", "Никитина", "Захарова",
            "Зайцева", "Соловьева", "Борисова", "Яковлева", "Григорьева",
            "Романова", "Воробьева", "Сергеева", "Кириллова", "Максимова",
            "Полякова", "Виноградова", "Ковалева", "Белова", "Медведева"
        ]
    }
    
    RUSSIAN_PATRONYMICS = {
        "male": [
            "Александрович", "Алексеевич", "Анатольевич", "Андреевич", "Антонович",
            "Аркадьевич", "Арсеньевич", "Артемович", "Борисович", "Вадимович",
            "Валентинович", "Валерьевич", "Васильевич", "Викторович", "Витальевич",
            "Владимирович", "Владиславович", "Вячеславович", "Геннадьевич", "Георгиевич",
            "Григорьевич", "Даниилович", "Денисович", "Дмитриевич", "Евгеньевич",
            "Егорович", "Иванович", "Игоревич", "Ильич", "Кириллович"
        ],
        "female": [
            "Александровна", "Алексеевна", "Анатольевна", "Андреевна", "Антоновна",
            "Аркадьевна", "Арсеньевна", "Артемовна", "Борисовна", "Вадимовна",
            "Валентиновна", "Валерьевна", "Васильевна", "Викторовна", "Витальевна",
            "Владимировна", "Владиславовна", "Вячеславовна", "Геннадьевна", "Георгиевна",
            "Григорьевна", "Данииловна", "Денисовна", "Дмитриевна", "Евгеньевна",
            "Егоровна", "Ивановна", "Игоревна", "Ильинична", "Кирилловна"
        ]
    }
    
    # Реальные российские города с районами
    RUSSIAN_CITIES = {
        "Москва": {
            "districts": ["Центральный", "Северный", "Южный", "Западный", "Восточный"],
            "streets": [
                "Тверская", "Арбат", "Новый Арбат", "Кутузовский проспект", "Ленинградский проспект",
                "Москва-Сити", "Китай-город", "Пресня", "Таганская", "Лефортово"
            ],
            "coords": [55.7558, 37.6173]
        },
        "Санкт-Петербург": {
            "districts": ["Центральный", "Адмиралтейский", "Василеостровский", "Петроградский", "Выборгский"],
            "streets": [
                "Невский проспект", "Литейный проспект", "Васильевский остров", "Петроградская сторона",
                "Московский проспект", "Лиговский проспект", "Большой проспект П.С."
            ],
            "coords": [59.9343, 30.3351]
        },
        "Новосибирск": {
            "districts": ["Центральный", "Железнодорожный", "Заельцовский", "Калининский", "Ленинский"],
            "streets": ["Красный проспект", "Ленина", "Гоголя", "Дзержинского", "Фрунзе"],
            "coords": [55.0084, 82.9357]
        },
        "Екатеринбург": {
            "districts": ["Верх-Исетский", "Железнодорожный", "Кировский", "Ленинский", "Октябрьский"],
            "streets": ["Ленина", "Малышева", "8 Марта", "Куйбышева", "Щорса"],
            "coords": [56.8389, 60.6057]
        },
        "Казань": {
            "districts": ["Вахитовский", "Московский", "Ново-Савиновский", "Кировский", "Советский"],
            "streets": ["Кремлевская", "Баумана", "Петербургская", "Декабристов", "Чистопольская"],
            "coords": [55.7961, 49.1064]
        }
    }
    
    # Возрастные группы для реалистичной генерации опыта
    AGE_GROUPS = {
        "young": (18, 25),      # Студенты, начинающие специалисты
        "middle": (26, 40),     # Опытные специалисты
        "senior": (41, 65)      # Руководители, эксперты
    }
    
    # Профессии с минимальным возрастом и опытом
    PROFESSIONS = {
        "Инженер-программист": {"min_age": 22, "max_experience": 40, "typical_experience": (2, 15)},
        "Менеджер по продажам": {"min_age": 20, "max_experience": 30, "typical_experience": (1, 10)},
        "Бухгалтер": {"min_age": 22, "max_experience": 45, "typical_experience": (3, 25)},
        "Врач": {"min_age": 25, "max_experience": 45, "typical_experience": (5, 35)},
        "Учитель": {"min_age": 23, "max_experience": 42, "typical_experience": (2, 30)},
        "Юрист": {"min_age": 24, "max_experience": 40, "typical_experience": (3, 25)},
        "Дизайнер": {"min_age": 20, "max_experience": 35, "typical_experience": (1, 15)},
        "Маркетолог": {"min_age": 22, "max_experience": 30, "typical_experience": (2, 15)},
        "Аналитик": {"min_age": 23, "max_experience": 35, "typical_experience": (2, 15)},
        "Системный администратор": {"min_age": 21, "max_experience": 40, "typical_experience": (2, 20)}
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "realistic_mode",
                True,
                "Реалистичная генерация данных",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "min_age",
                18,
                "Минимальный возраст",
                validator=loader.validators.Integer(minimum=18, maximum=30)
            ),
            loader.ConfigValue(
                "max_age",
                65,
                "Максимальный возраст",
                validator=loader.validators.Integer(minimum=40, maximum=100)
            ),
        )
        self._cache = {}
    
    async def client_ready(self, client, db):
        self._client = client
        self._db = db
    
    @loader.command(
        ru_doc="Сгенерировать реалистичные фейковые данные",
        en_doc="Generate realistic fake data"
    )
    async def pasta(self, message):
        """Реалистичная генерация личности"""
        try:
            data = self._generate_realistic_profile()
            await utils.answer(
                message,
                self.strings["generated"].format(data=data)
            )
        except Exception as e:
            await utils.answer(
                message,
                f"{self.strings['error']}: {str(e)}"
            )
    
    def _generate_realistic_profile(self) -> str:
        """Генерация реалистичного профиля"""
        # 1. Определяем возрастную группу
        age_group_key = random.choice(list(self.AGE_GROUPS.keys()))
        min_age, max_age = self.AGE_GROUPS[age_group_key]
        age = random.randint(min_age, max_age)
        
        # 2. Генерация даты рождения на основе возраста
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_day:02d}.{birth_month:02d}.{birth_year}"
        
        # 3. Выбор пола
        gender = random.choice(["male", "female"])
        
        # 4. Генерация ФИО
        first_name, last_name, patronymic = self._generate_fio(gender)
        
        # 5. Выбор города и адреса
        city_data = self._generate_real_address()
        city = city_data["city"]
        district = city_data["district"]
        street = city_data["street"]
        house = city_data["house"]
        apartment = city_data["apartment"]
        coords = city_data["coords"]
        
        # 6. Выбор профессии в соответствии с возрастом
        profession, experience = self._generate_profession_and_experience(age)
        
        # 7. Генерация контактов
        phone = self._generate_phone()
        email = self._generate_email(first_name, last_name)
        
        # 8. Telegram username на английском
        telegram = self._generate_telegram_username(first_name, last_name)
        
        # 9. Документы
        passport = self._generate_passport(birth_date)
        snils = self._generate_snils()
        inn = self._generate_inn()
        
        # 10. Банковские данные
        card = self._generate_card()
        
        # 11. Образование в соответствии с возрастом
        education = self._generate_education(age)
        
        # 12. Семейное положение в соответствии с возрастом
        marital = self._generate_marital_status(age)
        
        # 13. IP и соцсети
        ip = self._generate_ip(city)
        social = self._generate_social(first_name, last_name, telegram)
        
        # 14. Форматируем результат
        return self._format_profile(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            gender=gender,
            birth_date=birth_date,
            age=age,
            city=city,
            district=district,
            street=street,
            house=house,
            apartment=apartment,
            coords=coords,
            profession=profession,
            experience=experience,
            phone=phone,
            email=email,
            telegram=telegram,
            passport=passport,
            snils=snils,
            inn=inn,
            card=card,
            education=education,
            marital=marital,
            ip=ip,
            social=social
        )
    
    def _generate_fio(self, gender: str) -> Tuple[str, str, str]:
        """Генерация ФИО с правильными окончаниями"""
        first_name = random.choice(self.RUSSIAN_NAMES[gender])
        last_name = random.choice(self.RUSSIAN_SURNAMES[gender])
        patronymic = random.choice(self.RUSSIAN_PATRONYMICS[gender])
        
        return first_name, last_name, patronymic
    
    def _generate_real_address(self) -> Dict:
        """Генерация реального адреса с координатами"""
        city = random.choice(list(self.RUSSIAN_CITIES.keys()))
        city_info = self.RUSSIAN_CITIES[city]
        
        district = random.choice(city_info["districts"])
        street = random.choice(city_info["streets"])
        house = random.randint(1, 150)
        apartment = random.randint(1, 250)
        
        # Реалистичные координаты с небольшим смещением
        lat, lon = city_info["coords"]
        lat += random.uniform(-0.02, 0.02)  # ~2.2 км
        lon += random.uniform(-0.02, 0.02)  # ~1.2 км на широте Москвы
        
        # Тип здания в зависимости от района
        building_types = {
            "Центральный": "историческое здание",
            "Северный": "панельный дом",
            "Южный": "кирпичный дом", 
            "Западный": "новостройка",
            "Восточный": "панельный дом"
        }
        
        building_type = building_types.get(district, random.choice(["кирпичный дом", "панельный дом"]))
        
        return {
            "city": city,
            "district": district,
            "street": street,
            "house": house,
            "apartment": apartment,
            "coords": (lat, lon),
            "building_type": building_type,
            "floor": random.randint(1, 25 if city == "Москва" else 16),
            "entrance": random.randint(1, 10)
        }
    
    def _generate_profession_and_experience(self, age: int) -> Tuple[str, int]:
        """Генерация профессии и опыта работы с логической согласованностью"""
        # Фильтруем профессии по минимальному возрасту
        available_professions = {
            prof: data for prof, data in self.PROFESSIONS.items() 
            if age >= data["min_age"]
        }
        
        if not available_professions:
            # Если возраст слишком маленький для всех профессий
            profession = "Студент"
            experience = 0
        else:
            profession = random.choice(list(available_professions.keys()))
            prof_data = available_professions[profession]
            
            # Максимально возможный опыт работы
            max_possible_experience = age - prof_data["min_age"]
            if max_possible_experience < 0:
                max_possible_experience = 0
            
            # Типичный опыт для профессии, но не больше максимально возможного
            min_exp, max_exp = prof_data["typical_experience"]
            experience = random.randint(
                min(min_exp, max_possible_experience),
                min(max_exp, max_possible_experience)
            )
        
        return profession, experience
    
    def _generate_phone(self) -> str:
        """Генерация номера телефона"""
        operators = {
            "Москва": ["915", "916", "925", "926", "999"],
            "Санкт-Петербург": ["911", "921", "981"],
            "Новосибирск": ["913", "923", "983"],
            "Екатеринбург": ["922", "982"],
            "Казань": ["917", "987"]
        }
        
        # Используем случайный город для определения оператора
        city = random.choice(list(operators.keys()))
        operator = random.choice(operators[city])
        
        number = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
        return f"+7 ({operator}) {number}"
    
    def _generate_email(self, first_name: str, last_name: str) -> str:
        """Генерация email"""
        domains = ["yandex.ru", "mail.ru", "gmail.com", "rambler.ru"]
        username_variants = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{last_name.lower()}.{first_name.lower()}",
            f"{first_name.lower()}_{last_name.lower()}",
            f"{last_name.lower()}{first_name[0].lower()}"
        ]
        
        username = random.choice(username_variants)
        if random.random() < 0.3:  # 30% chance to add numbers
            username += str(random.randint(1, 99))
        
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def _generate_telegram_username(self, first_name: str, last_name: str) -> str:
        """Генерация Telegram username на английском"""
        # Транслитерация русских имен
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        def translit(text: str) -> str:
            result = []
            for char in text.lower():
                if char in translit_map:
                    result.append(translit_map[char])
                elif char.isalpha():
                    result.append(char)
            return ''.join(result)
        
        first_en = translit(first_name)
        last_en = translit(last_name)
        
        username_patterns = [
            f"{first_en}_{last_en}",
            f"{last_en}_{first_en}",
            f"{first_en}{last_en[:3]}",
            f"{last_en}{first_en[:1]}",
            f"{first_en}{random.randint(1, 99)}",
            f"{last_en}{random.randint(1, 99)}"
        ]
        
        username = random.choice(username_patterns)
        # Telegram usernames обычно без точек
        username = username.replace('.', '')
        return f"@{username}"
    
    def _generate_passport(self, birth_date: str) -> Dict[str, str]:
        """Генерация паспортных данных"""
        birth_year = int(birth_date.split('.')[2])
        
        # Серия зависит от региона и года выдачи
        if birth_year < 2000:
            series = f"{random.randint(10, 99)} {random.randint(10, 99)}"
        else:
            series = f"{random.randint(60, 99)} {random.randint(10, 99)}"
        
        number = f"{random.randint(100000, 999999)}"
        
        # Дата выдачи - не раньше 14 лет
        issue_year = random.randint(birth_year + 14, datetime.now().year)
        issue_month = random.randint(1, 12)
        issue_day = random.randint(1, 28)
        
        return {
            'series': series,
            'number': number,
            'issued': random.choice([
                "ОУФМС России по г. Москве",
                "ГУ МВД России по г. Санкт-Петербургу",
                "УМВД России по г. Новосибирску",
                "УФМС России по Московской области"
            ]),
            'issue_date': f"{issue_day:02d}.{issue_month:02d}.{issue_year}",
            'division_code': f"{random.randint(100, 999)}-{random.randint(100, 999)}"
        }
    
    def _generate_snils(self) -> str:
        """Генерация СНИЛС"""
        number = ''.join(str(random.randint(0, 9)) for _ in range(9))
        
        # Простое вычисление контрольного числа
        total = sum(int(digit) * (9 - i) for i, digit in enumerate(number[:9]))
        checksum = total % 101
        if checksum == 100:
            checksum = 0
        
        return f"{number[:3]}-{number[3:6]}-{number[6:9]} {checksum:02d}"
    
    def _generate_inn(self) -> str:
        """Генерация ИНН с контрольными цифрами"""
        # Регион (01-92)
        region = str(random.randint(1, 92)).zfill(2)
        
        # Налоговая инспекция (01-99)
        tax_office = str(random.randint(1, 99)).zfill(2)
        
        # Номер записи (000001-999999)
        record = str(random.randint(1, 999999)).zfill(6)
        
        inn_10 = region + tax_office + record
        
        # Контрольная цифра 1
        coefficients_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        sum_1 = sum(int(inn_10[i]) * coefficients_1[i] for i in range(10))
        control_1 = sum_1 % 11 % 10
        
        inn_11 = inn_10 + str(control_1)
        
        # Контрольная цифра 2
        coefficients_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        sum_2 = sum(int(inn_11[i]) * coefficients_2[i] for i in range(11))
        control_2 = sum_2 % 11 % 10
        
        return inn_11 + str(control_2)
    
    def _generate_card(self) -> Dict[str, str]:
        """Генерация банковской карты"""
        banks = [
            {"name": "Сбербанк", "prefix": "4276", "color": "Золотая"},
            {"name": "ВТБ", "prefix": "4471", "color": "Платиновая"},
            {"name": "Тинькофф", "prefix": "5536", "color": "Черная"},
            {"name": "Альфа-Банк", "prefix": "4584", "color": "Золотая"},
            {"name": "Газпромбанк", "prefix": "5484", "color": "Классическая"}
        ]
        
        bank = random.choice(banks)
        card_number = bank['prefix'] + ''.join(str(random.randint(0, 9)) for _ in range(12))
        card_number = self._luhn_checksum(card_number)
        
        # Срок действия - от 1 до 5 лет вперед
        month = random.randint(1, 12)
        year = datetime.now().year + random.randint(1, 5)
        
        return {
            'number': ' '.join([card_number[i:i+4] for i in range(0, 16, 4)]),
            'expiry': f"{month:02d}/{year}",
            'cvv': str(random.randint(100, 999)),
            'bank': bank['name'],
            'type': bank['color'],
            'account': "40817" + "810" + ''.join(str(random.randint(0, 9)) for _ in range(12))
        }
    
    def _luhn_checksum(self, card_number: str) -> str:
        """Алгоритм Луна для валидного номера карты"""
        digits = [int(d) for d in card_number]
        
        # Удваиваем каждую вторую цифру с конца
        for i in range(len(digits)-2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        # Суммируем все цифры кроме последней
        total = sum(digits[:-1])
        
        # Вычисляем контрольную цифру
        check_digit = (10 - (total % 10)) % 10
        
        return card_number[:-1] + str(check_digit)
    
    def _generate_education(self, age: int) -> Dict[str, str]:
        """Генерация образования в зависимости от возраста"""
        if age <= 22:
            # Молодые - студенты или недавние выпускники
            levels = ["Неполное высшее", "Бакалавр", "Среднее специальное"]
            universities = [
                "МГУ им. Ломоносова (студент)",
                "СПбГУ (студент)", 
                "НИУ ВШЭ (студент)",
                "МФТИ (студент)"
            ]
        elif age <= 30:
            # Средний возраст - специалисты
            levels = ["Высшее", "Бакалавр", "Специалист"]
            universities = [
                "МГУ им. Ломоносова",
                "СПбГУ",
                "НИУ ВШЭ", 
                "МФТИ",
                "МГТУ им. Баумана"
            ]
        else:
            # Старший возраст - возможно дополнительное образование
            levels = ["Высшее", "Магистр", "Кандидат наук", "Два высших"]
            universities = [
                "МГУ им. Ломоносова",
                "СПбГУ",
                "РАНХиГС",
                "МГИМО",
                "Финансовый университет"
            ]
        
        specialties = [
            "Информационные технологии",
            "Экономика",
            "Юриспруденция", 
            "Медицина",
            "Педагогика",
            "Строительство",
            "Менеджмент"
        ]
        
        return {
            'level': random.choice(levels),
            'university': random.choice(universities),
            'specialty': random.choice(specialties),
            'graduation_year': datetime.now().year - random.randint(0, age-18)
        }
    
    def _generate_marital_status(self, age: int) -> Dict[str, str]:
        """Генерация семейного положения в зависимости от возраста"""
        if age < 22:
            statuses = [
                {"status": "Холост/Не замужем", "details": "Не женат/Не замужем"},
                {"status": "Встречается", "details": "Есть партнер"}
            ]
        elif age < 30:
            statuses = [
                {"status": "Женат/Замужем", "details": "В браке, детей нет"},
                {"status": "Женат/Замужем", "details": "В браке, 1 ребенок"},
                {"status": "Гражданский брак", "details": "Совместное проживание"},
                {"status": "Разведен(а)", "details": "Брак расторгнут"}
            ]
        else:
            statuses = [
                {"status": "Женат/Замужем", "details": "В браке, 2 детей"},
                {"status": "Женат/Замужем", "details": "В браке, 3 детей"},
                {"status": "Разведен(а)", "details": "Двое детей от первого брака"},
                {"status": "Вдовец/Вдова", "details": "Есть взрослые дети"}
            ]
        
        return random.choice(statuses)
    
    def _generate_ip(self, city: str) -> str:
        """Генерация IP-адреса в зависимости от города"""
        ip_prefixes = {
            "Москва": ["77.", "78.", "79.", "95."],
            "Санкт-Петербург": ["81.", "82.", "93.", "94."],
            "Новосибирск": ["31.", "37.", "46."],
            "Екатеринбург": ["62.", "79.", "90."],
            "Казань": ["85.", "86.", "91."]
        }
        
        prefix = random.choice(ip_prefixes.get(city, ["77.", "78.", "79."]))
        return f"{prefix}{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    
    def _generate_social(self, first_name: str, last_name: str, telegram: str) -> Dict[str, str]:
        """Генерация аккаунтов в соцсетях"""
        username = telegram.replace('@', '')
        
        return {
            'vk': f"vk.com/id{random.randint(1000000, 999999999)}",
            'telegram': telegram,
            'instagram': f"@{username}",
            'username': username
        }
    
    def _format_profile(self, **kwargs) -> str:
        """Форматирование профиля"""
        maps_link = f"https://maps.google.com/?q={kwargs['coords'][0]},{kwargs['coords'][1]}"
        
        return f"""
👤 ЛИЧНЫЕ ДАННЫЕ:
ФИО: {kwargs['last_name']} {kwargs['first_name']} {kwargs['patronymic']}
Пол: {'Мужской' if kwargs['gender'] == 'male' else 'Женский'}
Дата рождения: {kwargs['birth_date']}
Возраст: {kwargs['age']} лет

📍 АДРЕС ПРОЖИВАНИЯ:
Город: {kwargs['city']}
Район: {kwargs['district']}
Адрес: ул. {kwargs['street']}, д. {kwargs['house']}, кв. {kwargs['apartment']}
Координаты: {kwargs['coords'][0]:.6f}, {kwargs['coords'][1]:.6f}
Карты: {maps_link}

💼 ПРОФЕССИЯ И ОПЫТ:
Профессия: {kwargs['profession']}
Опыт работы: {kwargs['experience']} лет
Возраст начала работы: {kwargs['age'] - kwargs['experience']} лет

📞 КОНТАКТЫ:
Телефон: {kwargs['phone']}
Email: {kwargs['email']}
Telegram: {kwargs['telegram']} (английский username)

📄 ДОКУМЕНТЫ:
Паспорт: {kwargs['passport']['series']} {kwargs['passport']['number']}
Выдан: {kwargs['passport']['issued']}
Дата выдачи: {kwargs['passport']['issue_date']}
СНИЛС: {kwargs['snils']}
ИНН: {kwargs['inn']}

💳 БАНКОВСКИЕ ДАННЫЕ:
Карта: {kwargs['card']['number']}
Срок: {kwargs['card']['expiry']}
CVV: {kwargs['card']['cvv']}
Банк: {kwargs['card']['bank']} ({kwargs['card']['type']})

🎓 ОБРАЗОВАНИЕ:
Уровень: {kwargs['education']['level']}
ВУЗ: {kwargs['education']['university']}
Специальность: {kwargs['education']['specialty']}
Год окончания: {kwargs['education']['graduation_year']}

👨‍👩‍👧‍👦 ЛИЧНАЯ ЖИЗНЬ:
Семейное положение: {kwargs['marital']['status']}
Дополнительно: {kwargs['marital']['details']}

🌐 ЦИФРОВОЙ СЛЕД:
IP адрес: {kwargs['ip']}
ВКонтакте: {kwargs['social']['vk']}
Telegram: {kwargs['social']['telegram']}
Instagram: {kwargs['social']['instagram']}

🔐 ЛОГИНЫ И ПАРОЛИ:
Логин: {kwargs['social']['username']}
Пароль: {self._generate_password()}
User-Agent: {self._generate_user_agent()}

📅 СГЕНЕРИРОВАНО: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🇷🇺 Страна: Россия
⚡ Реалистичная генерация: Да
"""
    
    def _generate_password(self) -> str:
        """Генерация сложного пароля"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(12))
    
    def _generate_user_agent(self) -> str:
        """Генерация User-Agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15"
        ]
        return random.choice(agents)
    
    # ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ
    
    @loader.command(
        ru_doc="Быстрая генерация карты",
        en_doc="Quick card generation"
    )
    async def pastacard(self, message):
        """Быстрая генерация карты"""
        try:
            card = self._generate_card()
            
            result = f"""
💳 БАНКОВСКАЯ КАРТА:

Номер: {card['number']}
Срок: {card['expiry']}
CVV: {card['cvv']}
Банк: {card['bank']} ({card['type']})
Счет: {card['account']}

📅 Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
            await utils.answer(message, result)
            
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}: {str(e)}")
    
    @loader.command(
        ru_doc="Сгенерировать только Telegram username",
        en_doc="Generate only Telegram username"
    )
    async def pastatg(self, message):
        """Генерация Telegram username"""
        try:
            gender = random.choice(["male", "female"])
            first_name = random.choice(self.RUSSIAN_NAMES[gender])
            last_name = random.choice(self.RUSSIAN_SURNAMES[gender])
            
            telegram = self._generate_telegram_username(first_name, last_name)
            
            result = f"""
📱 TELEGRAM USERNAME:

Имя: {first_name} {last_name}
Telegram: {telegram}
Английская транслитерация: Да

Примеры использования:
• Добавить в контакты: {telegram}
• Поиск в Telegram: {telegram}
• Ссылка: https://t.me/{telegram.replace('@', '')}

📅 Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
            await utils.answer(message, result)
            
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}: {str(e)}")
    
    @loader.command(
        ru_doc="Помощь по модулю",
        en_doc="Module help"
    )
    async def pastahelp(self, message):
        """Помощь по модулю"""
        help_text = """
🎭 FUNPASTA 2.1 - Реалистичный генератор данных

📋 Основные команды:

🎯 .pasta - Полная реалистичная личность
   • Согласованный возраст и опыт работы
   • Реальные адреса с координатами
   • Telegram username на английском

💳 .pastacard - Быстрая генерация карты
   • Валидные номера (алгоритм Луна)
   • Реальные банки России

📱 .pastatg - Только Telegram username
   • Английская транслитерация
   • Готовые ссылки для добавления

❓ .pastahelp - Эта справка

⚡ ОСОБЕННОСТИ 2.1:
• Логическая согласованность данных
• Возраст → Опыт работы → Образование
• Реальные российские адреса
• Английские Telegram usernames
• Валидные ИНН и СНИЛС
• Региональные IP-адреса

⚠️ Предупреждение:
Данные сгенерированы алгоритмически
и не относятся к реальным людям.

👨‍💻 Разработчик: @zymoyhold
Версия: 2.1.0
"""
        
        await utils.answer(message, help_text)
    
    @loader.command(
        ru_doc="Очистить кэш",
        en_doc="Clear cache"
    )
    async def pastaclear(self, message):
        """Очистка кэша"""
        self._cache.clear()
        await utils.answer(message, self.strings["clear"])