"""
    🛠️ FUN-HELPER v4.0 - Рабочий без лишних зависимостей
"""

__version__ = (4, 0, 0)

import aiohttp, asyncio, zipfile, io, base64, hashlib, json, os, re, urllib.parse, tempfile, mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .. import loader, utils

@loader.tds
class FunHelperMod(loader.Module):
    """FUN-HELPER v4.0 - Полностью рабочий модуль"""
    strings = {"name": "FunHelper"}

    def __init__(self):
        self.replies = {}
        self.stats = {
            "downloads": 0, "searches": 0, "encrypts": 0, "replies": 0,
            "exports": 0, "hashes": 0, "api_calls": 0, "time_checks": 0,
            "module_views": 0
        }
        self.config = loader.ModuleConfig(
            loader.ConfigValue("auto_reply", True, lambda: "Автоответчик"),
            loader.ConfigValue("g_key", "", lambda: "Google API ключ"),
            loader.ConfigValue("g_cse", "", lambda: "Google CSE ID"),
        )

    async def client_ready(self, client, db):
        self._client, self._db = client, db
        self.me = await client.get_me()
        self.replies = self._db.get(__name__, "replies", {})
        if stats := self._db.get(__name__, "stats"):
            self.stats.update(stats)

    def _save(self):
        self._db.set(__name__, "replies", self.replies)
        self._db.set(__name__, "stats", self.stats)

    # ==================== РАБОЧИЙ .funp БЕЗ ЗАВИСИМОСТЕЙ ====================
    @loader.command()
    async def funp(self, message):
        """Скачать весь сайт с ресурсами"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, 
                "🌐 <b>Скачать сайт полностью:</b>\n"
                "<code>.funp https://example.com</code>\n\n"
                "📦 <i>Скачивает HTML, CSS, JS, изображения</i>"
            )
            return
        
        url = args.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            msg = await message.edit(f"🔄 <b>Скачиваю сайт:</b>\n<code>{url[:50]}...</code>")
            
            # Скачиваем сайт
            zip_data, filename, file_count = await self._download_site_simple(url)
            
            if not zip_data:
                await msg.edit("❌ <b>Не удалось скачать сайт</b>\nПроверьте URL и доступность")
                return
            
            # Отправляем файл
            await self._client.send_file(
                message.peer_id,
                zip_data,
                caption=(
                    f"✅ <b>Сайт скачан!</b>\n\n"
                    f"📦 <b>Архив:</b> <code>{filename}</code>\n"
                    f"📊 <b>Файлов:</b> {file_count}\n"
                    f"📏 <b>Размер:</b> {len(zip_data) // 1024} KB\n"
                    f"🌐 <b>URL:</b> <code>{url}</code>\n\n"
                    f"👨‍💻 <i>Создано FunHelper v4.0</i>"
                ),
                file_name=filename,
                force_document=True
            )
            
            await msg.delete()
            self.stats["downloads"] += 1
            self._save()
            
        except Exception as e:
            await message.edit(f"❌ <b>Ошибка:</b>\n<code>{str(e)[:150]}</code>")

    async def _download_site_simple(self, url: str) -> Tuple[bytes, str, int]:
        """Упрощенное скачивание сайта без зависимостей"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                # Скачиваем основную страницу
                async with session.get(url) as response:
                    if response.status != 200:
                        return None, "", 0
                    
                    html_bytes = await response.read()
                    
                    # Пробуем разные кодировки
                    encodings = ['utf-8', 'cp1251', 'iso-8859-1', 'windows-1251']
                    html_text = None
                    
                    for enc in encodings:
                        try:
                            html_text = html_bytes.decode(enc)
                            break
                        except:
                            continue
                    
                    if html_text is None:
                        html_text = html_bytes.decode('utf-8', errors='ignore')
                
                # Создаем ZIP архив
                zip_buffer = io.BytesIO()
                file_count = 0
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Сохраняем основную страницу
                    zip_file.writestr("index.html", html_text)
                    file_count += 1
                    
                    # Парсим HTML простым regex для нахождения ресурсов
                    resources = set()
                    
                    # Ищем CSS
                    css_pattern = r'href=["\']([^"\']+\.css[^"\']*)["\']'
                    for match in re.finditer(css_pattern, html_text, re.IGNORECASE):
                        css_url = urllib.parse.urljoin(url, match.group(1))
                        resources.add(css_url)
                    
                    # Ищем JS
                    js_pattern = r'src=["\']([^"\']+\.js[^"\']*)["\']'
                    for match in re.finditer(js_pattern, html_text, re.IGNORECASE):
                        js_url = urllib.parse.urljoin(url, match.group(1))
                        resources.add(js_url)
                    
                    # Ищем изображения
                    img_pattern = r'src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg)[^"\']*)["\']'
                    for match in re.finditer(img_pattern, html_text, re.IGNORECASE):
                        img_url = urllib.parse.urljoin(url, match.group(1))
                        resources.add(img_url)
                    
                    # Скачиваем ресурсы (ограничиваем 15 файлами)
                    for i, resource_url in enumerate(list(resources)[:15]):
                        try:
                            async with session.get(resource_url, timeout=10) as res:
                                if res.status == 200:
                                    content = await res.read()
                                    
                                    # Получаем имя файла из URL
                                    parsed = urllib.parse.urlparse(resource_url)
                                    path = parsed.path
                                    filename = Path(path).name
                                    
                                    if not filename:
                                        # Если нет имени, создаем по типу контента
                                        content_type = res.headers.get('Content-Type', '')
                                        if 'css' in content_type:
                                            filename = f"style_{i}.css"
                                        elif 'javascript' in content_type:
                                            filename = f"script_{i}.js"
                                        elif 'image' in content_type:
                                            ext = '.jpg' if 'jpeg' in content_type else '.png'
                                            filename = f"image_{i}{ext}"
                                        else:
                                            filename = f"file_{i}.bin"
                                    
                                    # Создаем путь в архиве
                                    archive_path = f"assets/{filename}"
                                    zip_file.writestr(archive_path, content)
                                    file_count += 1
                                    
                        except Exception as e:
                            continue  # Пропускаем если не удалось скачать
                    
                    # Добавляем README файл
                    readme = f"""📦 СКАЧАННЫЙ САЙТ
━━━━━━━━━━━━━━━━
URL: {url}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Файлов: {file_count}
Размер HTML: {len(html_bytes)} байт

📁 Содержимое:
• index.html - главная страница
• assets/ - ресурсы сайта

🛠️ Создано: FunHelper v4.0
👨‍💻 Разработчик: @zymoyhold
🤝 Спонсор: @funcrmp
━━━━━━━━━━━━━━━━"""
                    
                    zip_file.writestr("README.txt", readme)
                    file_count += 1
                
                zip_buffer.seek(0)
                
                # Создаем имя файла
                domain = urllib.parse.urlparse(url).netloc
                domain = domain.replace('www.', '').replace('.', '_')[:20]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"site_{domain}_{timestamp}.zip"
                
                return zip_buffer.read(), filename, file_count
                
        except Exception as e:
            print(f"[FunHelper] Download error: {e}")
            return None, "", 0

    # ==================== ОСТАЛЬНЫЕ КОМАНДЫ ====================
    @loader.command()
    async def funpr(self, message):
        """Все проекты FunModules"""
        self.stats["module_views"] += 1
        self._save()
        
        text = """🎁 <b>ВСЕ ПРОЕКТЫ FUNMODULES</b>

🛠️  <b>FunHelper</b> (v4.0)
• Полностью рабочий модуль без лишних зависимостей
• Скачивание сайтов с ресурсами (.funp)
• Шифрование, хеширование, поиск
• Автоответчик и экспорт данных
• Отсчет до НГ и просмотр модулей

🏠  <b>FunAddress</b> (v0.1)
• Генератор случайных адресов
• Реальные координаты и IP
• Поддержка разных стран

🎭  <b>FunPasta</b> (v0.1)
• Генератор фейковых личностей
• Банковские карты с алгоритмом Луна
• Телефоны, адреса, email

🎮  <b>FunGame</b>
• Игровая система с балансом
• Мини-игры: кости и монетка
• Ежедневные бонусы и топ игроков

━━━━━━━━━━━━━━━━━━
👨‍💻 <b>Разработчик:</b> @zymoyhold
🤝 <b>Спонсор:</b> @funcrmp
🌐 <b>Сайт проектов:</b> https://funmodules.fwh.is"""
        
        await utils.answer(message, text)

    @loader.command()
    async def funnew(self, message):
        """Новогоднее поздравление"""
        text = """🎆 <b>С НОВЫМ ГОДОМ!</b>

✨ Пусть новый {year} год принесет:
🛠️  Мощные и удобные модули
🚀  Прорывные идеи для разработки
💻  Стабильный код без ошибок
📦  Успешные проекты и рост

🎁 <b>Посетите сайт FunModules:</b>
https://funmodules.fwh.is

━━━━━━━━━━━━━━━━━━
👨‍💻 С наилучшими пожеланиями,
Команда FunModules & @zymoyhold""".format(year=datetime.now().year + 1)
        
        await utils.answer(message, text)

    @loader.command()
    async def funtime(self, message):
        """Время до Нового Года"""
        try:
            now = datetime.now()
            target_year = now.year + 1
            target = datetime(target_year, 1, 1, 0, 0, 0)
            diff = target - now
            
            days = diff.days
            seconds = diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            # Выбираем эмодзи и статус
            if days > 60:
                emoji, status = "📅", "Еще много времени"
            elif days > 30:
                emoji, status = "🗓️", "Готовимся к празднику"
            elif days > 14:
                emoji, status = "⏳", "Скоро Новый Год"
            elif days > 7:
                emoji, status = "🎁", "Неделя до праздника"
            elif days > 3:
                emoji, status = "🎄", "Скоро-скоро!"
            elif days > 1:
                emoji, status = "🌟", "Уже завтра-послезавтра!"
            elif days == 1:
                emoji, status = "🎇", "ЗАВТРА НОВЫЙ ГОД!"
            elif hours > 12:
                emoji, status = "⏰", "Часы тикают..."
            elif hours > 6:
                emoji, status = "🕐", "Считаем часы!"
            elif hours > 1:
                emoji, status = "🕑", "Совсем скоро!"
            elif hours == 1:
                emoji, status = "🕒", "ЧАС ДО НОВОГО ГОДА!"
            elif minutes > 30:
                emoji, status = "⏱️", "Минуты летят..."
            elif minutes > 10:
                emoji, status = "🎆", "Приготовьте фейерверки!"
            elif minutes > 1:
                emoji, status = "✨", "ПОЧТИ НАСТУПИЛО!"
            else:
                emoji, status = "🎉", "СЕКУНДЫ ДО ПОЛУНОЧИ!"
            
            text = f"""{emoji} <b>ДО НОВОГО {target_year} ГОДА</b>
━━━━━━━━━━━━━━━━━━
📅 <b>Дней:</b> {days:02d}
🕐 <b>Часов:</b> {hours:02d}
⏰ <b>Минут:</b> {minutes:02d}
⏱️ <b>Секунд:</b> {secs:02d}
━━━━━━━━━━━━━━━━━━
📊 <b>Всего секунд:</b> {int(diff.total_seconds()):,}
📈 <b>Прогресс года:</b> {((365 - days) / 365 * 100):.1f}%

🎯 <b>Целевое время:</b> 
   {target.strftime('%d.%m.%Y %H:%M:%S')}
📆 <b>Текущее время:</b> 
   {now.strftime('%d.%m.%Y %H:%M:%S')}

✨ <b>Статус:</b> {status}"""
            
            self.stats["time_checks"] += 1
            self._save()
            await utils.answer(message, text)
            
        except Exception as e:
            await utils.answer(message, f"🎄 <b>Ошибка расчета:</b>\n<code>{str(e)[:100]}</code>")

    @loader.command()
    async def funr(self, message):
        """Автоответчик"""
        args = utils.get_args_raw(message)
        
        if not args:
            if not self.replies:
                await utils.answer(message, "📭 <b>Нет автоответов</b>\n\nИспользуйте: <code>.funr [триггер] [ответ]</code>")
                return
            
            text = "📋 <b>Автоответы:</b>\n\n"
            for i, (trigger, response) in enumerate(self.replies.items(), 1):
                text += f"{i}. <b>{trigger}</b> → {response[:30]}...\n"
            
            await utils.answer(message, text)
            return
        
        parts = args.split(" ", 1)
        
        if len(parts) == 1:
            # Удаление
            trigger = parts[0].lower()
            if trigger in self.replies:
                del self.replies[trigger]
                self._save()
                await utils.answer(message, f"✅ <b>Удален автоответ:</b> <code>{trigger}</code>")
            else:
                await utils.answer(message, f"❌ <b>Не найден:</b> <code>{trigger}</code>")
        else:
            # Добавление
            trigger, response = parts
            self.replies[trigger.lower()] = response
            self._save()
            await utils.answer(message, f"✅ <b>Добавлен автоответ:</b>\n<b>{trigger}</b> → {response[:50]}...")

    @loader.command()
    async def fune(self, message):
        """Шифрование текста"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, """🔐 <b>Методы шифрования:</b>

