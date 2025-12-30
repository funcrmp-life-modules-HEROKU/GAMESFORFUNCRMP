"""
    🛠️ FUN-HELPER v3.5 - Многофункциональный помощник
    
    Автоответчик, скачиватель сайтов, шифровальщик,
    Google поиск через API, экспорт и хеши.
    
"""

__version__ = (3, 5, 0)

# meta developer: @zymoyhold
# requires: aiohttp beautifulsoup4

import aiohttp
import asyncio
import zipfile
import io
import base64
import hashlib
import json
import re
import urllib.parse
import tempfile
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from .. import loader, utils

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

@loader.tds
class FunHelperMod(loader.Module):
    """FUN-HELPER v3.5 - Многофункциональный помощник"""
    
    strings = {
        "name": "FunHelper",
        "reply_added": "✅ <b>Автоответ добавлен:</b>\n\n📝 <b>Триггер:</b> <code>{trigger}</code>\n💬 <b>Ответ:</b> <code>{response}</code>",
        "reply_removed": "✅ <b>Автоответ удален:</b> <code>{trigger}</code>",
        "reply_list": "📋 <b>Список автоответов:</b>\n\n{replies}",
        "reply_not_found": "❌ <b>Автоответ не найден:</b> <code>{trigger}</code>",
        "download_start": "🌐 <b>Скачивание сайта:</b>\n\n📝 URL: <code>{url}</code>\n⏳ Скачивание контента...",
        "download_success": "✅ <b>Сайт скачан и упакован!</b>\n\n📦 Архив: <code>{filename}</code>\n📊 Файлов: {file_count}\n💾 Размер: {size} MB\n🌐 Главный файл: <code>index.html</code>",
        "download_error": "❌ <b>Ошибка скачивания:</b>\n\n{error}",
        "download_no_bs4": "❌ <b>Установите BeautifulSoup4:</b>\n\n<code>pip install beautifulsoup4</code>",
        "encrypt_options": "🔐 <b>Методы шифрования:</b>\n\n1. <code>.fune base64 [текст]</code>\n2. <code>.fune md5 [текст]</code>\n3. <code>.fune sha256 [текст]</code>\n4. <code>.fune rot13 [текст]</code>\n5. <code>.fune xor [текст]</code>\n6. <code>.fune decode [base64]</code>",
        "encrypted": "🔐 <b>{method}:</b>\n\n<code>{result}</code>",
        "searching": "🔍 <b>Поиск в Google...</b>\n\n📝 <code>{query}</code>",
        "search_results": "🔍 <b>Результаты поиска Google:</b>\n\n{results}",
        "search_error": "❌ <b>Ошибка поиска:</b>\n\n{error}",
        "search_no_api": "❌ <b>API ключ не установлен</b>\n\nИспользуйте команду: <code>.funapi [ваш_api_ключ]</code>\nДля помощи по получению API ключа: <code>.funapihelp</code>",
        "search_limit": "⚠️ <b>Лимит API превышен или ключ недействителен</b>\n\nПроверьте свой API ключ или подождите",
        "api_saved": "✅ <b>API ключ Google сохранен</b>\n\n🔑 Ключ: <code>{api_key}</code>\n📊 Статус: Активен\n💡 Теперь можно использовать команду <code>.funs [запрос]</code>",
        "api_removed": "✅ <b>API ключ Google удален</b>",
        "api_test": "🧪 <b>Тестирование API ключа...</b>",
        "api_test_success": "✅ <b>API ключ рабочий!</b>\n\n🔑 Ключ: <code>{api_key}</code>\n📊 Статус: Проверено\n⚡ Можно использовать поиск",
        "api_test_fail": "❌ <b>API ключ не работает</b>\n\nПроверьте правильность ключа или получите новый",
        "stats": "📊 <b>Статистика FUN-HELPER:</b>\n\n{stats}",
        "export_start": "📤 <b>Экспорт данных...</b>",
        "export_success": "✅ <b>Данные экспортированы!</b>\n\n📦 Файл: <code>{filename}</code>\n📊 Записей: {records}\n💾 Размер: {size} KB",
        "export_error": "❌ <b>Ошибка экспорта:</b>\n\n{error}",
        "hash_options": "🔢 <b>Доступные алгоритмы хеширования:</b>\n\n{algorithms}\n\n💡 <code>.funh [алгоритм] [текст]</code>",
        "hashed": "🔢 <b>{algorithm}:</b>\n\n<code>{result}</code>",
        "hash_error": "❌ <b>Неизвестный алгоритм:</b> <code>{algorithm}</code>",
        "api_help": "📚 <b>Помощь по Google API ключу:</b>\n\n{help_text}",
    }
    
    def __init__(self):
        # Алгоритмы хеширования
        self.HASH_ALGORITHMS = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha224": hashlib.sha224,
            "sha256": hashlib.sha256,
            "sha384": hashlib.sha384,
            "sha512": hashlib.sha512,
            "sha3_224": hashlib.sha3_224,
            "sha3_256": hashlib.sha3_256,
            "sha3_384": hashlib.sha3_384,
            "sha3_512": hashlib.sha3_512,
            "blake2b": hashlib.blake2b,
            "blake2s": hashlib.blake2s,
        }
        
        self.replies: Dict[str, str] = {}
        self.stats: Dict[str, int] = {
            "downloads": 0,
            "searches": 0,
            "encryptions": 0,
            "replies_used": 0,
            "exports": 0,
            "hashes": 0,
            "api_used": 0
        }
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_reply_enabled",
                True,
                "Включить автоответчик",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "max_download_size",
                10,
                "Макс. размер скачивания (MB)",
                validator=loader.validators.Integer(minimum=1, maximum=50)
            ),
            loader.ConfigValue(
                "download_timeout",
                30,
                "Таймаут скачивания (секунд)",
                validator=loader.validators.Integer(minimum=10, maximum=120)
            ),
            loader.ConfigValue(
                "user_agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "User-Agent для запросов",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "google_api_key",
                "",
                "Google Custom Search API ключ",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "google_cse_id",
                "",
                "Google Custom Search Engine ID",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "search_results_count",
                5,
                "Количество результатов поиска",
                validator=loader.validators.Integer(minimum=1, maximum=10)
            ),
        )
    
    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.me = await client.get_me()
        
        # Загрузка автоответов из базы
        replies_data = self._db.get(__name__, "replies", {})
        self.replies = replies_data
        
        # Загрузка статистики
        stats_data = self._db.get(__name__, "stats", {})
        self.stats = {**self.stats, **stats_data}
    
    def _save_replies(self):
        """Сохранение автоответов в базу"""
        self._db.set(__name__, "replies", self.replies)
    
    def _save_stats(self):
        """Сохранение статистики"""
        self._db.set(__name__, "stats", self.stats)
    
    # ==================== FUNR - АВТООТВЕТЧИК ====================
    
    @loader.command(
        ru_doc="[триггер] [ответ] - Добавить автоответ",
        en_doc="[trigger] [response] - Add auto reply"
    )
    async def funr(self, message):
        """Добавить/удалить автоответ"""
        args = utils.get_args_raw(message)
        
        if not args:
            # Показать список автоответов
            if not self.replies:
                await utils.answer(message, "📭 <b>Автоответы не настроены</b>")
                return
            
            replies_text = ""
            for i, (trigger, response) in enumerate(self.replies.items(), 1):
                replies_text += f"{i}. <b>{trigger}</b> → {response[:30]}...\n"
            
            await utils.answer(
                message,
                self.strings["reply_list"].format(replies=replies_text)
            )
            return
        
        parts = args.split(" ", 1)
        
        if len(parts) == 1:
            # Удаление автоответа
            trigger = parts[0].lower()
            if trigger in self.replies:
                del self.replies[trigger]
                self._save_replies()
                await utils.answer(
                    message,
                    self.strings["reply_removed"].format(trigger=trigger)
                )
            else:
                await utils.answer(
                    message,
                    self.strings["reply_not_found"].format(trigger=trigger)
                )
            return
        
        # Добавление автоответа
        trigger, response = parts
        trigger = trigger.lower()
        
        self.replies[trigger] = response
        self._save_replies()
        
        await utils.answer(
            message,
            self.strings["reply_added"].format(
                trigger=utils.escape_html(trigger),
                response=utils.escape_html(response[:100])
            )
        )
    
    # ==================== FUNP - СКАЧИВАНИЕ САЙТОВ ====================
    
    @loader.command(
        ru_doc="[url] - Скачать реальный сайт в ZIP архив",
        en_doc="[url] - Download real website to ZIP archive"
    )
    async def funp(self, message):
        """Скачать реальный сайт в ZIP"""
        if not HAS_BS4:
            await utils.answer(message, self.strings["download_no_bs4"])
            return
        
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, 
                "🌐 <b>Скачивание реальных сайтов:</b>\n\n"
                "📦 <code>.funp [url]</code>\n\n"
                "💡 <i>Примеры:</i>\n"
                "<code>.funp https://example.com</code>\n"
                "<code>.funp google.com</code>\n"
                "<code>.funp https://habr.com</code>\n\n"
                "⚡ <i>Скачивает реальный HTML и ресурсы</i>"
            )
            return
        
        url = args.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        processing_msg = await utils.answer(
            message,
            self.strings["download_start"].format(url=utils.escape_html(url))
        )
        
        try:
            zip_data, file_count, total_size = await self._download_real_website(url)
            
            if not zip_data:
                await utils.answer(
                    processing_msg,
                    self.strings["download_error"].format(error="Не удалось скачать сайт")
                )
                return
            
            # Создаем имя файла
            domain = self._extract_domain(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}.zip"
            
            # Сохраняем временный файл
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                tmp_file.write(zip_data)
                tmp_file.flush()
                
                # Отправляем файл
                await self._client.send_file(
                    message.peer_id,
                    tmp_file.name,
                    caption=self.strings["download_success"].format(
                        filename=filename,
                        file_count=file_count,
                        size=round(len(zip_data) / 1024 / 1024, 2)
                    )
                )
                
                # Удаляем временный файл
                os.unlink(tmp_file.name)
            
            # Обновляем статистику
            self.stats["downloads"] += 1
            self._save_stats()
            
            await processing_msg.delete()
            
        except Exception as e:
            await utils.answer(
                processing_msg,
                self.strings["download_error"].format(error=str(e)[:200])
            )
    
    async def _download_real_website(self, url: str) -> Tuple[bytes, int, int]:
        """Скачивание реального сайта"""
        zip_buffer = io.BytesIO()
        file_count = 0
        total_size = 0
        
        headers = {
            "User-Agent": self.config["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config["download_timeout"])
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                # Загружаем главную страницу
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    html_content = await response.text(encoding='utf-8', errors='ignore')
                    total_size += len(html_content)
                
                # Парсим HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Извлекаем заголовок
                title = soup.title.string if soup.title else self._extract_domain(url)
                if not title or title.strip() == "":
                    title = self._extract_domain(url)
                
                # Создаем ZIP архив
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Сохраняем оригинальный HTML
                    zip_file.writestr("original.html", html_content)
                    file_count += 1
                    
                    # Создаем улучшенный index.html для локального просмотра
                    enhanced_html = self._create_enhanced_html(url, title, html_content, soup)
                    zip_file.writestr("index.html", enhanced_html.encode('utf-8'))
                    file_count += 1
                    
                    # Создаем README с информацией
                    readme = f"""СКАЧАННЫЙ САЙТ: {url}
===============

ИНФОРМАЦИЯ:
• URL: {url}
• Дата скачивания: {datetime.now().isoformat()}
• Заголовок: {title}
• Статус: Успешно скачан
• Файлов в архиве: {file_count}
• Размер HTML: {len(html_content)} байт

СТРУКТУРА:
• original.html - оригинальная страница
• index.html - улучшенная версия для просмотра

ИНСТРУКЦИЯ:
1. Распакуйте архив
2. Откройте index.html в браузере
3. Для полной функциональности нужен интернет
   (внешние ресурсы не скачаны)

СОЗДАНО:
• Инструмент: FUN-HELPER v3.5
• Разработчик: @zymoyhold
• Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
                    zip_file.writestr("README.txt", readme.encode('utf-8'))
                    file_count += 1
                    
                    # Создаем info.json с метаданными
                    info = {
                        "url": url,
                        "download_date": datetime.now().isoformat(),
                        "title": title,
                        "original_size": len(html_content),
                        "files_count": file_count,
                        "tool": "FUN-HELPER v3.5",
                        "developer": "@zymoyhold"
                    }
                    zip_file.writestr("info.json", json.dumps(info, indent=2, ensure_ascii=False).encode('utf-8'))
                    file_count += 1
            
            zip_buffer.seek(0)
            return zip_buffer.read(), file_count, total_size
            
        except Exception as e:
            print(f"Download error: {e}")
            return None, 0, 0
        finally:
            zip_buffer.close()
    
    def _create_enhanced_html(self, url: str, title: str, html: str, soup: BeautifulSoup) -> str:
        """Создание улучшенного HTML для локального просмотра"""
        # Извлекаем meta description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'][:200]
        
        # Упрощенный HTML для локального просмотра
        enhanced = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📥 {title} - Скачанная копия</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{ 
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ 
            text-align: center;
            padding: 20px;
            background: #4285f4;
            color: white;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .info {{ 
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .frame {{ 
            width: 100%;
            height: 500px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 {title}</h1>
            <p>Скачанная локальная копия сайта</p>
        </div>
        
        <div class="info">
            <p><strong>📎 Оригинальный URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
            <p><strong>📅 Дата скачивания:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            {f'<p><strong>📝 Описание:</strong> {description}</p>' if description else ''}
        </div>
        
        <h2>📄 Оригинальное содержимое:</h2>
        <div class="frame">
            <iframe src="original.html" style="width:100%; height:100%; border:none;"></iframe>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="original.html" target="_blank" style="display:inline-block; padding:10px 20px; background:#4285f4; color:white; text-decoration:none; border-radius:5px; margin:5px;">
                📄 Открыть оригинал
            </a>
            <a href="{url}" target="_blank" style="display:inline-block; padding:10px 20px; background:#34a853; color:white; text-decoration:none; border-radius:5px; margin:5px;">
                🌐 Перейти на сайт
            </a>
        </div>
        
        <div style="text-align: center; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <p>Создано с помощью <strong>FUN-HELPER v3.5</strong> • @zymoyhold</p>
        </div>
    </div>
</body>
</html>"""
        
        return enhanced
    
    def _extract_domain(self, url: str) -> str:
        """Извлечение домена из URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace('www.', '').replace('.', '_')
            domain = re.sub(r'[^\w\-]', '_', domain)
            return domain[:20] if domain else "website"
        except:
            return "website"
    
    # ==================== FUNE - ШИФРОВАНИЕ ====================
    
    @loader.command(
        ru_doc="[метод] [текст] - Шифровать/дешифровать",
        en_doc="[method] [text] - Encrypt/decrypt"
    )
    async def fune(self, message):
        """Шифрование/дешифрование текста"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings["encrypt_options"])
            return
        
        parts = args.split(" ", 1)
        
        if len(parts) < 2:
            await utils.answer(message, "❌ <b>Укажите метод и текст</b>\n\n<code>.fune base64 текст</code>")
            return
        
        method, text = parts
        method = method.lower()
        
        result = ""
        
        if method == "base64":
            result = base64.b64encode(text.encode()).decode()
        elif method == "md5":
            result = hashlib.md5(text.encode()).hexdigest()
        elif method == "sha256":
            result = hashlib.sha256(text.encode()).hexdigest()
        elif method == "rot13":
            result = self._rot13(text)
        elif method == "xor":
            key = "zymoyhold"
            result = self._xor_encrypt(text, key)
        elif method == "decode":
            try:
                result = base64.b64decode(text.encode()).decode('utf-8')
                method = "Base64 Decode"
            except:
                result = "❌ Неверный Base64 формат"
                method = "Ошибка"
        else:
            await utils.answer(message, "❌ <b>Неизвестный метод</b>\n\nДоступно: base64, md5, sha256, rot13, xor, decode")
            return
        
        self.stats["encryptions"] += 1
        self._save_stats()
        
        await utils.answer(
            message,
            self.strings["encrypted"].format(
                method=method.upper(),
                result=utils.escape_html(result)
            )
        )
    
    def _rot13(self, text: str) -> str:
        """Шифрование ROT13"""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def _xor_encrypt(self, text: str, key: str) -> str:
        """Шифрование XOR"""
        encrypted = []
        key_len = len(key)
        for i, char in enumerate(text):
            key_char = key[i % key_len]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted.append(encrypted_char)
        encrypted_text = ''.join(encrypted)
        return base64.b64encode(encrypted_text.encode()).decode()
    
    # ==================== FUNS - GOOGLE ПОИСК ЧЕРЕЗ API ====================
    
    @loader.command(
        ru_doc="[запрос] - Поиск в Google через API",
        en_doc="[query] - Google search via API"
    )
    async def funs(self, message):
        """Поиск информации через Google API"""
        # Проверяем API ключ
        if not self.config["google_api_key"] or not self.config["google_cse_id"]:
            await utils.answer(message, self.strings["search_no_api"])
            return
        
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, 
                "🔍 <b>Google Поиск через API:</b>\n\n"
                "⚡ <code>.funs [запрос]</code>\n\n"
                "💡 <i>Примеры:</i>\n"
                "<code>.funs Python программирование</code>\n"
                "<code>.funs новости технологии</code>\n"
                "<code>.funs как установить Linux</code>\n\n"
                "🔑 <b>API ключ:</b> {api_status}\n"
                "🆔 <b>CSE ID:</b> {cse_status}".format(
                    api_status="✅ Установлен" if self.config["google_api_key"] else "❌ Не установлен",
                    cse_status="✅ Установлен" if self.config["google_cse_id"] else "❌ Не установлен"
                )
            )
            return
        
        query = args.strip()
        
        processing_msg = await utils.answer(
            message,
            self.strings["searching"].format(query=utils.escape_html(query[:50]))
        )
        
        try:
            results = await self._google_search(query)
            
            if not results:
                await utils.answer(
                    processing_msg,
                    "🔍 <b>Результаты не найдены</b>\n\n"
                    f"Запрос: <code>{query}</code>\n\n"
                    "💡 Попробуйте другой запрос или проверьте API ключ"
                )
                return
            
            results_text = ""
            for i, result in enumerate(results[:self.config["search_results_count"]], 1):
                title = result.get("title", "Результат")[:60]
                link = result.get("link", "#")
                snippet = result.get("snippet", "")[:100]
                
                results_text += f"{i}. <b>{title}</b>\n"
                if snippet:
                    results_text += f"   <i>{snippet}...</i>\n"
                results_text += f"   🔗 <code>{link}</code>\n\n"
            
            self.stats["searches"] += 1
            self.stats["api_used"] += 1
            self._save_stats()
            
            await utils.answer(
                processing_msg,
                self.strings["search_results"].format(results=results_text)
            )
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                await utils.answer(processing_msg, self.strings["search_limit"])
            elif "invalid" in error_msg.lower() or "key" in error_msg.lower():
                await utils.answer(
                    processing_msg,
                    "❌ <b>Неверный API ключ или CSE ID</b>\n\n"
                    "Проверьте правильность введенных данных:\n"
                    f"🔑 API ключ: <code>{self.config['google_api_key'][:10]}...</code>\n"
                    f"🆔 CSE ID: <code>{self.config['google_cse_id'][:10]}...</code>\n\n"
                    "Используйте <code>.funapihelp</code> для помощи"
                )
            else:
                await utils.answer(
                    processing_msg,
                    self.strings["search_error"].format(error=error_msg[:200])
                )
    
    async def _google_search(self, query: str) -> List[Dict]:
        """Поиск через Google Custom Search API"""
        api_key = self.config["google_api_key"]
        cse_id = self.config["google_cse_id"]
        
        if not api_key or not cse_id:
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": self.config["search_results_count"],
            "hl": "ru",
            "lr": "lang_ru",
            "safe": "off"
        }
        
        headers = {
            "User-Agent": self.config["user_agent"]
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Google API Error {response.status}: {error_text[:100]}")
                    
                    data = await response.json()
                    
                    if "error" in data:
                        raise Exception(f"Google API Error: {data['error'].get('message', 'Unknown error')}")
                    
                    results = []
                    if "items" in data:
                        for item in data["items"]:
                            result = {
                                "title": item.get("title", ""),
                                "link": item.get("link", ""),
                                "snippet": item.get("snippet", "")
                            }
                            results.append(result)
                    
                    return results
        except Exception as e:
            raise e
    
    # ==================== FUNAPI - УПРАВЛЕНИЕ API КЛЮЧОМ ====================
    
    @loader.command(
        ru_doc="[api_key] [cse_id] - Установить Google API ключ",
        en_doc="[api_key] [cse_id] - Set Google API key"
    )
    async def funapi(self, message):
        """Установить/удалить Google API ключ"""
        args = utils.get_args_raw(message)
        
        if not args:
            # Показать текущий статус
            api_status = "✅ Установлен" if self.config["google_api_key"] else "❌ Не установлен"
            cse_status = "✅ Установлен" if self.config["google_cse_id"] else "❌ Не установлен"
            
            await utils.answer(message,
                "🔑 <b>Google API Настройки:</b>\n\n"
                f"🔑 API ключ: {api_status}\n"
                f"🆔 CSE ID: {cse_status}\n\n"
                f"📊 Использовано поисков: {self.stats['api_used']}\n\n"
                "💡 <b>Команды:</b>\n"
                "<code>.funapi [api_key] [cse_id]</code> - установить\n"
                "<code>.funapi remove</code> - удалить\n"
                "<code>.funapitest</code> - протестировать\n"
                "<code>.funapihelp</code> - помощь по получению"
            )
            return
        
        if args.lower() == "remove":
            # Удаление API ключа
            old_api = self.config["google_api_key"]
            old_cse = self.config["google_cse_id"]
            
            self.config["google_api_key"] = ""
            self.config["google_cse_id"] = ""
            
            await utils.answer(message,
                self.strings["api_removed"] + f"\n\n"
                f"🔑 API ключ: <code>{old_api[:10]}...</code>\n"
                f"🆔 CSE ID: <code>{old_cse[:10]}...</code>"
            )
            return
        
        # Установка API ключа
        parts = args.split()
        
        if len(parts) < 2:
            await utils.answer(message,
                "❌ <b>Укажите API ключ и CSE ID</b>\n\n"
                "<code>.funapi [api_key] [cse_id]</code>\n\n"
                "Пример:\n"
                "<code>.funapi AIzaSyBxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxx</code>\n\n"
                "Используйте <code>.funapihelp</code> для помощи"
            )
            return
        
        api_key = parts[0]
        cse_id = parts[1]
        
        self.config["google_api_key"] = api_key
        self.config["google_cse_id"] = cse_id
        
        await utils.answer(message,
            self.strings["api_saved"].format(api_key=api_key[:20] + "...") + f"\n\n"
            f"🆔 CSE ID: <code>{cse_id[:20]}...</code>\n"
            f"📊 Результатов: {self.config['search_results_count']}\n\n"
            "💡 Теперь можно использовать поиск: <code>.funs [запрос]</code>"
        )
    
    @loader.command(
        ru_doc="Протестировать Google API ключ",
        en_doc="Test Google API key"
    )
    async def funapitest(self, message):
        """Протестировать Google API ключ"""
        if not self.config["google_api_key"] or not self.config["google_cse_id"]:
            await utils.answer(message, self.strings["search_no_api"])
            return
        
        processing_msg = await utils.answer(message, self.strings["api_test"])
        
        try:
            # Тестируем API простым запросом
            results = await self._google_search("test")
            
            if results:
                await utils.answer(
                    processing_msg,
                    self.strings["api_test_success"].format(api_key=self.config["google_api_key"][:20] + "...") + f"\n\n"
                    f"🆔 CSE ID: <code>{self.config['google_cse_id'][:20]}...</code>\n"
                    f"📊 Найдено результатов: {len(results)}\n"
                    f"✅ API ключ рабочий!"
                )
            else:
                await utils.answer(
                    processing_msg,
                    self.strings["api_test_fail"] + f"\n\n"
                    "API вернул пустой ответ\n"
                    "Проверьте CSE ID и настройки поиска"
                )
                
        except Exception as e:
            await utils.answer(
                processing_msg,
                self.strings["api_test_fail"] + f"\n\n"
                f"Ошибка: {str(e)[:200]}"
            )
    
    @loader.command(
        ru_doc="Помощь по получению Google API ключа",
        en_doc="Help for getting Google API key"
    )
    async def funapihelp(self, message):
        """Помощь по получению Google API ключа"""
        help_text = """
<b>🎯 Шаг 1: Создание проекта в Google Cloud</b>
1. Перейдите на <a href="https://console.cloud.google.com/">Google Cloud Console</a>
2. Создайте новый проект или выберите существующий
3. Включите <b>Custom Search API</b> для проекта

<b>🎯 Шаг 2: Получение API ключа</b>
1. В Google Cloud Console перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "API Key"
3. Скопируйте созданный ключ (начинается с AIzaSy...)

<b>🎯 Шаг 3: Создание Custom Search Engine (CSE)</b>
1. Перейдите на <a href="https://programmablesearchengine.google.com/">Google Programmable Search Engine</a>
2. Нажмите "Add" для создания нового поисковика
3. Укажите любые сайты для поиска (можно оставить пустым для поиска по всему интернету)
4. Нажмите "Create" и получите <b>Search engine ID</b>

<b>🎯 Шаг 4: Настройка модуля</b>
<code>.funapi [api_key] [cse_id]</code>
Пример:
<code>.funapi AIzaSyBxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxx</code>

<b>🎯 Шаг 5: Тестирование</b>
<code>.funapitest</code> - проверить работоспособность
<code>.funs Python</code> - выполнить поиск

<b>💡 Важная информация:</b>
• Бесплатный лимит: 100 запросов в день
• Для увеличения лимита нужна оплата
• Ключ безопасен - хранится только локально
• Можно использовать один ключ для нескольких ботов

<b>⚠️ Ограничения:</b>
• Без API ключа поиск не работает
• Лимит запросов обновляется каждый день
• Для коммерческого использования нужна оплата

<b>👨‍💻 Поддержка:</b>
• Разработчик: @zymoyhold
• Версия модуля: FUN-HELPER v3.5
• Для помощи: <code>.funhelp</code>
"""
        
        await utils.answer(
            message,
            self.strings["api_help"].format(help_text=help_text)
        )
    
    # ==================== FUNEE - ЭКСПОРТ ====================
    
    @loader.command(
        ru_doc="Экспорт данных модуля",
        en_doc="Export module data"
    )
    async def funee(self, message):
        """Экспорт данных модуля"""
        processing_msg = await utils.answer(message, self.strings["export_start"])
        
        try:
            # Собираем все данные
            export_data = {
                "module": "FUN-HELPER v3.5",
                "export_date": datetime.now().isoformat(),
                "developer": "@zymoyhold",
                "data": {
                    "replies": self.replies,
                    "stats": self.stats,
                    "config": {
                        "auto_reply_enabled": self.config["auto_reply_enabled"],
                        "max_download_size": self.config["max_download_size"],
                        "download_timeout": self.config["download_timeout"],
                        "search_results_count": self.config["search_results_count"],
                        "google_api_key_set": bool(self.config["google_api_key"]),
                        "google_cse_id_set": bool(self.config["google_cse_id"]),
                    },
                    "version": __version__
                }
            }
            
            # Конвертируем в JSON
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
            # Создаем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"funhelper_export_{timestamp}.json"
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.json', mode='w', encoding='utf-8', delete=False) as tmp_file:
                tmp_file.write(json_data)
                tmp_file.flush()
                
                # Отправляем файл
                await self._client.send_file(
                    message.peer_id,
                    tmp_file.name,
                    caption=self.strings["export_success"].format(
                        filename=filename,
                        records=len(self.replies),
                        size=round(len(json_data) / 1024, 2)
                    )
                )
                
                # Удаляем временный файл
                os.unlink(tmp_file.name)
            
            self.stats["exports"] += 1
            self._save_stats()
            
            await processing_msg.delete()
            
        except Exception as e:
            await utils.answer(
                processing_msg,
                self.strings["export_error"].format(error=str(e)[:200])
            )
    
    # ==================== FUNH - ХЕШИРОВАНИЕ ====================
    
    @loader.command(
        ru_doc="[алгоритм] [текст] - Хеширование текста",
        en_doc="[algorithm] [text] - Hash text"
    )
    async def funh(self, message):
        """Хеширование текста"""
        args = utils.get_args_raw(message)
        
        if not args:
            # Показать доступные алгоритмы
            algorithms_text = "\n".join([f"• <code>{alg}</code>" for alg in self.HASH_ALGORITHMS.keys()])
            
            await utils.answer(
                message,
                self.strings["hash_options"].format(algorithms=algorithms_text)
            )
            return
        
        parts = args.split(" ", 1)
        
        if len(parts) < 2:
            await utils.answer(message, "❌ <b>Укажите алгоритм и текст</b>\n\n<code>.funh md5 текст</code>")
            return
        
        algorithm, text = parts
        algorithm = algorithm.lower()
        
        if algorithm not in self.HASH_ALGORITHMS:
            await utils.answer(
                message,
                self.strings["hash_error"].format(algorithm=algorithm)
            )
            return
        
        # Вычисляем хеш
        hash_func = self.HASH_ALGORITHMS[algorithm]
        result = hash_func(text.encode()).hexdigest()
        
        self.stats["hashes"] += 1
        self._save_stats()
        
        await utils.answer(
            message,
            self.strings["hashed"].format(
                algorithm=algorithm.upper(),
                result=utils.escape_html(result)
            )
        )
    
    # ==================== WATCHER - АВТООТВЕТЧИК ====================
    
    async def watcher(self, message):
        """Обработчик входящих сообщений для автоответов"""
        if not self.config["auto_reply_enabled"]:
            return
        
        if not message.text or message.out:
            return
        
        sender_id = message.sender_id
        if sender_id == self.me.id:
            return
        
        text = message.text.lower()
        
        for trigger, response in self.replies.items():
            if trigger in text:
                await asyncio.sleep(0.5)
                await message.reply(response)
                self.stats["replies_used"] += 1
                self._save_stats()
                break
    
    # ==================== ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ====================
    
    @loader.command(
        ru_doc="Статистика модуля",
        en_doc="Module statistics"
    )
    async def funstats(self, message):
        """Статистика модуля"""
        stats_text = f"""
📊 <b>Статистика FUN-HELPER v3.5:</b>

🌐 <b>Скачивания сайтов:</b> {self.stats["downloads"]}
🔍 <b>Поисковые запросы:</b> {self.stats["searches"]}
🔐 <b>Операции шифрования:</b> {self.stats["encryptions"]}
🤖 <b>Использовано автоответов:</b> {self.stats["replies_used"]}
📤 <b>Экспортов данных:</b> {self.stats["exports"]}
🔢 <b>Хеширований:</b> {self.stats["hashes"]}
🔑 <b>Использовано API:</b> {self.stats["api_used"]}

📝 <b>Автоответов в базе:</b> {len(self.replies)}
⚙️ <b>Автоответчик:</b> {'🟢 ВКЛ' if self.config['auto_reply_enabled'] else '🔴 ВЫКЛ'}
📦 <b>Макс. размер архива:</b> {self.config['max_download_size']} MB
🔍 <b>Результатов поиска:</b> {self.config['search_results_count']}
🔑 <b>Google API:</b> {'✅ Настроен' if self.config['google_api_key'] else '❌ Не настроен'}

👨‍💻 <b>Разработчик:</b> @zymoyhold
"""
        await utils.answer(message, stats_text)
    
    @loader.command(
        ru_doc="Помощь по модулю",
        en_doc="Module help"
    )
    async def funhelp(self, message):
        """Помощь по модулю"""
        help_text = """
🛠️ <b>FUN-HELPER v3.5 - Помощь</b>

🔹 <b>Автоответчик:</b>
<code>.funr привет Привет! Как дела?</code> - добавить
<code>.funr привет</code> - удалить
<code>.funr</code> - список автоответов

🔹 <b>Скачивание сайтов:</b>
<code>.funp example.com</code> - скачать сайт в ZIP

🔹 <b>Шифрование:</b>
<code>.fune base64 текст</code> - Base64
<code>.fune md5 текст</code> - MD5
<code>.fune sha256 текст</code> - SHA256
<code>.fune rot13 текст</code> - ROT13
<code>.fune xor текст</code> - XOR
<code>.fune decode [base64]</code> - декодирование

🔹 <b>Google Поиск (API):</b>
<code>.funapi [ключ] [cse_id]</code> - установить API
<code>.funapi remove</code> - удалить API
- <code>.funs запрос</code> - поиск
- <code>.funapitest</code> - тест API
- <code>.funapihelp</code> - помощь по API

🔹 <b>Экспорт данных:</b>
<code>.funee</code> - экспорт всех данных в JSON

🔹 <b>Хеширование:</b>
<code>.funh md5 текст</code> - MD5 хеш
<code>.funh sha256 текст</code> - SHA256
и другие алгоритмы...

🔹 <b>Дополнительно:</b>
<code>.funstats</code> - статистика
<code>.funautoreply</code> - вкл/выкл автоответчик
<code>.funclear</code> - очистить автоответы

👨‍💻 <b>Разработчик:</b> @zymoyhold
"""
        await utils.answer(message, help_text)
    
    @loader.command(
        ru_doc="Включить/выключить автоответчик",
        en_doc="Enable/disable auto reply"
    )
    async def funautoreply(self, message):
        """Управление автоответчиком"""
        current = self.config["auto_reply_enabled"]
        new_value = not current
        
        self.config["auto_reply_enabled"] = new_value
        
        status = "🟢 ВКЛЮЧЕН" if new_value else "🔴 ВЫКЛЮЧЕН"
        await utils.answer(
            message,
            f"⚙️ <b>Автоответчик</b> {status}\n\n"
            f"📊 Автоответов: {len(self.replies)}\n"
            f"💡 <code>.funr [триггер] [ответ]</code>"
        )
    
    @loader.command(
        ru_doc="Очистить все автоответы",
        en_doc="Clear all auto replies"
    )
    async def funclear(self, message):
        """Очистить все автоответы"""
        count = len(self.replies)
        self.replies = {}
        self._save_replies()
        
        await utils.answer(
            message,
            f"🧹 <b>Очищено {count} автоответов</b>\n\n"
            f"Автоответчик отключен до добавления новых правил"
        )
    
    @loader.command(
        ru_doc="Тест модуля",
        en_doc="Module test"
    )
    async def funtest(self, message):
        """Тест модуля"""
        test_results = []
        
        # Проверяем базовые функции
        try:
            test_text = "test123"
            base64_result = base64.b64encode(test_text.encode()).decode()
            test_results.append("✅ Base64 шифрование работает")
        except:
            test_results.append("❌ Base64 шифрование не работает")
        
        # Проверяем хеширование
        try:
            md5_result = hashlib.md5(test_text.encode()).hexdigest()
            test_results.append("✅ MD5 хеширование работает")
        except:
            test_results.append("❌ MD5 хеширование не работает")
        
        # Проверяем BeautifulSoup
        test_results.append(f"✅ BeautifulSoup4: {'Установлен' if HAS_BS4 else 'Не установлен'}")
        
        # Проверяем Google API
        api_status = "✅ Настроен" if self.config["google_api_key"] and self.config["google_cse_id"] else "❌ Не настроен"
        test_results.append(f"✅ Google API: {api_status}")
        
        # Статистика
        test_results.append(f"✅ Автоответов: {len(self.replies)}")
        test_results.append(f"✅ Скачиваний: {self.stats['downloads']}")
        test_results.append(f"✅ Поисков: {self.stats['searches']}")
        test_results.append(f"✅ Экспортов: {self.stats['exports']}")
        
        result_text = "🧪 <b>Тест FUN-HELPER v3.5:</b>\n\n" + "\n".join(test_results)
        
        await utils.answer(message, result_text)