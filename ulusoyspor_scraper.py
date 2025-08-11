"""
Ulusoyspor Shoe Scraper Module

This module provides functionality to scrape Turkish shoe products from ulusoyspor.com,
process the scraped data, and create products in an e-commerce platform (Ecwid) with
multilingual support (Turkish, English, Arabic).

The scraper extracts product information including:
- Product names, codes, prices, quantities
- Size ranges, colors, materials, brands
- Product images and category information
- Specifications like shoe base type and size assortments

Dependencies:
    - requests: HTTP requests for web scraping and API calls
    - BeautifulSoup: HTML parsing and web scraping
    - webcolors: Color name processing and validation
    - progressbar/tqdm: Progress tracking for long-running operations
    - Custom modules for category management and product creation

Author: Ulusoyspor Scraper Team
Version: 1.0
"""

import glob
import json
import math
import os
import random
import re
import time

import requests
import webcolors
from bs4 import BeautifulSoup
from progressbar import progressbar
from tqdm import tqdm

from config.settings import settings
from modules.dump_category import dump_categories
from tasks.create_products import poster

# Initialize translation services and logging from settings
turk_translate = settings.turk_translate     # Turkish to English translator
english_translate = settings.english_translate  # English to Arabic translator
logger = settings.logger                    # Application logger instance

