import random
import sqlite3
from datetime import datetime
from .. import loader, utils
import logging

logger = logging.getLogger(__name__)

@loader.tds
class FunGameFTG(loader.Module):
    """🎮 FunGame для юзербота"""
    
    strings = {
        "name": "FunGame",
        "start": "🎮 **FunGame запущен!**\nОснователь: @zymoyhold\nСпонсор: @funcrmp",
        "profile": """
👤 **Профиль**
💰 Баланс: {}
🏆 Уровень: {}
📈 XP: {}/100
🎰 Игр: {}
🍀 Выиграно: {}""",
        "no_player": "❌ Сначала напиши `.fungame`",
        "low_balance": "⚠️ Недостаточно монет!",
        "daily_today": "🎁 Сегодня уже получал!",
        "daily_got": "🎁 Бонус {} монет! Баланс: {}",
        "game_win": "🎉 Выигрыш {}! Баланс: {}",
        "game_lose": "😔 Проигрыш {}. Баланс: {}",
        "game_tie": "🤝 Ничья. Баланс: {}",
        "top_empty": "🏆 Топ пуст!",
        "admin_only": "⚠️ Только для админов!",
        "coins_added": "✅ Игроку {} добавлено {} монет",
        "player_not_found": "❌ Игрок не найден",
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "admin_ids",
                [8036003277],
                "ID администраторов",
                validator=loader.validators.Series(
                    validator=loader.validators.Integer()
                )
            ),
            loader.ConfigValue(
                "start_balance",
                1000,
                "Начальный баланс",
                validator=loader.validators.Integer(minimum=100)
            ),
        )
        self.db_path = "fungame_lite.db"
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Игроки
            c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                daily TEXT,
                created TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB init error: {e}")
    
    def _get_player(self, uid):
        """Получить игрока"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM players WHERE user_id = ?", (uid,))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'balance': row[1],
                    'level': row[2],
                    'xp': row[3],
                    'games': row[4],
                    'wins': row[5],
                    'daily': row[6],
                    'created': row[7]
                }
        except:
            pass
        return None
    
    def _save_player(self, player):
        """Сохранить игрока"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Проверяем существование
            c.execute("SELECT user_id FROM players WHERE user_id = ?", (player['user_id'],))
            exists = c.fetchone()
            
            if exists:
                # Обновляем
                c.execute('''
                UPDATE players SET 
                    balance = ?, level = ?, xp = ?, games = ?, wins = ?, daily = ?
                WHERE user_id = ?
                ''', (
                    player['balance'],
                    player.get('level', 1),
                    player.get('xp', 0),
                    player.get('games', 0),
                    player.get('wins', 0),
                    player.get('daily'),
                    player['user_id']
                ))
            else:
                # Создаем нового
                c.execute('''
                INSERT INTO players (user_id, balance, level, xp, games, wins, daily)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player['user_id'],
                    player['balance'],
                    player.get('level', 1),
                    player.get('xp', 0),
                    player.get('games', 0),
                    player.get('wins', 0),
                    player.get('daily')
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Save player error: {e}")
            return False
    
    def _add_xp(self, uid, amount):
        """Добавить опыт"""
        p = self._get_player(uid)
        if not p:
            return False
        
        p['xp'] = p.get('xp', 0) + amount
        old_level = p.get('level', 1)
        new_level = p['xp'] // 100 + 1
        
        if new_level > old_level:
            p['level'] = new_level
            p['balance'] += new_level * 100  # Бонус за уровень
        
        return self._save_player(p)
    
    def _get_top(self, limit=10):
        """Получить топ игроков"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            SELECT user_id, balance, level, wins, games 
            FROM players 
            ORDER BY balance DESC 
            LIMIT ?
            ''', (limit,))
            
            rows = c.fetchall()
            conn.close()
            
            result = []
            for row in rows:
                result.append({
                    'user_id': row[0],
                    'balance': row[1],
                    'level': row[2],
                    'wins': row[3],
                    'games': row[4]
                })
            return result
        except:
            return []
    
    def _is_admin(self, uid):
        """Проверка админских прав"""
        admins = set(self.config.get('admin_ids', [8036003277]))
        admins.add(8036003277)  # Твой ID всегда админ
        
        if hasattr(self, 'me'):
            admins.add(self.me.id)  # Владелец юзербота тоже админ
        
        return uid in admins
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.me = await client.get_me()
        logger.info(f"FunGame загружен для {self.me.id}")
    
    @loader.command()
    async def fungame(self, message):
        """🎮 Активировать FunGame"""
        user_id = message.sender_id
        
        # Создаем или получаем игрока
        player = self._get_player(user_id)
        if not player:
            player = {
                'user_id': user_id,
                'balance': self.config['start_balance'],
                'level': 1,
                'xp': 0,
                'games': 0,
                'wins': 0,
                'daily': None
            }
            self._save_player(player)
            await utils.answer(message, self.strings["start"])
        else:
            await utils.answer(message, "🎮 FunGame уже активен!")
    
    @loader.command()
    async def profile(self, message):
        """👤 Мой профиль"""
        user_id = message.sender_id
        player = self._get_player(user_id)
        
        if not player:
            await utils.answer(message, self.strings["no_player"])
            return
        
        xp_current = player['xp'] % 100
        text = self.strings["profile"].format(
            player['balance'],
            player['level'],
            xp_current,
            player['games'],
            player['wins'] * 100  # Примерная сумма выигрышей
        )
        
        text += f"\n\n👑 **Админы:**\nОснователь: @zymoyhold\nСпонсор: @funcrmp"
        
        await utils.answer(message, text)
    
    @loader.command()
    async def daily(self, message):
        """🎁 Ежедневный бонус"""
        user_id = message.sender_id
        player = self._get_player(user_id)
        
        if not player:
            await utils.answer(message, self.strings["no_player"])
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if player.get('daily') == today:
            await utils.answer(message, self.strings["daily_today"])
            return
        
        # Выдаем бонус
        bonus = random.randint(50, 200)
        player['balance'] += bonus
        player['daily'] = today
        self._save_player(player)
        
        await utils.answer(
            message, 
            self.strings["daily_got"].format(bonus, player['balance'])
        )
    
    @loader.command()
    async def dice(self, message):
        """🎲 Игра в кости (ставка: 100)"""
        user_id = message.sender_id
        player = self._get_player(user_id)
        
        if not player:
            await utils.answer(message, self.strings["no_player"])
            return
        
        bet = 100
        
        if player['balance'] < bet:
            await utils.answer(message, self.strings["low_balance"])
            return
        
        # Игра
        player_num = random.randint(1, 6)
        bot_num = random.randint(1, 6)
        
        player['games'] += 1
        
        if player_num > bot_num:
            # Победа
            win_amount = bet * 2
            player['balance'] += win_amount
            player['wins'] += 1
            result = self.strings["game_win"].format(win_amount, player['balance'])
        elif player_num < bot_num:
            # Проигрыш
            player['balance'] -= bet
            result = self.strings["game_lose"].format(bet, player['balance'])
        else:
            # Ничья
            result = self.strings["game_tie"].format(player['balance'])
        
        # Добавляем опыт
        self._add_xp(user_id, 10)
        
        # Сохраняем
        self._save_player(player)
        
        result = f"🎲 **Кости**\nТы: {player_num} | Бот: {bot_num}\n{result}"
        await utils.answer(message, result)
    
    @loader.command()
    async def coin(self, message):
        """🪙 Подбросить монету (ставка: 50)"""
        user_id = message.sender_id
        player = self._get_player(user_id)
        
        if not player:
            await utils.answer(message, self.strings["no_player"])
            return
        
        bet = 50
        
        if player['balance'] < bet:
            await utils.answer(message, self.strings["low_balance"])
            return
        
        # Игра
        choices = ["орёл", "решка"]
        player_choice = random.choice(choices)
        bot_choice = random.choice(choices)
        
        player['games'] += 1
        
        if player_choice == bot_choice:
            # Победа
            win_amount = bet * 2
            player['balance'] += win_amount
            player['wins'] += 1
            result = self.strings["game_win"].format(win_amount, player['balance'])
        else:
            # Проигрыш
            player['balance'] -= bet
            result = self.strings["game_lose"].format(bet, player['balance'])
        
        # Опыт
        self._add_xp(user_id, 5)
        
        # Сохраняем
        self._save_player(player)
        
        result = f"🪙 **Монетка**\nТы: {player_choice} | Бот: {bot_choice}\n{result}"
        await utils.answer(message, result)
    
    @loader.command()
    async def top(self, message):
        """🏆 Топ игроков"""
        top_players = self._get_top(10)
        
        if not top_players:
            await utils.answer(message, self.strings["top_empty"])
            return
        
        text = "🏆 **ТОП ИГРОКОВ**\n\n"
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, player in enumerate(top_players):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            text += f"{medal} Игрок {player['user_id']}\n"
            text += f"   💰 {player['balance']} | 🏆 Ур. {player['level']}\n"
            text += f"   ✅ {player['wins']}/{player['games']} побед\n\n"
        
        text += "**Основатель:** @zymoyhold\n**Спонсор:** @funcrmp"
        
        await utils.answer(message, text)
    
    @loader.command()
    async def gameadd(self, message):
        """➕ [ADMIN] Добавить монеты"""
        user_id = message.sender_id
        
        if not self._is_admin(user_id):
            await utils.answer(message, self.strings["admin_only"])
            return
        
        args = utils.get_args(message)
        if len(args) < 2:
            await utils.answer(message, "❌ Использование: `.gameadd <сумма> <id>`")
            return
        
        try:
            amount = int(args[0])
            target_id = int(args[1])
            
            player = self._get_player(target_id)
            if not player:
                await utils.answer(message, self.strings["player_not_found"])
                return
            
            player['balance'] += amount
            self._save_player(player)
            
            await utils.answer(
                message,
                self.strings["coins_added"].format(target_id, amount)
            )
        except ValueError:
            await utils.answer(message, "❌ Неверные числа!")
    
    @loader.command()
    async def gamestats(self, message):
        """📊 Статистика модуля"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Общая статистика
            c.execute("SELECT COUNT(*) FROM players")
            total_players = c.fetchone()[0]
            
            c.execute("SELECT SUM(balance) FROM players")
            total_balance = c.fetchone()[0] or 0
            
            c.execute("SELECT SUM(games) FROM players")
            total_games = c.fetchone()[0] or 0
            
            conn.close()
            
            stats = f"""
📊 **СТАТИСТИКА FUNGAME**

👥 Игроков: {total_players}
💰 Всего монет: {total_balance}
🎮 Всего игр: {total_games}
👑 Админов: {len(self.config.get('admin_ids', []))}

**Команды:**
`.fungame` - Активация
`.profile` - Профиль
`.daily` - Бонус
`.dice` - Кости (100)
`.coin` - Монетка (50)
`.top` - Топ игроков
`.gameadd` - [ADMIN] Добавить монеты

**Авторы:**
Основатель: @zymoyhold
Спонсор: @funcrmp
"""
            await utils.answer(message, stats)
        except:
            await utils.answer(message, "❌ Ошибка статистики")