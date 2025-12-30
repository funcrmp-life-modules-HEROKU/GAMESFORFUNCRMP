"""
    🔧 FUNGH - Мониторинг GitHub репозиториев
"""

__version__ = (1, 1, 0)

# meta developer: @zymoyhold
# requires: aiohttp

import aiohttp, asyncio, json, time, hashlib, re
from datetime import datetime
from typing import Dict, List, Set
from .. import loader, utils

@loader.tds
class FunGithubMod(loader.Module):
    """FUNGH - Мониторинг GitHub репозиториев"""
    strings = {"name": "FUNGH"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("github_token", "", "GitHub API токен"),
            loader.ConfigValue("monitor_channel", "", "Канал для уведомлений (@username)"),
        )
        self.monitoring = False
        self.repos = {}  # repo_name: {"last_commit": "", "files": {}}
        self.session = None

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.me = await client.get_me()
        self.repos = self._db.get(__name__, "repos", {})
        self.session = aiohttp.ClientSession(headers={
            "User-Agent": "Mozilla/5.0",
            "Authorization": f"token {self.config['github_token']}" if self.config['github_token'] else ""
        })

    def _save_repos(self):
        self._db.set(__name__, "repos", self.repos)

    # ==================== ОСНОВНЫЕ КОМАНДЫ ====================
    @loader.command()
    async def funghapi(self, m):
        """Установить GitHub API токен"""
        args = utils.get_args_raw(m)
        if not args:
            token_status = "✅ Установлен" if self.config['github_token'] else "❌ Не установлен"
            await utils.answer(m, f"🔑 <b>GitHub API токен:</b> {token_status}")
            return
        
        self.config["github_token"] = args.strip()
        if self.session:
            self.session.headers["Authorization"] = f"token {args.strip()}"
        
        await utils.answer(m, f"✅ <b>GitHub API токен установлен!</b>\n\n🔑 <code>{args[:10]}...</code>")

    @loader.command()
    async def ghchannel(self, m):
        """Установить канал для уведомлений"""
        args = utils.get_args_raw(m)
        if not args:
            channel = self.config['monitor_channel']
            status = f"<code>{channel}</code>" if channel else "❌ Не установлен"
            await utils.answer(m, f"📢 <b>Канал для уведомлений:</b> {status}")
            return
        
        channel = args.strip().replace('@', '')
        self.config["monitor_channel"] = channel
        
        await utils.answer(m, f"✅ <b>Канал установлен:</b> @{channel}")

    @loader.command()
    async def startgh(self, m):
        """Запустить мониторинг репозиториев"""
        if not self.config['github_token']:
            await utils.answer(m, "❌ <b>Установите GitHub API токен:</b>\n<code>.funghapi [ваш_токен]</code>")
            return
        
        if not self.config['monitor_channel']:
            await utils.answer(m, "❌ <b>Установите канал для уведомлений:</b>\n<code>.ghchannel [@username]</code>")
            return
        
        if self.monitoring:
            await utils.answer(m, "❌ <b>Мониторинг уже запущен!</b>")
            return
        
        self.monitoring = True
        await utils.answer(m, 
            "🚀 <b>Мониторинг GitHub запущен!</b>\n\n"
            f"🔑 API токен: <code>{self.config['github_token'][:10]}...</code>\n"
            f"📢 Канал: @{self.config['monitor_channel']}\n"
            f"📊 Отслеживаем: {len(self.repos)} репозиториев\n\n"
            "⚡ <i>Начинаю отслеживание изменений...</i>"
        )
        
        asyncio.create_task(self._monitor_loop())

    @loader.command()
    async def stopgh(self, m):
        """Остановить мониторинг"""
        if not self.monitoring:
            await utils.answer(m, "❌ <b>Мониторинг не запущен!</b>")
            return
        
        self.monitoring = False
        await utils.answer(m, "🛑 <b>Мониторинг остановлен!</b>")

    @loader.command()
    async def funall(self, m):
        """Просмотреть все репозитории и файлы"""
        if not self.config['github_token']:
            await utils.answer(m, "❌ <b>Установите GitHub API токен:</b>\n<code>.funghapi [ваш_токен]</code>")
            return
        
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, "🔍 <b>Формат:</b>\n<code>.funall [owner/repo]</code>")
            return
        
        try:
            repo = args.strip()
            await utils.answer(m, f"🔍 <b>Сканирую репозиторий:</b> {repo}")
            
            # Получаем информацию о репозитории
            repo_info = await self._get_repo_info(repo)
            if not repo_info:
                await utils.answer(m, f"❌ <b>Репозиторий не найден:</b> {repo}")
                return
            
            # Получаем список файлов
            files = await self._get_repo_files(repo)
            
            # Сохраняем в отслеживаемые
            self.repos[repo] = {
                "last_commit": repo_info.get("pushed_at", ""),
                "files": {f["path"]: f.get("sha", "") for f in files[:50]},
                "last_check": time.time()
            }
            self._save_repos()
            
            await utils.answer(m,
                f"✅ <b>Репозиторий добавлен:</b> {repo}\n"
                f"📁 Файлов: {len(files)}\n"
                f"⭐ Звезд: {repo_info.get('stargazers_count', 0)}\n"
                f"🔄 Последний коммит: {repo_info.get('pushed_at', '')[:10]}"
            )
            
        except Exception as e:
            await utils.answer(m, f"❌ <b>Ошибка:</b>\n{str(e)[:100]}")

    @loader.command()
    async def funlist(self, m):
        """Список отслеживаемых репозиториев"""
        if not self.repos:
            await utils.answer(m, "📭 <b>Нет отслеживаемых репозиториев</b>")
            return
        
        text = "📋 <b>Отслеживаемые репозитории:</b>\n\n"
        for i, (repo, data) in enumerate(self.repos.items(), 1):
            files_count = len(data.get("files", {}))
            last_check = datetime.fromtimestamp(data.get("last_check", 0)).strftime("%H:%M") if data.get("last_check") else "никогда"
            text += f"{i}. <b>{repo}</b>\n   📁 {files_count} файлов | 🔄 {last_check}\n"
        
        await utils.answer(m, text)

    @loader.command()
    async def funremove(self, m):
        """Удалить репозиторий из отслеживания"""
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, "🗑️ <b>Формат:</b>\n<code>.funremove [owner/repo]</code>")
            return
        
        repo = args.strip()
        if repo in self.repos:
            del self.repos[repo]
            self._save_repos()
            await utils.answer(m, f"✅ <b>Репозиторий удален:</b> {repo}")
        else:
            await utils.answer(m, f"❌ <b>Репозиторий не найден:</b> {repo}")

    # ==================== ОСНОВНОЙ ЦИКЛ МОНИТОРИНГА ====================
    async def _monitor_loop(self):
        """Цикл мониторинга репозиториев"""
        while self.monitoring:
            try:
                for repo in list(self.repos.keys()):
                    if not self.monitoring:
                        break
                    
                    # Проверяем обновления
                    await self._check_repo_updates(repo)
                    
                    # Пауза между проверками репозиториев
                    await asyncio.sleep(2)
                
                # Пауза между циклами
                if self.monitoring:
                    await asyncio.sleep(60)  # Проверка каждую минуту
                    
            except Exception as e:
                print(f"FUNGH error: {e}")
                await asyncio.sleep(10)

    async def _check_repo_updates(self, repo: str):
        """Проверка обновлений в репозитории"""
        try:
            # Получаем информацию о репозитории
            repo_info = await self._get_repo_info(repo)
            if not repo_info:
                return
            
            last_push = repo_info.get("pushed_at")
            repo_data = self.repos[repo]
            
            # Проверяем новые коммиты
            if last_push != repo_data.get("last_commit"):
                # Есть новые коммиты
                await self._process_new_commits(repo, repo_info, repo_data)
            
            # Проверяем изменения файлов (стриминг содержимого)
            await self._check_file_changes(repo, repo_data)
            
            # Обновляем время последней проверки
            repo_data["last_check"] = time.time()
            self._save_repos()
            
        except Exception as e:
            print(f"Check updates error for {repo}: {e}")

    async def _process_new_commits(self, repo: str, repo_info: dict, repo_data: dict):
        """Обработка новых коммитов"""
        try:
            # Получаем последние коммиты
            commits = await self._get_repo_commits(repo, repo_data.get("last_commit"))
            
            if commits:
                # Отправляем уведомление
                message = f"🔄 <b>Новые коммиты в {repo}</b>\n\n"
                
                for commit in commits[:3]:  # Показываем 3 последних коммита
                    author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
                    message_text = commit.get("commit", {}).get("message", "No message")
                    date = commit.get("commit", {}).get("author", {}).get("date", "")[:10]
                    
                    message += f"👤 <b>{author}</b> [{date}]\n"
                    message += f"💬 {message_text[:100]}...\n"
                    message += f"🔗 <code>{commit.get('html_url', '')}</code>\n\n"
                
                await self._send_to_channel(message)
                
                # Обновляем последний коммит
                repo_data["last_commit"] = repo_info.get("pushed_at")
        
        except Exception as e:
            print(f"Process commits error: {e}")

    async def _check_file_changes(self, repo: str, repo_data: dict):
        """Проверка изменений в файлах (стриминг содержимого)"""
        try:
            current_files = await self._get_repo_files(repo)
            old_files = repo_data.get("files", {})
            
            # Проверяем новые файлы
            new_files = []
            changed_files = []
            
            for file in current_files[:100]:  # Ограничиваем 100 файлов
                file_path = file.get("path")
                file_sha = file.get("sha", "")
                
                if file_path not in old_files:
                    # Новый файл
                    new_files.append(file_path)
                elif old_files.get(file_path) != file_sha:
                    # Файл изменился
                    changed_files.append(file_path)
            
            # Отправляем уведомления
            if new_files:
                message = f"📁 <b>Новые файлы в {repo}</b>\n\n"
                for file in new_files[:5]:  # Показываем 5 новых файлов
                    message += f"➕ <code>{file}</code>\n"
                if len(new_files) > 5:
                    message += f"\n... и еще {len(new_files) - 5} файлов\n"
                
                await self._send_to_channel(message)
            
            if changed_files:
                message = f"✏️ <b>Измененные файлы в {repo}</b>\n\n"
                for file in changed_files[:5]:
                    message += f"📝 <code>{file}</code>\n"
                if len(changed_files) > 5:
                    message += f"\n... и еще {len(changed_files) - 5} файлов\n"
                
                await self._send_to_channel(message)
            
            # Обновляем хеши файлов
            repo_data["files"] = {f["path"]: f.get("sha", "") for f in current_files[:100]}
            
        except Exception as e:
            print(f"Check file changes error: {e}")

    # ==================== GITHUB API МЕТОДЫ ====================
    async def _get_repo_info(self, repo: str) -> dict:
        """Получение информации о репозитории"""
        try:
            url = f"https://api.github.com/repos/{repo}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return None

    async def _get_repo_commits(self, repo: str, since_commit: str = "") -> list:
        """Получение коммитов репозитория"""
        try:
            url = f"https://api.github.com/repos/{repo}/commits"
            params = {"per_page": 10}
            if since_commit:
                # Здесь должна быть логика фильтрации по времени
                pass
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return []

    async def _get_repo_files(self, repo: str) -> list:
        """Получение списка файлов репозитория"""
        try:
            url = f"https://api.github.com/repos/{repo}/contents"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return []

    # ==================== УТИЛИТЫ ====================
    async def _send_to_channel(self, message: str):
        """Отправка сообщения в канал"""
        try:
            channel = self.config['monitor_channel']
            if channel:
                await self._client.send_message(f"@{channel}", message)
        except Exception as e:
            print(f"Send to channel error: {e}")

    # ==================== CLEANUP ====================
    async def on_unload(self):
        """Очистка при выгрузке модуля"""
        if self.session:
            await self.session.close()
        self.monitoring = False