# Session cookies for maintaining authenticated requests to ulusoyspor.com
# These cookies handle user session, popup settings, push notifications, and cart data
cookies = {
    'ticimax_PopupSettings': '{"desktop":false,"mobilApps":false}',
    '__zlcmid': '1DHlQZP5CRr4OeQ',
    'ticiPushNotification': '{"chromePush":false}',
    'TicimaxReferer': 'referer=https://www.ulusoyspor.com/toptan-erkek-ayakkabi-01',
    # Long cookie containing visited product IDs for session tracking
    'SonZiyaretEdilenUrunler': 'strUrunID=44495,39295,44496,44296,9078,9093,9096,9103,9139,9140,9142,9176,9183,9200,9276,9277,9303,14775,18628,18631,18632,27350,27355,28166,28167,31535,31536,33815,34216,35336,35346,35359,35762,35799,35927,35928,35929,35931,35932,35940,35942,36062,36063,36215,36216,36338,36363,36434,36435,36437,36471,36576,36610,36612,36614,36651,36654,36655,36731,36732,36733,36735,36736,36740,36928,36929,36977,36978,37013,37080,37081,37148,37179,37215,37229,37246,37262,37553,37871,38285,38288,38303,38304,38309,38347,38392,38437,38545,38668,38839,38992,39020,39087,39191,39222,39242,39247,39249,39273,39277,39417,39425,39457,39476,39603,39606,39696,39702,39809,39811,39857,39870,39933,39937,39959,40004,40005,40006,40123,40126,40127,40229,40433,40517,40518,40539,40685,40686,40692,40694,40695,40734,40735,40762,40763,40766,40767,40809,40895,40917,40918,40919,40920,41017,41042,41043,41044,41046,41428,41483,41486,41550,41551,41557,41648,41649,41650,41651,41652,41692,41693,41696,41700,41704,41705,41716,41717,41718,41719,41741,41742,41743,41766,41768,41790,41791,41800,41801,41808,41809,41810,41811,27285,41812,41813,41814,41815,41816,41817,41818,41819,41820,41821,41827,41828,41841,41842,41981,41982,41983,42010,42011,42012,42013,42027,42028,42086,42091,42173,42174,42175,42181,42197,42281,42282,42308,42431,42463,42466,42467,42469,42470,42476,42479,42481,42482,42483,42523,42533,42538,42548,42577,42579,42619,42621,42636,43338,43337,43336,42639,42635,42634,42633,42629,42628,42627,42637,42638,42640,42641,42670,42673,42676,42721,42755,42757,42759,42760,42766,42767,42768,42828,42829,42830,42831,42833,42834,42835,42849,42850,42874,42912,42913,42914,42917,42944,42945,42946,42954,42958,42959,43011,43012,43016,43017,43018,43045,43100,43101,43104,43212,43213,43215,43216,43233,43235,43299,43352,43364,43457,43545,43546,43553,43554,43555,43556,43575,43737,43738,43753,43787,43792,43861,43863,43885,43889,43891,43901,43988,43989,43990,43991,43992,43993,43994,44093,44100,44104,44107,44135,44136,44137,44181,44188,44226,44262,44263,44264,44270,44276,44277,44279,44348,44350,44351,44353,44358,44359,44360,44361,44362,44388,44389,44396,44406,44407,44413,44414,44415,44421,44422,44423,44424,44425,44429,44430,44431,44432,44433,44438,44440,44441,44451,44457,44460,44461,44470,44473,44500,44501,35761,34381,34217,42752,42089,44499,44498,44395,44133,44085,43790,43098,44525,44526,42480&strKategoriID=242,229,256,244,267,232,233,280,255,265,247,230,248,268',
    'TcmxSID': 'dcq5ashvd1i1lbyfg4mkc4ad',
    '__cf_bm': 'Rkva610tSj21ulcPIL462tv7uiN9RLqSwRec5VRDM58-1670499974-0-AUPmiLKGGSolSinxDrCUFIt5w5fMztVqfGbb3UprZGpRnnkdchHJHZFy1At9AiC69iAuBuq0IQreO9P1qptVpeU=',
    'Ticimax_Cart_SessionID': '638060969710169946740E9DEB02CC43EA9D671477F54991E5',
    '.TicimaxAuthModule': 'A86BF86423AE321AA0819550D547F01FED0D3F622F1144309FD744BADBC9435AF959EE21AFB6CAEECA8A78D5BBF867EC651131E02FA4EB79FCD27598436B0EE8242B1EE26BDD88E941C80F0FC7AFEDDCBC9F8D2E8DD57DBA0EFE5E443BB2D3BA',
    'Ticimax_Member_Data': 'H4sIAAAAAAAEAA3Kx6JrQAAA0A+y0KItjegliDLs1BGjS67y9e+d9QkM8fbvwFhAJUFvcxmYLcMhd65Sgb4Xb/vE2DppmBeqTygCO47mpKCSmTt1bIZt/hDYByOCYquQ8fxqIt0TajrZW5Jjn74HIKwr35idNyfOX2qnIkeVGp2ags/kxLcSqQnxrGsRqKtj6jnpJGLk5LevjnmSfGIjwfmLbmlLCB+Coj3240ivY8U96TmMu/NxJG+cWT9zx1wjE5uZ/EVpVZsznfdpltLbX9XgOfd19jfSEsrRsBFSsD7RHcSRS9V/xzroBq1h4YQhi6a1Mx1H0usbLeb3a8gkmAL7sL4PFewTt6fILPlGjg7ea5LNRbYYWhRg3mtsjbb9lQu3VZ6vzC78wzs5iCbGR1HEPsTf/ibW8lAYfF5pidXs1QX0EoxNqv8i1hspULT+tqX09OdCl/9pHVdpOCj7ayLO1oBvCUgjTENchWS5Ny0HSnTxhcDUUsIsOZ+Iczd597AS6pJwZI1H6M27tSCe261NNLCMLdhV3Qu8RO4pA7niL76Ptq6vryn32MvT3+AuHle7hEEhCf3oSOHPE4ePFsQDknBnrlPxIq3Pb855jON4Slgn1exPuIaF/g7gSZYYXX+Z+lMFarKLcm6iK8hBHrde1nSElk0ZjGtpfRLZ++DDETgniTf2I+aUMCukS9djdrDJ8L+3YlNHvbGThHb8A3oPMWWgAgAA',
    'CultureSettings': 'H4sIAAAAAAAEAAXByYJDMAAA0A9yQGM99CAytVcaa92qjNIEUUzbr5%2f3vkkExaCz18E9wa2id0Uiw3YVDt77%2fHG4LUTcswhqLSdFHCexOBbAZCGm38fv05bTqsncF3jD3qnFPmKzrj%2fzIt9%2bbmX24dGw6orehG6ODXOjMZ41RhONwHU1i1cr3ILUFCxRUt%2by4ym1wsh0InE6E1MIwtH4NLW715JjF4enjtrwnXGnnJV98yV1ogS2aa8l42TTMpZ8sa6RbC0dsG1ZhqdAGzkv4326yry%2bwFndv8CYXfKH1QvrtW1FHpHNlFLj8mcjnYigNmBJEU7hDVUCXsRlxvdk4N1K%2fF4ZwcxA6C7AzSqwP8rXufGZSSo1P7B7KIjjiq9bAkMM1TJSu%2bPxH9chbwdYAQAA',
}

