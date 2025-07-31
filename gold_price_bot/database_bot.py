import aiosqlite

DB_PATH = "settings.db"

async def setup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                buy_offset INTEGER DEFAULT 0,
                sell_offset INTEGER DEFAULT 0,
                source_channel TEXT DEFAULT '',
                source_channel_id INTEGER DEFAULT 0,
                is_enabled INTEGER DEFAULT 1,
                buy_extra_misqal INTEGER DEFAULT 0,
                buy_extra_gram INTEGER DEFAULT 0,
                sell_reduce_misqal INTEGER DEFAULT 0,
                sell_reduce_gram INTEGER DEFAULT 0
            )
        ''')
        await db.execute('INSERT OR IGNORE INTO settings (id) VALUES (1)')
        await db.commit()

async def update_offsets(buy_offset, sell_offset):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE settings SET buy_offset = ?, sell_offset = ? WHERE id = 1', (buy_offset, sell_offset))
        await db.commit()

async def get_offsets():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT buy_offset, sell_offset FROM settings WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            return row if row else (0, 0)


async def update_source_channel(source_channel, channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE settings SET source_channel = ?, source_channel_id = ? WHERE id = 1',
                         (source_channel, channel_id))
        await db.commit()

async def get_source_channel():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT source_channel FROM settings WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_source_channel_id():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT source_channel_id FROM settings WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_enabled(status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE settings SET is_enabled = ? WHERE id = 1', (1 if status else 0,))
        await db.commit()

async def is_enabled():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT is_enabled FROM settings WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            return row[0] == 1 if row else True

async def set_price_adjustments(buy_misqal, buy_gram, sell_misqal, sell_gram):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE settings 
            SET 
                buy_extra_misqal = ?, 
                buy_extra_gram = ?, 
                sell_reduce_misqal = ?, 
                sell_reduce_gram = ?
            WHERE id = 1
        ''', (buy_misqal, buy_gram, sell_misqal, sell_gram))
        await db.commit()

async def get_price_adjustments():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT 
                buy_extra_misqal, 
                buy_extra_gram, 
                sell_reduce_misqal, 
                sell_reduce_gram 
            FROM settings WHERE id = 1
        ''') as cursor:
            row = await cursor.fetchone()
            return row if row else (0, 0, 0, 0)