1. <code>.fune base64 [текст]</code> - Base64 кодирование
2. <code>.fune md5 [текст]</code> - MD5 хеш
3. <code>.fune sha256 [текст]</code> - SHA256 хеш
4. <code>.fune rot13 [текст]</code> - ROT13 шифрование
5. <code>.fune decode [base64]</code> - декодирование Base64

💡 <i>Пример:</i> <code>.fune base64 Hello World</code>""")
            return
        
        parts = args.split(" ", 1)
        if len(parts) < 2:
            await utils.answer(message, "❌ <b>Формат:</b> <code>.fune [метод] [текст]</code>")
            return
        
        method, text = parts
        method = method.lower()
        
        if method == "base64":
            result = base64.b64encode(text.encode()).decode()
        elif method == "md5":
            result = hashlib.md5(text.encode()).hexdigest()
        elif method == "sha256":
            result = hashlib.sha256(text.encode()).hexdigest()
        elif method == "rot13":
            result = self._rot13(text)
        elif method == "decode":
            try:
                result = base64.b64decode(text.encode()).decode()
                method = "base64 decode"
            except:
                result = "❌ Неверный Base64 формат"
        else:
            await utils.answer(message, "❌ <b>Неизвестный метод</b>\nДоступно: base64, md5, sha256, rot13, decode")
            return
        
        self.stats["encrypts"] += 1
        self._save()
        await utils.answer(message, f"🔐 <b>{method}:</b>\n<code>{result}</code>")

    def _rot13(self, text: str) -> str:
        """ROT13 шифрование"""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - 97 + 13) % 26 + 97))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - 65 + 13) % 26 + 65))
            else:
                result.append(char)
        return ''.join(result)

    @loader.command()
    async def funh(self, message):
        """Хеширование"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, """🔢 <b>Алгоритмы хеширования:</b>