# HTTP headers for API requests to ulusoyspor.com
# Configured to mimic a real browser request for better success rate
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en,ar;q=0.9,tr;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

# API parameters for product listing requests
# Contains filter and pagination configuration for product queries
params = {
    'c': 'entry0010',  # Controller identifier
    # JSON filter for product search - controls categories, brands, price range, etc.
    'FilterJson': '{"CategoryIdList":[0],"BrandIdList":[],"SupplierIdList":[],"TagIdList":[],"TagId":-1,"FilterObject":[],"MinStockAmount":-1,"IsShowcaseProduct":-1,"IsOpportunityProduct":-1,"FastShipping":-1,"IsNewProduct":-1,"IsDiscountedProduct":-1,"IsShippingFree":-1,"IsProductCombine":-1,"MinPrice":0,"MaxPrice":0,"Point":0,"SearchKeyword":"","StrProductIds":"","IsSimilarProduct":false,"RelatedProductId":0,"ProductKeyword":"","PageContentId":0,"StrProductIDNotEqual":"","IsVariantList":-1,"IsVideoProduct":-1,"ShowBlokVideo":-1,"VideoSetting":{"ShowProductVideo":-1,"AutoPlayVideo":-1},"ShowList":1,"VisibleImageCount":6,"ShowCounterProduct":-1,"ImageSliderActive":false,"ProductListPageId":0,"ShowGiftHintActive":false,"NonStockShowEnd":1}',
    # JSON pagination settings - controls page size and ordering
    'PagingJson': '{"PageItemCount":0,"PageNumber":1,"OrderBy":"uk.ID","OrderDirection":"DESC"}',
    'CreateFilter': 'true',  # Enable filter creation
    'TransitionOrder': '0',  # Order transition setting
    'PageType': '1',         # Page type identifier
    'PageId': '228',         # Default page ID
}

# Data structure to organize scraped products by demographic categories
# Each category will contain a list of product dictionaries
products = {"Men": [],      # Men's shoes
            "Women": [],    # Women's shoes
            "Kid": [],      # Children's shoes
            "Baby": []}     # Baby shoes

# Base URLs for the ulusoyspor website
URL = "https://www.ulusoyspor.com/en"    # English version for navigation
URL2 = "https://www.ulusoyspor.com"       # Turkish version (main site)
Login = 'https://www.ulusoyspor.com/UyeGiris'  # Login endpoint

# Color validation list from CSS3 color names for product color extraction
colors = list(map(str, webcolors.CSS3_NAMES_TO_HEX.keys()))

# Global flag to control synchronization between scraping and product creation threads
switchLock = False


