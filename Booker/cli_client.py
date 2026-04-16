#!/usr/bin/env python3
# cli_client.py - Simple CLI client for Literary Multi-Agent System

import requests
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 60


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("=" * 70)
    print("  LITERARY MULTI-AGENT SYSTEM - Booker Client")
    print("=" * 70)
    print()


def print_section(title):
    print(f"\n{'-' * 50}")
    print(f"[ {title} ]")
    print(f"{'-' * 50}")


def fetch_book_full(author, title, language="en"):
    """Запрос к API Booker для получения полного текста"""
    print(f"\n[INFO] Searching for '{title}' by '{author}'...")
    print(f"       Language: {language}")
    print("       (First request may take 5-10 seconds)\n")
    
    start_time = time.time()
    
    try:
        # ИСПОЛЬЗУЕМ /fetch_full ВМЕСТО /fetch
        response = requests.post(
            f"{BASE_URL}/fetch_full",
            json={"title": title, "author": author, "language": language},
            timeout=TIMEOUT
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            return {"success": True, "data": response.json(), "elapsed": elapsed}
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", {}), "elapsed": elapsed}
    
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": {"message": f"Cannot connect to {BASE_URL}"}, "elapsed": 0}
    except requests.exceptions.Timeout:
        return {"success": False, "error": {"message": f"Timeout ({TIMEOUT} seconds)"}, "elapsed": TIMEOUT}
    except Exception as e:
        return {"success": False, "error": {"message": str(e)}, "elapsed": 0}


def display_book_info(data):
    print_section("BOOK INFORMATION")
    print(f"\n  Title: {data.get('title', 'N/A')}")
    print(f"  Author: {data.get('author', 'N/A')}")
    print(f"  Language: {data.get('language', 'N/A')}")
    print(f"  Word count: {data.get('word_count', 0):,}")
    print(f"  Source: {data.get('source', 'N/A')}")
    print(f"  From cache: {'Yes' if data.get('cached') else 'No'}")
    print(f"  Processing time: {data.get('processing_time_ms', 0)} ms")


def display_text_preview(data):
    """Показать превью текста"""
    full_text = data.get('text', '')
    
    if not full_text:
        print("\n  [WARNING] Text not available")
        return
    
    print_section("TEXT PREVIEW (first 1000 characters)")
    print(f"\n{full_text[:1000]}")
    
    if len(full_text) > 1000:
        print("\n... (text continues)")
    
    print(f"\n  Total text size: {len(full_text):,} characters")


def save_full_text(data):
    """Сохранить полный текст в файл"""
    full_text = data.get('text', '')
    
    if not full_text:
        print("\n  [WARNING] Text not available")
        return
    
    safe_title = data.get('title', 'book').replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_author = data.get('author', 'unknown').replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"{safe_title}_{safe_author}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {data.get('title')}\n")
        f.write(f"Author: {data.get('author')}\n")
        f.write(f"Source: {data.get('source')}\n")
        f.write(f"Download date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        f.write(full_text)
    
    print(f"\n  [OK] Text saved to: {filename}")
    return filename


def save_full_report(data, author, title):
    """Сохранить полный отчёт с метаданными и текстом"""
    safe_author = author.replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_title = title.replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"report_{safe_author}_{safe_title}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("LITERARY ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Title: {data.get('title')}\n")
        f.write(f"Author: {data.get('author')}\n")
        f.write(f"Language: {data.get('language')}\n")
        f.write(f"Word count: {data.get('word_count', 0):,}\n")
        f.write(f"Source: {data.get('source')}\n")
        f.write(f"From cache: {data.get('cached', False)}\n")
        f.write(f"Processing time: {data.get('processing_time_ms', 0)} ms\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("FULL TEXT\n")
        f.write("=" * 70 + "\n\n")
        f.write(data.get('text', 'Text not available'))
    
    return filename


def main():
    clear_screen()
    print_header()
    
    while True:
        print("\n" + "=" * 50)
        print("  ENTER SEARCH DATA")
        print("=" * 50)
        
        import sys
        
        sys.stdout.write("Author: ")
        sys.stdout.flush()
        author = sys.stdin.readline().strip()
        
        while not author:
            sys.stdout.write("Author (cannot be empty): ")
            sys.stdout.flush()
            author = sys.stdin.readline().strip()
        
        sys.stdout.write("Title: ")
        sys.stdout.flush()
        title = sys.stdin.readline().strip()
        
        while not title:
            sys.stdout.write("Title (cannot be empty): ")
            sys.stdout.flush()
            title = sys.stdin.readline().strip()
        
        # Выбор языка
        print("\nLanguage options:")
        print("  1. English (recommended)")
        print("  2. Russian")
        sys.stdout.write("Choose (1-2) [default: 1]: ")
        sys.stdout.flush()
        lang_choice = sys.stdin.readline().strip()
        
        language = "ru" if lang_choice == "2" else "en"
        
        # Ищем книгу (с полным текстом)
        result = fetch_book_full(author, title, language)
        
        if not result["success"]:
            print("\n" + "=" * 50)
            print("  [ERROR] BOOK NOT FOUND")
            print("=" * 50)
            print(f"\n  Reason: {result['error'].get('message', 'Unknown error')}")
            
            if 'attempted_sources' in result.get('error', {}):
                print(f"  Sources checked: {', '.join(result['error']['attempted_sources'])}")
            
            print("\n  Tips:")
            print("     1. Check spelling of title and author")
            print("     2. Try English title (for Russian classics)")
            print("     3. Example: Author 'Tolstoy', Title 'War and Peace'")
        else:
            data = result["data"]
            elapsed = result["elapsed"]
            
            clear_screen()
            print_header()
            
            print(f"\n[SUCCESS] Book loaded! ({elapsed:.2f} sec)")
            
            display_book_info(data)
            
            # Показываем превью текста
            display_text_preview(data)
            
            # Сохраняем отчёт
            sys.stdout.write("\n  Save full report to file? (y/n): ")
            sys.stdout.flush()
            save_report = sys.stdin.readline().strip().lower()
            
            if save_report == 'y':
                filename = save_full_report(data, author, title)
                print(f"\n  [OK] Report saved to: {filename}")
            
            # Сохраняем только текст
            sys.stdout.write("\n  Save only text to file? (y/n): ")
            sys.stdout.flush()
            save_text = sys.stdin.readline().strip().lower()
            
            if save_text == 'y':
                filename = save_full_text(data)
                print(f"\n  [OK] Text saved to: {filename}")
        
        # Повторный поиск
        print("\n" + "=" * 50)
        sys.stdout.write("\n  Search another book? (y/n): ")
        sys.stdout.flush()
        again = sys.stdin.readline().strip().lower()
        
        if again != 'y':
            print("\n[INFO] Thank you for using Literary Multi-Agent System!")
            print("       Goodbye!\n")
            break
        
        clear_screen()
        print_header()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")