• <code>.funh md5 [текст]</code> - MD5
• <code>.funh sha1 [текст]</code> - SHA1
• <code>.funh sha256 [текст]</code> - SHA256
• <code>.funh sha512 [текст]</code> - SHA512

💡 <i>Пример:</i> <code>.funh md5 password123</code>""")
            return
        
        parts = args.split(" ", 1)
        if len(parts) < 2:
            await utils.answer(message, "❌ <b>Формат:</b> <code>.funh [алгоритм] [текст]</code>")
            return
        
        algorithm, text = parts
        algorithm = algorithm.lower()
        
        hash_functions = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }
        
        if algorithm not in hash_functions:
            await utils.answer(message, f"❌ <b>Неизвестный алгоритм:</b> {algorithm}\nДоступно: {', '.join(hash_functions.keys())}")
            return
        
        result = hash_functions[algorithm](text.encode()).hexdigest()
        
        self.stats["hashes"] += 1
        self._save()
        await utils.answer(message, f"🔢 <b>{algorithm}:</b>\n<code>{result}</code>")

    @loader.command()
    async def funs(self, message):
        """Google поиск"""
        api_key = self.config["g_key"]
        cse_id = self.config["g_cse"]
        
        if not api_key or not cse_id:
            await utils.answer(message, 
                "❌ <b>Google API не настроен</b>\n\n"
                "Используйте команду:\n"
                "<code>.funapi [api_key] [cse_id]</code>\n\n"
                "💡 <i>Для помощи по получению API ключа используйте .funhelp</i>"
            )
            return
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "🔍 <b>Формат:</b> <code>.funs [запрос]</code>")
            return
        
        query = args.strip()
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "num": 5,
                "hl": "ru",
                "lr": "lang_ru",
                "safe": "off"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text[:100]}")
                    
                    data = await response.json()
            
            if "items" not in data:
                await utils.answer(message, "🔍 <b>Результаты не найдены</b>\n\nПопробуйте другой запрос")
                return
            
            text = f"🔍 <b>Результаты поиска Google:</b>\n\n"
            text += f"📝 <b>Запрос:</b> <code>{query}</code>\n\n"
            
            for i, item in enumerate(data["items"][:5], 1):
                title = item.get("title", "Без названия")[:70]
                link = item.get("link", "#")
                snippet = item.get("snippet", "Без описания")[:120]
                
                text += f"{i}. <b>{title}</b>\n"
                if snippet:
                    text += f"   <i>{snippet}...</i>\n"
                text += f"   🔗 <code>{link}</code>\n\n"
            
            self.stats["searches"] += 1
            self.stats["api_calls"] += 1
            self._save()
            
            await utils.answer(message, text)
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                await utils.answer(message, "⚠️ <b>Лимит API превышен</b>\n\nПроверьте квоту API ключа")
            elif "invalid" in error_msg.lower() or "key" in error_msg.lower():
                await utils.answer(message, "❌ <b>Неверный API ключ</b>\n\nПроверьте правильность ключа и CSE ID")
            else:
                await utils.answer(message, f"❌ <b>Ошибка поиска:</b>\n<code>{error_msg[:150]}</code>")

    @loader.command()
    async def funapi(self, message):
        """Управление API ключом"""
        args = utils.get_args_raw(message)
        
        if not args:
            status = "✅ Настроен" if self.config["g_key"] else "❌ Не настроен"
            await utils.answer(message, f"🔑 <b>Google API статус:</b> {status}")
            return
        
        if args.lower() == "remove":
            old_key = self.config["g_key"][:10] + "..." if self.config["g_key"] else "нет"
            old_cse = self.config["g_cse"][:10] + "..." if self.config["g_cse"] else "нет"
            
            self.config["g_key"] = ""
            self.config["g_cse"] = ""
            
            await utils.answer(message, f"✅ <b>API ключ удален</b>\n\n🔑 Ключ: <code>{old_key}</code>\n🆔 CSE ID: <code>{old_cse}</code>")
            return
        
        parts = args.split()
        
        if len(parts) < 2:
            await utils.answer(message, 
                "❌ <b>Формат:</b> <code>.funapi [api_key] [cse_id]</code>\n\n"
                "💡 <i>Пример:</i>\n"
                "<code>.funapi AIzaSyBxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxx</code>"
            )
            return
        
        api_key = parts[0]
        cse_id = parts[1]
        
        self.config["g_key"] = api_key
        self.config["g_cse"] = cse_id
        
        await utils.answer(message, 
            f"✅ <b>API ключ сохранен</b>\n\n"
            f"🔑 Ключ: <code>{api_key[:20]}...</code>\n"
            f"🆔 CSE ID: <code>{cse_id[:20]}...</code>\n\n"
            f"💡 Теперь можно использовать команду <code>.funs [запрос]</code>"
        )

    @loader.command()
    async def funee(self, message):
        """Экспорт данных"""
        try:
            export_data = {
                "module": "FunHelper v4.0",
                "export_date": datetime.now().isoformat(),
                "developer": "@zymoyhold",
                "sponsor": "@funcrmp",
                "data": {
                    "replies": self.replies,
                    "stats": self.stats,
                    "config": {
                        "auto_reply_enabled": self.config["auto_reply"],
                        "google_api_key_set": bool(self.config["g_key"]),
                        "google_cse_id_set": bool(self.config["g_cse"]),
                    },
                    "version": __version__
                }
            }
            
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                f.write(json_data)
                temp_path = f.name
            
            # Отправляем файл
            filename = f"funhelper_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            await self._client.send_file(
                message.peer_id,
                temp_path,
                caption=(
                    f"✅ <b>Данные экспортированы!</b>\n\n"
                    f"📦 Файл: <code>{filename}</code>\n"
                    f"📊 Записей: {len(self.replies)}\n"
                    f"💾 Размер: {len(json_data) // 1024} KB\n\n"
                    f"👨‍💻 <i>FunHelper v4.0</i>"
                ),
                file_name=filename
            )
            
            # Удаляем временный файл
            os.unlink(temp_path)
            
            self.stats["exports"] += 1
            self._save()
            
        except Exception as e:
            await utils.answer(message, f"❌ <b>Ошибка экспорта:</b>\n<code>{str(e)[:150]}</code>")

    @loader.command()
    async def funstats(self, message):
        """Статистика модуля"""
        text = f"""📊 <b>FunHelper v4.0 - Статистика</b>