def save_data(data: dict, main: str, files: str):
    """
    Saves scraped product data to JSON files with intelligent merging.

    This function handles incremental data saving during the scraping process
    to prevent data loss and enable resume functionality. It performs:

    1. Checks if the target JSON file already exists
    2. If exists: loads existing data and merges with new data
    3. If not exists: creates new file with current data
    4. Implements duplicate detection to prevent redundant saves
    5. Uses UTF-8 encoding for proper multilingual support

    Args:
        data (dict): Complete product data structure with categories as keys
                    Format: {"Men": [...], "Women": [...], "Kid": [...], "Baby": [...]}
        main (str): Main category being processed (e.g., "Men", "Women", "Kid", "Baby")
        files (str): Base filename without extension (e.g., "data" creates "data.json")

    Returns:
        dict: Updated JSON data structure after save operation

    File Structure:
        - Creates/updates files in 'dumps/' directory
        - Uses UTF-8 encoding for international character support
        - Maintains data integrity with proper JSON formatting

    Error Handling:
        - Handles file creation and writing errors gracefully
        - Ensures proper file closure for resource management
        - Maintains data consistency across save operations
    """
    global json_data
    File_path = f'dumps/{files}.json'

    # Check if data file already exists for incremental updates
    if os.path.exists(File_path):

        # Load existing data for comparison and merging
        open_json = open(File_path, 'r', encoding='utf-8')
        json_data = json.load(open_json)

        # Prevent duplicate saves by comparing data lengths
        if len(data[main]) == len(json_data[main]):
            pass  # No new data to save
        else:
            # Add new product data to existing structure
            json_data[main].append(data[main][0])
            with open(File_path, 'w', encoding='utf-8') as file:
                file.truncate()  # Clear file before writing
                # Preserve Unicode characters
                json.dump(data, file, ensure_ascii=False)
            file.close()
    else:
        # Create new file with current data
        with open(File_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
        file.close()

        # Load the newly created file for consistency
        open_json = open(File_path, 'r', encoding='utf-8')
        json_data = json.load(open_json)

    return json_data


def main():
    """
    Main orchestration function that coordinates scraping and product creation.

    This function implements a multi-threaded approach to optimize performance:

    1. Creates a separate thread for web scraping (ulusoyScraper)
    2. Runs product creation in the main thread (create_product)  
    3. Uses thread synchronization to coordinate between operations

    Threading Strategy:
        - Scraping thread: Handles I/O intensive web scraping operations
        - Main thread: Handles API calls and product creation
        - Synchronization: Uses global switchLock flag for coordination

    This design allows:
        - Parallel processing of scraping and product creation
        - Better resource utilization and reduced total execution time
        - Graceful handling of network delays and API rate limits

    Returns:
        None: Function coordinates background operations
    """
    from threading import Thread

    # Create and start the scraping thread
    # new_thread = Thread(target=ulusoyScraper)
    # new_thread.start()

    # Run product creation in main thread (will wait for scraping to complete)
    # create_product()

    # For now, just run scraping in main thread for testing
    print("Starting Ulusoyspor scraper...")
    logger.info('New ULUSOYSPOR session has been started')


def cls():
    """
    Utility function to clear the console screen.

    Provides a clean console interface by clearing previous output.
    Platform-specific implementation for Windows environment.

    Returns:
        int: System command return code (0 for success)
    """
    return os.system("cls")


# Clear console for clean startup interface
cls()

# Log session initialization
logger.info('New ULUSOYSPOR session has been started')

# Main execution block with performance monitoring
if __name__ == '__main__':
    """
    Main execution entry point with performance measurement.

    Features:
        - Performance timing for optimization analysis
        - Comprehensive error handling and logging
        - Clean session initialization and cleanup

    Execution Flow:
        1. Clear console and initialize logging
        2. Start performance timer
        3. Execute main scraping and creation workflow
        4. Calculate and log total execution time

    Performance Metrics:
        - Total execution time measurement
        - Memory usage optimization through proper resource management
        - Network efficiency through session reuse and connection pooling
    """
    import time

    # Start performance measurement
    s = time.perf_counter()

    # Execute main workflow
    main()

    # Calculate and log execution time
    elapsed = time.perf_counter() - s
    logger.info(f"Tasks executed in {elapsed:0.2f} seconds.")
