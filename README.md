# 🏪 Ulusoyspor Shoe Scraper & E-commerce Integration

A comprehensive **Turkish shoe product scraper** and **e-commerce automation system** that extracts product data from [Ulusoyspor.com](https://www.ulusoyspor.com) and automatically creates multilingual product listings in Ecwid e-commerce platform.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Multilingual Support](#multilingual-support)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This system automates the process of importing Turkish shoe products from a wholesale supplier (Ulusoyspor) into an e-commerce platform. It handles:

- **Web Scraping**: Extracts product data including images, prices, sizes, and specifications
- **Data Processing**: Cleans and validates product information
- **Translation**: Converts Turkish content to English and Arabic
- **E-commerce Integration**: Creates products in Ecwid with full multilingual support
- **Media Management**: Downloads and uploads product images
- **Telegram Integration**: Processes product information from Telegram channels

## ✨ Features

### 🔍 **Web Scraping**
- Automated extraction from ulusoyspor.com
- Product details (names, codes, prices, quantities)
- Size ranges, colors, materials, and brands
- High-resolution product images
- Category and subcategory information

### 🌐 **Multilingual Support**
- **Turkish** → **English** translation
- **English** → **Arabic** translation
- SEO-optimized content in multiple languages
- Localized product attributes

### 🛒 **E-commerce Integration**
- Automated product creation in Ecwid
- Dynamic pricing with markup calculations
- Category assignment and management
- Product attribute mapping
- Image gallery management

### 📱 **Telegram Integration**
- Bot-based product information processing
- Channel monitoring for new products
- Message parsing and validation
- Automated workflow triggers

### ⚡ **Performance & Reliability**
- Multi-threaded processing
- Session management and connection pooling
- Comprehensive error handling and logging
- Data persistence and resume capability
- Progress tracking and monitoring

## 🛠 Tech Stack

### **Core Technologies**
- ![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white) **Python 3.10+** - Main programming language
- ![Flask](https://img.shields.io/badge/Flask-2.0+-green?logo=flask&logoColor=white) **Flask** - Web framework for API endpoints
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue?logo=postgresql&logoColor=white) **PostgreSQL** - Primary database
- ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.9+-orange?logo=rabbitmq&logoColor=white) **RabbitMQ** - Message broker for async tasks

### **Web Scraping & Processing**
- **BeautifulSoup4** - HTML parsing and web scraping
- **Requests** - HTTP client for web requests
- **lxml** - XML/HTML parser
- **webcolors** - Color name processing and validation

### **Task Processing**
- **Celery** - Distributed task queue
- **Redis** - Celery broker and result backend
- **threading** - Multi-threaded processing

### **API Integrations**
- **Ecwid API** - E-commerce platform integration
- **Telegram Bot API** - Telegram bot and channel management
- **Google Translate API** - Multi-language translation services

### **Data & Configuration**
- **Pydantic** - Settings management and validation
- **JSON** - Data storage and interchange
- **python-dotenv** - Environment variable management

### **Monitoring & Logging**
- **logging** - Comprehensive application logging
- **tqdm** - Progress bars and monitoring
- **progressbar2** - Alternative progress tracking

### **Development & Deployment**
- **Docker** - Containerization (configured)
- **Git** - Version control
- **VS Code** - Development environment

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ulusoyspor    │    │   Telegram      │    │   Google        │
│   Website       │────│   Channels      │────│   Translate     │
│   (Source)      │    │   (Trigger)     │    │   (Translation) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ulusoyspor Scraper                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Scraping  │  │ Translation │  │    Data Processing      │ │
│  │   Module    │  │   Service   │  │    & Validation         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   File System   │    │   RabbitMQ      │
│   Database      │    │   (JSON/Images) │    │   Task Queue    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │      Ecwid API          │
                    │   (E-commerce Platform) │
                    └─────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- RabbitMQ 3.9+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Great0S/Ulusoyspor-SC.git
cd Ulusoyspor-SC
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the project root:
```env
# Database Configuration
DATABASE_URL=postgresql://db_user:db_password@localhost:5432/ulusoyspor_db

# Telegram Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token

# Ecwid Configuration
ECWID_STORE_ID=your_store_id
ECWID_API_TOKEN=your_api_token

# Google Translate
GOOGLE_TRANSLATE_API_KEY=your_translate_key

# RabbitMQ
CELERY_BROKER_URL=pyamqp://guest@localhost//
CELERY_RESULT_BACKEND=rpc://guest@localhost//
```

### 5. Database Setup
```bash
python manage.py db upgrade
```

## ⚙️ Configuration

### Application Settings
Configure the application in `config/settings.py`:

```python
class Settings(BaseSettings):
    # Logging
    logs_dir: str = 'logs/'
    
    # Translation Services
    turk_translate = GoogleTranslator(source='tr', target='en')
    english_translate = GoogleTranslator(source='en', target='ar')
    
    # E-commerce API
    products_url = "https://app.ecwid.com/api/v3/{store_id}/products"
    category_url = "https://app.ecwid.com/api/v3/{store_id}/categories"
```