━━━━━━━━━━━━━━━━━━
🌐 <b>Скачиваний сайтов:</b> {self.stats["downloads"]}
🔍 <b>Поисковых запросов:</b> {self.stats["searches"]}
🔐 <b>Операций шифрования:</b> {self.stats["encrypts"]}
🤖 <b>Срабатываний автоответа:</b> {self.stats["replies"]}
📤 <b>Экспортов данных:</b> {self.stats["exports"]}
🔢 <b>Хеширований:</b> {self.stats["hashes"]}
🔑 <b>API запросов:</b> {self.stats["api_calls"]}
⏰ <b>Проверок времени:</b> {self.stats["time_checks"]}
📦 <b>Просмотров модулей:</b> {self.stats["module_views"]}
━━━━━━━━━━━━━━━━━━
📝 <b>Автоответов в базе:</b> {len(self.replies)}
⚙️ <b>Автоответчик:</b> {'✅ ВКЛ' if self.config['auto_reply'] else '❌ ВЫКЛ'}
🔑 <b>Google API:</b> {'✅ Настроен' if self.config['g_key'] else '❌ Не настроен'}
━━━━━━━━━━━━━━━━━━
👨‍💻 <b>Разработчик:</b> @zymoyhold
🤝 <b>Спонсор:</b> @funcrmp"""
        
        await utils.answer(message, text)

    @loader.command()
    async def funautoreply(self, message):
        """Включить/выключить автоответчик"""
        current = self.config["auto_reply"]
        self.config["auto_reply"] = not current
        
        status = "🟢 ВКЛЮЧЕН" if self.config["auto_reply"] else "🔴 ВЫКЛЮЧЕН"
        await utils.answer(message, 
            f"⚙️ <b>Автоответчик</b> {status}\n\n"
            f"📊 Автоответов: {len(self.replies)}\n"
            f"💡 <code>.funr [триггер] [ответ]</code> - добавить новый"
        )

    @loader.command()
    async def funclear(self, message):
        """Очистить все автоответы"""
        count = len(self.replies)
        
        if count == 0:
            await utils.answer(message, "📭 <b>Нет автоответов для очистки</b>")
            return
        
        self.replies = {}
        self._save()
        
        await utils.answer(message, f"🧹 <b>Очищено {count} автоответов</b>")

    @loader.command()
    async def funtest(self, message):
        """Тест модуля"""
        tests = []
        
        # Проверка базовых функций
        try:
            base64.b64encode(b"test").decode()
            tests.append("✅ Base64 шифрование работает")
        except:
            tests.append("❌ Base64 шифрование не работает")
        
        try:
            hashlib.md5(b"test").hexdigest()
            tests.append("✅ MD5 хеширование работает")
        except:
            tests.append("❌ MD5 хеширование не работает")
        
        try:
            hashlib.sha256(b"test").hexdigest()
            tests.append("✅ SHA256 хеширование работает")
        except:
            tests.append("❌ SHA256 хеширование не работает")
        
        # Проверка API
        tests.append(f"✅ Google API: {'Настроен' if self.config['g_key'] else 'Не настроен'}")
        
        # Статистика
        tests.append(f"✅ Автоответов: {len(self.replies)}")
        tests.append(f"✅ Скачиваний: {self.stats['downloads']}")
        tests.append(f"✅ Поисков: {self.stats['searches']}")
        tests.append(f"✅ Экспортов: {self.stats['exports']}")
        tests.append(f"✅ Хеширований: {self.stats['hashes']}")
        
        result_text = "🧪 <b>Тест FunHelper v4.0:</b>\n\n" + "\n".join(tests)
        
        await utils.answer(message, result_text)

    @loader.command()
    async def funhelp(self, message):
        """Помощь по модулю"""
        text = """🛠️ <b>FunHelper v4.0 - Полная справка</b>

