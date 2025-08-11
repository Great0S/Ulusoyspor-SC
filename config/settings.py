"""
Configuration Settings Module

This module centralizes all application configuration including:
- Logging configuration and setup
- Translation services for multilingual support
- Telegram API and bot configuration  
- E-commerce platform (Ecwid) API settings
- Database and message broker configuration
- Environment-specific settings (Development/Production/Test)

The settings are organized using Pydantic BaseSettings for:
- Type validation and conversion
- Environment variable loading
- Configuration management best practices

Dependencies:
    - pydantic: Settings management and validation
    - deep_translator: Google Translate API integration
    - logging: Application logging configuration

Author: Ulusoyspor Team
Version: 1.0
"""

from logging import config as Config
import logging
from deep_translator import GoogleTranslator
from pydantic import BaseSettings
from config.logger import log_config

# Global configuration and settings management


class Settings(BaseSettings):
    """
    Main settings class containing all application configuration.

    This class uses Pydantic BaseSettings to provide:
    - Automatic type validation
    - Environment variable loading
    - Default value management
    - Configuration documentation

    Configuration Categories:
        1. Logging: Application logging setup and file management
        2. Translation: Multi-language support services
        3. Telegram: Bot API configuration and channel settings
        4. E-commerce: Ecwid API endpoints and authentication
        5. Server: Application server and webhook configuration
        6. Database: PostgreSQL connection settings
    """

    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================

    # Apply logging configuration from external config file
    Config.dictConfig(log_config)
    logger = logging.getLogger('mainLog')  # Main application logger instance
    logs_dir: str = 'logs/'                # Directory for log file storage

    # ============================================================================
    # TRANSLATION SERVICES CONFIGURATION
    # ============================================================================
    # Google Translate API instances for multilingual support

    turk_translate = GoogleTranslator(
        source='tr', target='en')    # Turkish → English
    english_translate = GoogleTranslator(
        source='en', target='ar')  # English → Arabic
    arabic_translate = GoogleTranslator(
        source='ar', target='en')  # Arabic → English

    # ============================================================================
    # TELEGRAM API CONFIGURATION
    # ============================================================================
    # Telegram application and bot authentication settings

    api_id: int = 7148663                              # Telegram API application ID
    api_hash: str = '81c16de88cd5e25fcbf01e5af332b41f'  # Telegram API hash

    # ============================================================================
    # TELEGRAM BOT CONFIGURATION
    # ============================================================================
    # Bot credentials and communication settings

    username: str = 'albeyanfashion2'                           # Bot username
    # Associated phone number
    phone: int = 905434050709
    token: str = '5754073767:AAE3IbbE7-zXKGMg1fqunFxsUOg5K-kH6GI'  # Bot token
    channel_id: str = '@BeyanStorebot'                          # Main bot channel
    session_name: str = 'tele_bot'                              # Session identifier

    # ============================================================================
    # TELEGRAM CHANNELS CONFIGURATION
    # ============================================================================
    # Target channels for different product categories

    women_ids = [-1001411372097, -1001188747858, -1001147535835,
                 -1001237631051, -1001653408221]  # Women's product channels

    # ============================================================================
    # SERVER CONFIGURATION
    # ============================================================================
    # Application server and webhook settings

    Target: str = 'https://7e5e-213-254-138-110.eu.ngrok.io'  # Webhook target URL

    # ============================================================================
    # ECWID E-COMMERCE CONFIGURATION
    # ============================================================================
    # E-commerce platform API settings and endpoints

    category_id: int = 127443592  # Default category ID for new products

    # API endpoints for e-commerce operations
    products_url = "https://app.ecwid.com/api/v3/63690252/products"   # Products API
    category_url = "https://app.ecwid.com/api/v3/63690252/categories"  # Categories API
    ecwid_token = "?token=secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7"   # API token

    # Request configuration for Ecwid API calls
    payload = {}  # Default empty payload for GET requests
    ecwid_headers = {
        "Authorization": "Bearer secret_4i936SRqRp3317MZ51Aa4tVjeUVyGwW7",  # OAuth bearer token
        # JSON content type
        "Content-Type": 'application/json;charset: utf-8'
    }

    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================

    class Config:
        """
        Pydantic configuration for settings management.

        Settings:
            case_sensitive (bool): Enables case-sensitive field names for
                                  consistent configuration handling
        """
        case_sensitive = True


# ============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATION CLASSES
# ============================================================================

class BaseConfig():
    """
    Base configuration class with common settings for all environments.

    Provides fundamental configuration that applies across all deployment
    environments (Development, Production, Testing).

    Attributes:
        API_PREFIX (str): Base URL prefix for all API endpoints
        TESTING (bool): Testing mode flag for test-specific behavior
        DEBUG (bool): Debug mode flag for development features
    """
    API_PREFIX = '/api'    # Standard API route prefix
    TESTING = False        # Default: not in testing mode
    DEBUG = False          # Default: debug mode disabled


class DevConfig(BaseConfig):
    """
    Development environment configuration.

    Optimized for local development with:
    - Debug mode enabled for detailed error messages
    - Local database and message broker connections
    - Development-friendly logging and monitoring

    Database: PostgreSQL with development credentials
    Message Broker: RabbitMQ for async task processing
    """
    FLASK_ENV = 'development'
    DEBUG = True  # Enable debug mode for development

    # Development database connection
    SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/flask-deploy'

    # Development message broker configuration
    CELERY_BROKER = 'pyamqp://rabbit_user:rabbit_password@broker-rabbitmq//'
    CELERY_RESULT_BACKEND = 'rpc://rabbit_user:rabbit_password@broker-rabbitmq//'


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.

    Optimized for production deployment with:
    - Security-focused settings
    - Performance optimizations
    - Production-grade database and broker connections
    - Enhanced monitoring and logging

    Security Features:
    - Debug mode disabled
    - Secure database connections
    - Production message broker setup
    """
    FLASK_ENV = 'production'
    # Debug disabled for security in production

    # Production database connection (same as dev for this setup)
    SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/flask-deploy'

    # Production message broker configuration
    CELERY_BROKER = 'pyamqp://rabbit_user:rabbit_password@broker-rabbitmq//'
    CELERY_RESULT_BACKEND = 'rpc://rabbit_user:rabbit_password@broker-rabbitmq//'


class TestConfig(BaseConfig):
    """
    Testing environment configuration.

    Optimized for automated testing with:
    - Synchronous task execution for predictable testing
    - Debug mode enabled for test debugging
    - Testing-specific database and broker settings

    Testing Features:
    - CELERY_ALWAYS_EAGER: Forces synchronous task execution
    - TESTING flag: Enables test-specific application behavior
    - DEBUG mode: Provides detailed error information for test debugging
    """
    FLASK_ENV = 'development'
    TESTING = True    # Enable testing mode
    DEBUG = True      # Enable debug for test development

    # Force synchronous execution for predictable testing
    # Tasks execute immediately instead of being queued
    CELERY_ALWAYS_EAGER = True


# ============================================================================
# SETTINGS INSTANCE CREATION
# ============================================================================

# Create global settings instance for application-wide access
# This instance provides centralized configuration management
settings = Settings()
