import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

DB_FILE = "financial_data.db"
NUM_NORMAL_USERS = 2000
NUM_FRAUD_USERS = 5
NUM_TRANSACTIONS = 50000
FRAUD_TRANSACTION_PROB = 0.8

def create_database_schema(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("DROP TABLE IF EXISTS users;")

    cursor.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        country_code TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_time TEXT NOT NULL,
        FOREIGN KEY(sender_id) REFERENCES users(user_id),
        FOREIGN KEY(receiver_id) REFERENCES users(user_id)
    );
    """)
    conn.commit()
    print("Database schema created successfully.")

def generate_and_load_data(conn):
    fake = Faker()
    cursor = conn.cursor()
    generated_usernames = set()

    print(f"Generating {NUM_NORMAL_USERS} normal users...")
    all_users = []
    while len(all_users) < NUM_NORMAL_USERS:
        username = fake.user_name()
        if username not in generated_usernames:
            user_id = len(all_users) + 1
            all_users.append((user_id, username, fake.date_time_this_year().isoformat(), fake.country_code()))
            generated_usernames.add(username)

    print(f"Generating {NUM_FRAUD_USERS} fraud ring users...")
    fraud_ring_start_id = NUM_NORMAL_USERS + 1
    fraud_ring_ids = list(range(fraud_ring_start_id, fraud_ring_start_id + NUM_FRAUD_USERS))
    fraud_user_count = 0
    while fraud_user_count < NUM_FRAUD_USERS:
        username = fake.user_name()
        if username not in generated_usernames:
            user_id = fraud_ring_start_id + fraud_user_count
            all_users.append((user_id, username, (datetime.now() - timedelta(days=1)).isoformat(), fake.country_code()))
            generated_usernames.add(username)
            fraud_user_count += 1

    cursor.executemany("INSERT INTO users (user_id, username, created_at, country_code) VALUES (?, ?, ?, ?)", all_users)
    
    print(f"Generating {NUM_TRANSACTIONS} transactions...")
    transactions = []
    start_date = datetime.now() - timedelta(days=365)
    for _ in range(NUM_TRANSACTIONS):
        is_fraud = random.random() < 0.1
        if is_fraud and random.random() < FRAUD_TRANSACTION_PROB:
            sender, receiver = random.sample(fraud_ring_ids, 2)
        elif is_fraud:
            sender, receiver = random.choice(fraud_ring_ids), random.randint(1, NUM_NORMAL_USERS)
        else:
            sender, receiver = random.sample(range(1, NUM_NORMAL_USERS + 1), 2)
        amount = round(random.uniform(500, 2000) if is_fraud else random.uniform(10, 500), 2)
        time = fake.date_time_between(start_date=start_date, end_date='now').isoformat()
        transactions.append((sender, receiver, amount, time))

    cursor.executemany("INSERT INTO transactions (sender_id, receiver_id, amount, transaction_time) VALUES (?, ?, ?, ?)", transactions)
    conn.commit()
    print("Data generation and loading complete.")

if __name__ == "__main__":
    connection = sqlite3.connect(DB_FILE, timeout=10)
    create_database_schema(connection)
    generate_and_load_data(connection)
    connection.close()
    print("\nData Generation Completed")
