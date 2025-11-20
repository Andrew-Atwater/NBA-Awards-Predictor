# basketballreference.com MVP Scraper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random


class MVPSeleniumScraper:
    
    BASE_URL = "https://www.basketball-reference.com"
    
    def __init__(self, start_year: int = 2000, end_year: int = 2025, headless: bool = False):
        self.start_year = start_year
        self.end_year = end_year
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def get_mvp_voting(self, year: int) -> pd.DataFrame:

        url = f"{self.BASE_URL}/awards/awards_{year}.html"
        print(f"Fetching MVP voting data for {year-1}-{str(year)[-2:]} season...")
        
        try:
            self.driver.get(url)
            
            # Wait for table to load
            wait = WebDriverWait(self.driver, 10)
            mvp_table = wait.until(
                EC.presence_of_element_located((By.ID, "mvp"))
            )
            
            tbody = mvp_table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            data = []
            
            for row in rows:
                try:
                    # Skip header rows
                    if "thead" in row.get_attribute("class") or "":
                        continue
                    
                    # Get player name
                    player_cell = row.find_element(By.CSS_SELECTOR, 'td[data-stat="player"]')
                    player_name = player_cell.text.strip()
                    
                    # Get points won
                    points_cell = row.find_element(By.CSS_SELECTOR, 'td[data-stat="points_won"]')
                    points_text = points_cell.text.strip()
                    
                    try:
                        points = float(points_text) if points_text else 0
                    except ValueError:
                        points = 0
                    
                    # Only include players with >100 points
                    if points > 100 and player_name:
                        data.append({
                            'Player': player_name,
                            'Points': points,
                            'Season': f"{year-1}-{str(year)[-2:]}",
                            'Year': year
                        })
                
                except NoSuchElementException:
                    continue
            
            df = pd.DataFrame(data)
            print(f"  Found {len(df)} MVP candidates with >100 points")
            return df
            
        except TimeoutException:
            print(f"  Timeout: MVP table not found for {year}")
            return pd.DataFrame()
        except Exception as e:
            print(f"  Error fetching {year}: {e}")
            return pd.DataFrame()
    
    def scrape_all_data(self) -> pd.DataFrame:

        print(f"\nStarting MVP voting data scrape from {self.start_year} to {self.end_year}")
        
        self.setup_driver()
        all_data = []
        
        try:
            for year in range(self.start_year, self.end_year + 1):
                mvp_df = self.get_mvp_voting(year)
                
                if mvp_df.empty:
                    print(f"  Skipping {year}, no data retrieved")
                else:
                    all_data.extend(mvp_df.to_dict('records'))
                
                # Random delay between requests
                delay = random.uniform(3, 7)
                time.sleep(delay)
            
        finally:
            print("\nClosing browser...")
            if self.driver:
                self.driver.quit()
        
        print("\n" + "=" * 60)
        print("Scraping complete")
        
        # Create final DataFrame
        df = pd.DataFrame(all_data)
        
        if not df.empty:
            print(f"\nTotal records collected: {len(df)}")
        else:
            print("\nNo data collected!")
        
        return df


def main():
    
    scraper = MVPSeleniumScraper(start_year=2000, end_year=2025, headless=False)
    
    df = scraper.scrape_all_data()
    
    if df.empty:
        print("\nNo data was scraped. Please check for errors above.")
        return
    
    # Save to CSV
    output_file = 'mvp_voting_results.csv'
    df.to_csv(output_file, index=False)
    print(f"\nData saved to {output_file}")
    
    # Display summary
    print("DATA SUMMARY")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head(10))
    
    print("Scraping completed successfully!")


if __name__ == "__main__":
    main()
