# evals/test_russian.py

import requests
import json
import sys

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"

# Список русских книг с английскими названиями для поиска
russian_books_en = [
    ("War and Peace", "Tolstoy"),
    ("Anna Karenina", "Tolstoy"),
    ("Crime and Punishment", "Dostoevsky"),
    ("The Brothers Karamazov", "Dostoevsky"),
    ("Eugene Onegin", "Pushkin"),
    ("Dead Souls", "Gogol"),
    ("Fathers and Sons", "Turgenev"),
]

print("=" * 60)
print("Testing Russian classics via English titles")
print("=" * 60)
print()

for title, author in russian_books_en:
    try:
        print(f"[TESTING] {title} by {author}...")
        
        response = requests.post(
            f"{BASE_URL}/fetch",
            json={"title": title, "author": author, "language": "en"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] {title} - {data.get('word_count', 0):,} words, source: {data.get('source')}")
        else:
            error_data = response.json()
            error_msg = error_data.get('detail', {}).get('message', 'Unknown error')
            print(f"[FAILED] {title} - {error_msg}")
    
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to Booker API at {BASE_URL}")
        print("Make sure the container is running: docker-compose up")
        break
    except Exception as e:
        print(f"[ERROR] {title} - {str(e)}")
    
    print()

print("=" * 60)
print("Done!")