import sqlite3
import os

SIM_DB = os.path.join(os.path.dirname(__file__), "simulation.db")
CHAT_DB = os.path.join(os.path.dirname(__file__), "chat.db")


def get_sim_db():
    conn = sqlite3.connect(SIM_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_chat_db():
    conn = sqlite3.connect(CHAT_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_chat_db():
    conn = get_chat_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def init_member_ops_db():
    """Ensure member operations tables exist in the simulation database."""
    conn = get_sim_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS comp_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patron_id TEXT NOT NULL,
                comp_type TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'issued',
                issued_by TEXT,
                approved_by TEXT,
                issue_date TEXT NOT NULL,
                expiry_date TEXT,
                redeem_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                room_type TEXT NOT NULL,
                floor INTEGER NOT NULL,
                rate REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
                features TEXT
            );

            CREATE TABLE IF NOT EXISTS room_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patron_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                total_rate REAL,
                comped INTEGER DEFAULT 0,
                booking_date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS fb_reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patron_id TEXT NOT NULL,
                venue TEXT NOT NULL,
                reservation_date TEXT NOT NULL,
                reservation_time TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                special_requests TEXT,
                total_spend REAL,
                comped_amount REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS credit_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patron_id TEXT NOT NULL UNIQUE,
                credit_limit REAL NOT NULL,
                signing_limit REAL NOT NULL,
                current_balance REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                issued_date TEXT NOT NULL,
                review_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS live_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                patron_id TEXT,
                details TEXT,
                amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ai_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patron_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                confidence REAL NOT NULL,
                estimated_impact TEXT,
                status TEXT NOT NULL DEFAULT 'suggested',
                params TEXT,
                approved_by TEXT,
                executed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_comp_patron ON comp_transactions(patron_id);
            CREATE INDEX IF NOT EXISTS idx_comp_status ON comp_transactions(status);
            CREATE INDEX IF NOT EXISTS idx_bookings_patron ON room_bookings(patron_id);
            CREATE INDEX IF NOT EXISTS idx_bookings_room ON room_bookings(room_id);
            CREATE INDEX IF NOT EXISTS idx_bookings_dates ON room_bookings(check_in, check_out);
            CREATE INDEX IF NOT EXISTS idx_fb_patron ON fb_reservations(patron_id);
            CREATE INDEX IF NOT EXISTS idx_fb_date ON fb_reservations(reservation_date);
            CREATE INDEX IF NOT EXISTS idx_credit_patron ON credit_lines(patron_id);
            CREATE INDEX IF NOT EXISTS idx_live_events_type ON live_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_live_events_created ON live_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_ai_actions_patron ON ai_actions(patron_id);
            CREATE INDEX IF NOT EXISTS idx_ai_actions_status ON ai_actions(status);
        """)
        conn.commit()
    finally:
        conn.close()
