"""
Fast scraper for Equipauto exhibitor list - optimized version
"""
import time
import logging
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from scraper import WebScraper
from colorama import Fore
import config

logger = logging.getLogger(__name__)


class EquipautoScraperFast(WebScraper):
    """Fast scraper for Equipauto website"""

    def scrape_equipauto(self, language='fr'):
        """
        Scrape Equipauto exhibitor list - fast version

        Args:
            language: Language code (fr or en)
        """
        all_exhibitors = []

        try:
            if not self.driver:
                self.setup_driver()

            # Navigate to main page
            main_url = 'https://paris.equipauto.com/liste-des-exposants/'
            logger.info(f"{Fore.CYAN}Loading main page: {main_url}")
            self.driver.get(main_url)
            time.sleep(3)

            # Accept cookies if present
            logger.info(f"{Fore.YELLOW}Looking for cookie consent...")
            try:
                # Use JavaScript to find and click any button with "accept" text
                self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button, a');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].textContent.toLowerCase();
                        if (text.includes('accept') || text.includes('accepter') || text.includes('agree')) {
                            buttons[i].click();
                            break;
                        }
                    }
                """)
                logger.info(f"{Fore.GREEN}Attempted to click cookie consent")
                time.sleep(1)
            except Exception as e:
                logger.info(f"{Fore.YELLOW}No cookie consent found")

            # Wait for and switch to iframe
            logger.info(f"{Fore.YELLOW}Waiting for iframe to load...")
            try:
                iframe = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'exposantsFrame'))
                )
                self.driver.switch_to.frame(iframe)
                logger.info(f"{Fore.GREEN}Switched to iframe successfully")
            except:
                logger.warning(f"{Fore.YELLOW}Could not find iframe")
                return all_exhibitors

            # Wait for content to load
            time.sleep(5)

            # Click on "Liste" button using JavaScript
            logger.info(f"{Fore.YELLOW}Looking for 'Liste' button...")
            try:
                self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button, a');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].textContent.toLowerCase();
                        if (text.includes('liste') || text.includes('list')) {
                            buttons[i].click();
                            console.log('Clicked Liste button');
                            break;
                        }
                    }
                """)
                logger.info(f"{Fore.GREEN}Clicked 'Liste' button")
                time.sleep(3)
            except Exception as e:
                logger.warning(f"{Fore.YELLOW}Error clicking Liste button: {e}")

            # Wait for list to load
            logger.info(f"{Fore.YELLOW}Waiting for exhibitor list to load...")
            time.sleep(5)

            # Get page source and parse with BeautifulSoup (much faster than Selenium element iteration)
            logger.info(f"{Fore.CYAN}Parsing page source...")
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Save HTML for inspection
            with open('/Users/sylvainboue/web-scraper/equipauto_page.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"{Fore.GREEN}Saved page source for inspection")

            # Try to find exhibitor cards with various selectors
            exhibitor_containers = []

            selectors_to_try = [
                ('div.exhibitor-card', 'exhibitor-card'),
                ('div.exposant-card', 'exposant-card'),
                ('div[class*="exposant"]', 'exposant div'),
                ('div[class*="exhibitor"]', 'exhibitor div'),
                ('li[class*="item"]', 'list items'),
                ('.card', 'card class'),
            ]

            for selector, description in selectors_to_try:
                containers = soup.select(selector)
                if containers and len(containers) > 10:
                    exhibitor_containers = containers
                    logger.info(f"{Fore.GREEN}Found {len(containers)} containers using selector: {selector}")
                    break

            if not exhibitor_containers:
                logger.warning(f"{Fore.YELLOW}Could not find exhibitor containers, trying broader search...")

                # Try to find any repeated structure
                all_divs = soup.find_all('div', class_=True)

                # Count class occurrences to find repeated patterns
                class_counts = {}
                for div in all_divs:
                    classes = ' '.join(div.get('class', []))
                    if classes:
                        class_counts[classes] = class_counts.get(classes, 0) + 1

                # Find the most common class (likely exhibitor cards)
                if class_counts:
                    most_common_class = max(class_counts.items(), key=lambda x: x[1])
                    logger.info(f"Most common class: {most_common_class[0]} ({most_common_class[1]} occurrences)")

                    if most_common_class[1] > 50:  # If it appears more than 50 times
                        class_parts = most_common_class[0].split()
                        for class_part in class_parts:
                            exhibitor_containers = soup.find_all('div', class_=lambda x: x and class_part in x)
                            if len(exhibitor_containers) > 50:
                                logger.info(f"{Fore.GREEN}Found {len(exhibitor_containers)} using class: {class_part}")
                                break

            # Extract data from containers
            logger.info(f"{Fore.CYAN}Extracting data from {len(exhibitor_containers)} exhibitors...")

            for idx, container in enumerate(exhibitor_containers):
                try:
                    exhibitor = {
                        'id': idx + 1,
                    }

                    # Extract all text
                    exhibitor['full_text'] = container.get_text(strip=True, separator=' ')

                    # Try to find name (usually in h2, h3, h4, or strong)
                    name_elem = container.find(['h2', 'h3', 'h4', 'strong', 'b'])
                    if name_elem:
                        exhibitor['name'] = name_elem.get_text(strip=True)

                    # Try to find stand/hall info
                    stand_keywords = ['stand', 'hall', 'pavillon', 'booth']
                    for elem in container.find_all(['span', 'div', 'p']):
                        text = elem.get_text(strip=True).lower()
                        if any(keyword in text for keyword in stand_keywords):
                            exhibitor['stand'] = elem.get_text(strip=True)
                            break

                    # Extract links
                    links = []
                    for a in container.find_all('a', href=True):
                        links.append(a['href'])
                    if links:
                        exhibitor['links'] = links

                    # Extract all class names (for debugging)
                    exhibitor['classes'] = ' '.join(container.get('class', []))

                    all_exhibitors.append(exhibitor)

                    # Log progress every 500 items
                    if (idx + 1) % 500 == 0:
                        logger.info(f"{Fore.CYAN}Extracted {idx + 1}/{len(exhibitor_containers)} exhibitors...")

                except Exception as e:
                    logger.debug(f"Error extracting exhibitor {idx}: {e}")
                    continue

            logger.info(f"{Fore.GREEN}Extraction complete! Total: {len(all_exhibitors)} exhibitors")

            # Save raw JSON for inspection
            with open('/Users/sylvainboue/web-scraper/equipauto_raw.json', 'w', encoding='utf-8') as f:
                json.dump(all_exhibitors[:10], f, ensure_ascii=False, indent=2)  # Save first 10 for inspection
            logger.info(f"{Fore.GREEN}Saved sample data to equipauto_raw.json")

            self.data = all_exhibitors

        except Exception as e:
            logger.error(f"{Fore.RED}Error scraping Equipauto: {e}")
            import traceback
            traceback.print_exc()

        return all_exhibitors


def main():
    """Run Equipauto scraper"""
    scraper = EquipautoScraperFast(headless=False)

    try:
        # Scrape exhibitors
        logger.info("Starting Equipauto scraper...")
        data = scraper.scrape_equipauto(language='fr')

        # Export data
        if data:
            scraper.export_data(format='all', filename='equipauto_exhibitors')
            print(f"\n{Fore.GREEN}Successfully scraped {len(data)} exhibitors!")
            print(f"{Fore.CYAN}Data exported to output/ directory")
            print(f"\nFiles created:")
            print(f"  - output/equipauto_exhibitors.json")
            print(f"  - output/equipauto_exhibitors.csv")
            print(f"  - output/equipauto_exhibitors.xlsx")
            print(f"  - equipauto_page.html (page source for inspection)")
            print(f"  - equipauto_raw.json (sample of first 10 records)")
        else:
            print(f"\n{Fore.YELLOW}No data extracted.")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{Fore.CYAN}Closing browser...")
        scraper.close()
        print("Done!")


if __name__ == '__main__':
    main()
