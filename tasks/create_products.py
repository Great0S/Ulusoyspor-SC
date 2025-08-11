"""
Product Creation Tasks Module

This module handles the creation of products in the e-commerce platform (Ecwid)
from Telegram message data. It processes incoming product information, validates
content, translates text to multiple languages, and creates fully-featured 
product listings with comprehensive attributes and media.

Key Features:
- Telegram message parsing and validation
- Multi-language content generation (Arabic/English)
- Product attribute mapping and processing
- Media file handling and optimization
- E-commerce API integration
- Comprehensive error handling and logging

Dependencies:
    - requests: HTTP API calls to e-commerce platform
    - celery: Asynchronous task processing
    - Custom modules for specialized processing (categories, options, text)

Author: Ulusoyspor Team
Version: 1.0
"""

import json
import re

import requests

from config.settings import settings
from modules.category_filling import category_fill
from modules.category_processor import category_processor
from modules.options_processor import options_fill
from modules.text_processor import text_processor
from tasks.checks import clear_all
from app.celery_server import celery

# Initialize logging and translation services from settings
logger = settings.logger
arabic_translate = settings.arabic_translate


# Creates a product and assign the main product image
@celery.task()
def create_product(message, MCategory, categories, media_path):
    """
    Celery task to create a product in the e-commerce platform from Telegram data.

    This asynchronous task processes incoming Telegram messages containing product
    information and creates corresponding products in the Ecwid e-commerce platform.

    Processing Pipeline:
    1. Message validation and text processing
    2. Content extraction and validation
    3. Multi-language translation (Arabic ↔ English)
    4. Product attribute mapping and calculation
    5. Category assignment and SEO optimization
    6. API payload construction
    7. Product creation via Ecwid API
    8. Media cleanup and error handling

    Args:
        message (str): Raw Telegram message containing product information
                      Expected format: product details with size, price, etc.
        MCategory (str): Main product category for classification
        categories (dict): Category mapping data for proper assignment
        media_path (str): Path to temporary media files for cleanup

    Returns:
        None: Function handles all operations internally with comprehensive logging

    Raises:
        ValidationError: For invalid message format or content
        APIError: For e-commerce platform API failures
        TranslationError: For translation service failures

    Error Handling:
        - Invalid message length validation
        - Content filtering for inappropriate terms
        - API response validation and error logging
        - Automatic media cleanup on errors

    Side Effects:
        - Creates product in e-commerce platform
        - Logs all operations for monitoring
        - Cleans up temporary media files
        - Updates product categories if needed
    """
    global ResContent, Main, body, seoNameEn

    # Validate message exists and is processable
    if message:
        try:
            # Step 1: Process and clean the raw Telegram message text
            RefinedTxt = text_processor(message)

            # Step 2: Validate message content length for completeness
            if len(RefinedTxt) < 7:
                clear_all(media_path)  # Cleanup media files
                logger.error(
                    f"Invalid message length found | Length: {len(RefinedTxt)}"
                )
                return

            # Step 3: Extract product information from processed text
            # Product name in Arabic
            name = RefinedTxt[1].strip()
            nameEn = arabic_translate.translate(
                name)       # English translation
            # Clean translation artifacts
            nameEn = re.sub('a ', '', nameEn)
            nameEn = nameEn.capitalize()                    # Proper capitalization

            # Step 4: Content validation - filter inappropriate terms
            if re.search('السيري', name) or re.search('السيري', name):
                clear_all(media_path)
                logger.error('Invalid name found')
                return

            # Step 5: Extract and process size information
            size = RefinedTxt[2]
            size = re.sub('\D', '', size)  # Extract only numeric characters
            pcQty = RefinedTxt[3]
            pcQty = int(re.sub('\D', '', pcQty))
            price = RefinedTxt[4]
            price = float(re.sub('[^\d|^\d.\d]', '', price))
            pcPrice = RefinedTxt[5]
            pcPrice = int(re.sub('\D', '', pcPrice))
            sku = RefinedTxt[6]
            if re.search('-', sku):
                sku = sku.replace("كود الموديل", "")
                sku = sku.replace('-', '')
                sku = sku.split()
                sku = str(sku[1]) + '-' + str(sku[0])
            else:
                sku = re.sub('[^a-zA-Z\d\-]', '', sku)
            true = True
            false = False

            # Category values
            telegram_category = RefinedTxt[0].strip()
            if re.search('ماركه', telegram_category) or re.search('ماركة', telegram_category):
                clear_all(media_path)
                logger.warning(
                    f'Brand found with sku: {sku}')
                return
            main_category = ''
            category_names = set(categories['name'])
            main_category = category_processor(
                telegram_category, main_category, category_names)
            CatName = categories['name']
            CatId = categories['id']

            # Options values
            OpValues = [2, 3, 5]
            OpBody = []

            # Extract options from processed text
            options_fill(RefinedTxt, false, OpValues, OpBody)
            # Assigning categories using a for loop and a condition to match stored category list
            secName, Category, MainCategory, Cats = category_fill(
                main_category, CatName, CatId, MCategory)

            # Create a product request body
            if secName:
                if categories['name']:
                    for catNam in categories['name']:
                        if catNam == secName:
                            seoNameEn = categories['name'].index(catNam)
                            break
                seoNameEn = categories['nameEn'][seoNameEn] + ' / ' + nameEn
                seoName = secName + ' / ' + name
            else:
                seoName = name
                seoNameEn = nameEn
            body = {
                "sku": sku,
                "unlimited": true,
                "inStovalue": true,
                "name": nameEn,
                "nameTranslated": {
                    "ar": name,
                    "en": nameEn
                },
                "price": price,
                "enabled": true,
                "options": OpBody,
                "description": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish clothes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>",
                "descriptionTranslated": {
                    "ar": "<b>اختار/ي أفضل المنتجات من مئات الماركات الراقية التركية. نقدم لك/ي أكبر تشكيلة    من الملابس التركية واحدث الصيحات في الأزياء النسائية والرجالية والاطفال التي تناسب جميع الأذواق.   بمقاسات وألوان مختلفة.</b>",
                    "en": "<b>Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish clothes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colors.</b>"
                },
                "categoryIds": Category,
                "categories": Cats,
                "defaultCategoryId": MainCategory,
                "seoTitle": f'{seoNameEn}',
                "seoTitleTranslated": {
                    "ar": seoName,
                    "en": seoNameEn
                },
                "seoDescription": "Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish clothes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colours.",
                "seoDescriptionTranslated": {
                    "ar": "اختار/ي أفضل المنتجات من مئات الماركات الراقية التركية. نقدم لك/ي أكبر تشكيلة    من الملابس التركية واحدث الصيحات في الأزياء النسائية والرجالية والاطفال التي تناسب جميع الأذواق.   بمقاسات وألوان مختلفة.",
                    "en": "Choose the best products from hundreds of Turkish high-end brands. We offer you the largest selection of Turkish clothes and the latest trends in women's, men's and children's fashion that suit all tastes. In different sizes and colours."
                },
                "attributes": [{"name": "Note", "nameTranslated": {"ar": "ملاحظة", "en": "Note"},
                                "value": "The choice of colors is done at the start of processing the order.",
                                "valueTranslated": {
                    "ar": "اختيار الألوان يتم عند البدء بتجهيز الطلبية",
                          "en": "The choice of colors is done at the start of processing the order."
                }, "show":   "DESCR", "type": "UPC"}, {"name": "Brand", "nameTranslated": {"ar": "العلامة التجارية", "en": "Brand"},
                                                       "value": "Al Beyan Fashion™",
                                                       "valueTranslated": {
                    "ar": "Al Beyan Fashion™",
                    "en": "Al Beyan Fashion™"
                }, "show":   "DESCR", "type": "BRAND"}],
                "subtitle": "The displayed price is for the full set",
                "subtitleTranslated": {
                    "ar": "السعر المعروض للسيري كامل",
                    "en": "The displayed price is for the full set"
                }
            }

            # Parsing collected data
            ResContent, resCode = poster(body)
            # Feedback and returning response and media_path new values
            if resCode == 200:
                # Created product ID
                if 'id' in ResContent:
                    ItemId = ResContent['id']
                    logger.info(
                        f"Product created successfully with ID: {ItemId} | SKU: {sku}"
                    )
                    return ItemId
                else:
                    logger.error(
                        f"Product ID is empty?! | Response: {ResContent} | Sku: {sku}")
                    return ItemId

            elif resCode == 400:
                logger.error(
                    f"New product body request parameters are malformed | Sku: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                )
                clear_all(media_path)
                return None
            elif resCode == 409:
                logger.warning(
                    f"SKU_ALREADY_EXISTS: {sku} | Error Message: {ResContent['errorMessage']} | Error code: {ResContent['errorCode']}"
                )
                clear_all(media_path)
                return None
            else:
                logger.info(
                    f"Failed to create a new product")
                clear_all(media_path)
                return None

        # Errors handling
        except IndexError as e:
            logger.exception(e)
            return None

        except KeyError as e:
            logger.exception(e)
            return None

        except ValueError as e:
            logger.exception(e)
            return None


def poster(body):

    # Sending the POST request to create the products
    postData = json.dumps(body)
    response = requests.post(settings.products_url,
                             data=postData, headers=settings.ecwid_headers)
    resCode = int(response.status_code)
    response = json.loads(response.text.encode('utf-8'))
    logger.info("Body request has been sent")
    return response, resCode
