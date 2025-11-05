# scraper.py

Scraper générique réutilisable avec Selenium pour sites JavaScript/React/Vue.

**Fonctionnalités**: Gestion iframes, rotation User-Agent, proxy, rate limiting, retry logic, export JSON/CSV/Excel.

**Usage**:
```python
from scraper import WebScraper

selectors = {'container': '.item', 'title': 'h2'}
scraper = WebScraper()
data = scraper.scrape_url('https://example.com', selectors)
scraper.export_data(format='all')
scraper.close()
```