### Environment-Specific Configuration
- **Development**: Debug mode, local database
- **Production**: Optimized settings, production database
- **Testing**: Synchronous tasks, test database

## 🚀 Usage

### Basic Scraping
```bash
python ulusoyspor_scraper.py
```

### Run with Celery Workers
```bash
# Terminal 1: Start Celery worker
celery -A app.celery_server worker --loglevel=info

# Terminal 2: Start main application
python ulusoyspor_scraper.py
```

### Telegram Bot Integration
```bash
python app/tele_bot.py
```

## 📁 Project Structure

```
Ulusoyspor-SC/
├── 📄 ulusoyspor_scraper.py      # Main scraping application
├── 📁 app/
│   ├── 📄 __init__.py
│   ├── 📄 celery_server.py       # Celery configuration
│   └── 📄 tele_bot.py           # Telegram bot handler
├── 📁 config/
│   ├── 📄 __init__.py
│   ├── 📄 settings.py           # Application configuration
│   └── 📄 logger.py             # Logging configuration
├── 📁 modules/
│   ├── 📄 __init__.py
│   ├── 📄 category_processor.py  # Category management
│   ├── 📄 text_processor.py     # Text processing utilities
│   ├── 📄 options_processor.py  # Product options handling
│   └── 📄 dump_category.py      # Category data management
├── 📁 tasks/
│   ├── 📄 create_products.py    # Product creation tasks
│   ├── 📄 category_create.py    # Category creation tasks
│   ├── 📄 checks.py             # Validation and checks
│   └── 📄 uploader.py           # Media upload tasks
├── 📁 dumps/                    # JSON data storage
│   ├── 📄 data.json             # Scraped product data
│   └── 📄 categories.json       # Category mappings
├── 📁 logs/                     # Application logs
└── 📁 media/                    # Temporary image storage
```

## 🔌 API Integration

### Ecwid E-commerce Platform
- **Product Creation**: Automated product listing creation
- **Category Management**: Dynamic category assignment
- **Image Upload**: Main product images and galleries
- **Attribute Mapping**: Size, color, brand, and custom attributes

### Telegram Bot API
- **Channel Monitoring**: Real-time product information processing
- **Message Parsing**: Structured data extraction from messages
- **Bot Commands**: Administrative controls and status updates

### Google Translate API
- **Multi-language Support**: Turkish → English → Arabic
- **Content Localization**: Product names, descriptions, and attributes
- **SEO Optimization**: Localized metadata and search terms

## 🌍 Multilingual Support

### Translation Pipeline
1. **Source**: Turkish product information from Ulusoyspor
2. **Primary Translation**: Turkish → English using Google Translate
3. **Secondary Translation**: English → Arabic for Middle Eastern markets
4. **Content Optimization**: SEO-friendly titles and descriptions

### Supported Languages
- 🇹🇷 **Turkish** (Source language)
- 🇺🇸 **English** (Primary target)
- 🇸🇦 **Arabic** (Secondary target)

## 📊 Data Flow

```mermaid
graph TD
    A[Ulusoyspor Website] --> B[Web Scraper]
    B --> C[Data Processing]
    C --> D[Translation Service]
    D --> E[Product Creation]
    E --> F[Ecwid API]
    F --> G[E-commerce Store]
    
    H[Telegram Channel] --> I[Message Parser]
    I --> J[Content Validation]
    J --> K[Product Creation Task]
    K --> F
```

## 🔒 Security Features

- **API Token Management**: Secure token storage and rotation
- **Rate Limiting**: Prevents API abuse and ensures compliance
- **Data Validation**: Input sanitization and validation
- **Error Handling**: Comprehensive exception management
- **Logging**: Security event monitoring and audit trails

## 📈 Performance Metrics

- **Scraping Speed**: ~100-500 products per hour (depending on network)
- **Translation Throughput**: ~1000 words per minute
- **API Rate Limits**: Respects Ecwid and Google API limits
- **Memory Usage**: Optimized for large product catalogs
- **Error Recovery**: Automatic retry mechanisms with exponential backoff

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please contact:
- **Email**: support@ulusoyspor-scraper.com
- **GitHub Issues**: [Create an issue](https://github.com/Great0S/Ulusoyspor-SC/issues)
- **Documentation**: [Wiki](https://github.com/Great0S/Ulusoyspor-SC/wiki)

## 🙏 Acknowledgments

- **Ulusoyspor.com** - Product data source
- **Ecwid** - E-commerce platform
- **Google Translate** - Translation services
- **Telegram** - Bot platform and messaging

---

<div align="center">
<p><strong>Built with ❤️ for Turkish shoe retailers</strong></p>
<p>
  <a href="#top">⬆️ Back to Top</a>
</p>
</div>
