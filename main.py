import logging
from datetime import datetime
import time
# Import the absolute path from config
from config import TICKERS, EXCEL_FILE, LOG_FILE 
from nse_fetcher import fetch_nse_data
from excel_writer import write_to_excel

# Setup logging using the ABSOLUTE path
logging.basicConfig(
    filename=LOG_FILE,  # <--- FIXED: Uses absolute path now
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def main():
    """Main function to fetch and save NSE data"""
    logging.info("="*50)
    logging.info("Starting NSE data fetch cycle")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        logging.info(f"Fetching data for {len(TICKERS)} stocks...")
        
        # Fetch Data + Market Trend
        data, is_bearish = fetch_nse_data(TICKERS, timestamp)
        
        if data.empty:
            logging.error("No data fetched. Aborting this cycle.")
            return

        logging.info(f"Writing {len(data)} records to Excel...")
        
        # Write to Excel (Passing Trend)
        write_to_excel(data, EXCEL_FILE, is_bearish)
        
        logging.info(f"Successfully saved {len(data)} stock records")
        
    except Exception as e:
        logging.error(f"Critical error in main cycle: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()