🔹 <b>Основные команды:</b>
• <code>.funr [триггер] [ответ]</code> - добавить автоответ
• <code>.funr [триггер]</code> - удалить автоответ
• <code>.funr</code> - список автоответов

• <code>.fune base64 [текст]</code> - Base64 кодирование
• <code>.fune md5 [текст]</code> - MD5 хеш
• <code>.fune sha256 [текст]</code> - SHA256 хеш
• <code>.fune rot13 [текст]</code> - ROT13 шифрование
• <code>.fune decode [base64]</code> - декодирование Base64

• <code>.funh md5 [текст]</code> - MD5 хеширование
• <code>.funh sha256 [текст]</code> - SHA256 хеширование
• <code>.funh sha512 [текст]</code> - SHA512 хеширование

• <code>.funs [запрос]</code> - поиск в Google
• <code>.funapi [ключ] [cse_id]</code> - установить API ключ
• <code>.funapi remove</code> - удалить API ключ

• <code>.funp [url]</code> - скачать весь сайт с ресурсами
• <code>.funee</code> - экспорт данных в JSON

🔹 <b>Новые команды:</b>
• <code>.funpr</code> - все проекты FunModules
• <code>.funnew</code> - новогоднее поздравление
• <code>.funtime</code> - время до Нового Года

🔹 <b>Управление:</b>
• <code>.funstats</code> - статистика модуля
• <code>.funautoreply</code> - вкл/выкл автоответчик
• <code>.funclear</code> - очистить все автоответы
• <code>.funtest</code> - тест модуля
• <code>.funhelp</code> - эта справка

━━━━━━━━━━━━━━━━━━
👨‍💻 <b>Разработчик:</b> @zymoyhold
🤝 <b>Спонсор:</b> @funcrmp
🌐 <b>Сайт проектов:</b> https://funmodules.fwh.is
━━━━━━━━━━━━━━━━━━
💡 <b>Зависимости:</b> <code>aiohttp</code> (уже встроен в большинство сборок)"""
        
        await utils.answer(message, text)

    async def watcher(self, message):
        """Обработчик автоответов"""
        if not self.config["auto_reply"]:
            return
        
        if not message.text or message.out:
            return
        
        if message.sender_id == self.me.id:
            return
        
        text = message.text.lower()
        
        for trigger, response in self.replies.items():
            if trigger in text:
                await asyncio.sleep(0.5)
                await message.reply(response)
                self.stats["replies"] += 1
                self._save()
                break