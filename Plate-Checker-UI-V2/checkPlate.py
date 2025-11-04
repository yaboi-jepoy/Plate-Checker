"""Cleaned-up plate lookup helper using Selenium.

This module provides a single function `check_plate` that performs a
search on the LTO NCR "brand-new motor vehicle and motorcycle" page for a
given plate number and returns a list of result lines.

The previous script-style prints were replaced with logging and the
selector/lookup logic was simplified and made more robust.
"""

from typing import List, Optional
import logging
import argparse
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

LOG = logging.getLogger(__name__)


def check_plate(plate_number: str, headless: bool = True, timeout: int = 15) -> tuple[List[str], dict]:
    """Search LTO NCR site for a plate number and return textual results and structured data.

    Args:
        plate_number: Plate string to search for.
        headless: Whether to run Chrome in headless mode.
        timeout: Maximum seconds to wait for elements.

    Returns:
        A tuple containing:
        - List[str]: Formatted text results for display
        - dict: Structured data with keys: plate_number, mv_classification, 
               lto_nru_office, released_to, date_released
    """
    results: List[str] = []
    data = {
        'plate_number': '',
        'mv_classification': '',
        'lto_nru_office': '',
        'released_to': '',
        'date_released': ''
    }

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/118.0.0.0 Safari/537.36'
    )

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.ltoncr.com/brand-new-motor-vehicle-and-motorcycle/")
        LOG.debug("Navigated to site: %s", driver.current_url)

        # Primary strategy: find the iframe that includes the plate-search and
        # locate an input inside it. Try a small set of selectors to be robust.
        iframe_selectors = ["iframe[src*='npindex']", "iframe"]
        input_selectors = [
            "#search_text",
            ".search-txt",
            ".input-group input[type='text']",
            "input[type='text']",
            "input",
        ]

        # Give the page a short moment to settle (replaces large blind sleeps)
        time.sleep(2)

        iframe = None
        for sel in iframe_selectors:
            try:
                iframe = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                LOG.debug("Found iframe using selector: %s", sel)
                break
            except TimeoutException:
                LOG.debug("No iframe found with selector: %s", sel)

        if iframe:
            driver.switch_to.frame(iframe)
            LOG.debug("Switched to iframe for plate inquiry")
        else:
            LOG.debug("No specific iframe found; continuing in main document")

        # Try several selectors in order until one yields a clickable input
        input_box = None
        for sel in input_selectors:
            try:
                input_box = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                LOG.debug("Found input using selector: %s", sel)
                break
            except TimeoutException:
                LOG.debug("Input not found with selector: %s", sel)

        if not input_box:
            LOG.error("Could not locate an input box for plate search")
            return results

        LOG.info("Using %s to search.", plate_number)

        # Populate the input (try JS first, then fallback to send_keys)
        try:
            driver.execute_script("arguments[0].value = ''", input_box)
            driver.execute_script("arguments[0].value = arguments[1]", input_box, plate_number.strip())
        except Exception:
            input_box.clear()
            input_box.send_keys(plate_number.strip())

        # Trigger events that commonly cause the search to run. Fire both keyup and change.
        try:
            # First clear any existing results
            driver.execute_script("if(document.getElementById('result')) document.getElementById('result').innerHTML = '';")
            
            # Then trigger the search events
            driver.execute_script(
                """
                var el = arguments[0];
                var plate = arguments[1];
                if (window.jQuery) {
                    $(el).val(plate).trigger('keyup').trigger('change');
                } else {
                    el.value = plate;
                    el.dispatchEvent(new Event('keyup'));
                    el.dispatchEvent(new Event('change'));
                }
                """,
                input_box,
                plate_number.strip()
            )
            LOG.debug("Triggered search events via JavaScript")
        except Exception as e:
            LOG.debug("Triggering events via JS failed: %s", e)

        # Wait for results list items
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#result li"))
            )
            # First wait a bit longer for jQuery to populate results
            time.sleep(3)  # Give jQuery AJAX call time to complete
            
            # Try to get results both directly and via JavaScript
            items = driver.find_elements(By.CSS_SELECTOR, "#result li")
            if not items:
                LOG.debug("No items found directly, trying JavaScript")
                try:
                    items_html = driver.execute_script("return document.getElementById('result').innerHTML")
                    LOG.debug("Results HTML: %s", items_html)
                except Exception as e:
                    LOG.debug("JavaScript fallback failed: %s", e)
            
            for item in items:
                text = item.text.strip()
                if text:
                    # Try to split on colon if present, otherwise use the full text
                    if ":" in text:
                        label, value = map(str.strip, text.split(":", 1))
                        results.append(f"{label}: {value}")
                        
                        # Map the label to our data dictionary keys
                        key = label.lower().replace(" ", "_")
                        if key in data:
                            data[key] = value
                    else:
                        results.append(text)
            
            if not results:
                LOG.info("No results found for %s", plate_number)
        except TimeoutException:
            LOG.info("No results found for %s", plate_number)

    except (NoSuchElementException, TimeoutException) as exc:
        LOG.exception("Selenium error while searching for plate %s: %s", plate_number, exc)
    finally:
        driver.quit()

    return results, data


# Backwards-compatible alias for existing callers/scripts that only want the text results
def checkPlate(plate_number: str) -> List[str]:
    """Legacy wrapper that returns only the text results."""
    results, _ = check_plate(plate_number)
    return results


def _main() -> None:
    parser = argparse.ArgumentParser(description="Check plate on LTO NCR site")
    parser.add_argument("plate", help="Plate number to search for")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Run with visible Chrome")
    parser.add_argument("--timeout", type=int, default=15, help="Seconds to wait for elements")
    parser.add_argument("--json", action="store_true", help="Output structured JSON data only")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s"
    )

    results, data = check_plate(
        args.plate, 
        headless=args.headless, 
        timeout=args.timeout
    )
    
    if args.json:
        import json
        print(json.dumps(data, indent=2))
    else:
        # Print formatted results
        for line in results:
            print(line)


if __name__ == "__main__":
    _main()
