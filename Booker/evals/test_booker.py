# import requests
# import json
# import time

# BASE_URL = "http://localhost:8000"

# def test_health():
#     print("=" * 50)
#     print("1. Тест health check")
#     response = requests.get(f"{BASE_URL}/health")
#     print(f"Status: {response.status_code}")
#     print(f"Response: {response.json()}")
#     print()

# def test_fetch_english():
#     print("=" * 50)
#     print("2. Тест загрузки английской книги (Frankenstein)")
#     start = time.time()
#     response = requests.post(
#         f"{BASE_URL}/fetch",
#         json={"title": "Frankenstein", "author": "Shelley"}
#     )
#     elapsed = time.time() - start
#     print(f"Status: {response.status_code}")
#     if response.status_code == 200:
#         data = response.json()
#         print(f"Title: {data.get('title')}")
#         print(f"Author: {data.get('author')}")
#         print(f"Language: {data.get('language')}")
#         print(f"Word count: {data.get('word_count')}")
#         print(f"Chapters: {data.get('chapters_count')}")
#         print(f"Source: {data.get('source')}")
#         print(f"Cached: {data.get('cached')}")
#         print(f"Time: {elapsed:.2f} sec")
#     print()

# def test_fetch_russian():
#     print("=" * 50)
#     print("3. Тест загрузки русской книги (Преступление и наказание)")
#     start = time.time()
#     response = requests.post(
#         f"{BASE_URL}/fetch",
#         json={"title": "Преступление и наказание", "author": "Достоевский"}
#     )
#     elapsed = time.time() - start
#     print(f"Status: {response.status_code}")
#     if response.status_code == 200:
#         data = response.json()
#         print(f"Title: {data.get('title')}")
#         print(f"Author: {data.get('author')}")
#         print(f"Language: {data.get('language')}")
#         print(f"Word count: {data.get('word_count')}")
#         print(f"Chapters: {data.get('chapters_count')}")
#         print(f"Source: {data.get('source')}")
#         print(f"Cached: {data.get('cached')}")
#         print(f"Time: {elapsed:.2f} sec")
#     print()

# def test_cache():
#     print("=" * 50)
#     print("4. Тест кеширования (повторный запрос Frankenstein)")
    
#     # Первый запрос
#     start = time.time()
#     response1 = requests.post(
#         f"{BASE_URL}/fetch",
#         json={"title": "Frankenstein", "author": "Shelley"}
#     )
#     time1 = time.time() - start
#     cached1 = response1.json().get('cached', False)
    
#     # Второй запрос
#     start = time.time()
#     response2 = requests.post(
#         f"{BASE_URL}/fetch",
#         json={"title": "Frankenstein", "author": "Shelley"}
#     )
#     time2 = time.time() - start
#     cached2 = response2.json().get('cached', False)
    
#     print(f"Первый запрос: {time1:.2f} сек, cached={cached1}")
#     print(f"Второй запрос: {time2:.2f} сек, cached={cached2}")
    
#     if cached2 and time2 < time1:
#         print("✅ Кеш работает!")
#     else:
#         print("⚠️ Кеш не работает или время не уменьшилось")
#     print()

# def test_not_found():
#     print("=" * 50)
#     print("5. Тест ненайденной книги")
#     response = requests.post(
#         f"{BASE_URL}/fetch",
#         json={"title": "NonexistentBook12345"}
#     )
#     print(f"Status: {response.status_code}")
#     if response.status_code == 404:
#         print("✅ Ошибка 404 получена корректно")
#         print(f"Message: {response.json().get('detail', {}).get('message')}")
#     print()

# if __name__ == "__main__":
#     print("\n🧪 Запуск тестов Booker Agent\n")
    
#     try:
#         test_health()
#         test_fetch_english()
#         test_fetch_russian()
#         test_cache()
#         test_not_found()
#         print("\n✅ Все тесты завершены!")
#     except requests.exceptions.ConnectionError:
#         print("\n❌ Ошибка: Не удалось подключиться к Booker API")
#         print("Убедитесь, что контейнер запущен: docker-compose up")
#     except Exception as e:
#         print(f"\n❌ Ошибка: {e}")


import requests

# Поиск русских книг через Gutendex
response = requests.get("https://gutendex.com/books/?languages=ru&page=1")
data = response.json()

print(f"Найдено русских книг: {data.get('count', 0)}")
print("\nПримеры:")
for book in data.get("results", [])[:5]:
    print(f"- {book.get('title')} (ID: {book.get('id')})")