from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def check_plate(plate_number: str) -> tuple[list[str], dict]:
    # initialize arrays and formatting
    results = []
    data = {
        'plate_number': '',
        'mv_classification': '',
        'lto_nru_office': '',
        'released_to': '',
        'date_released': ''
    }
    
    # Selenium flags
    options = Options()
    options.add_argument('--headless')  # headless mode para di na lumabas yung browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # initialize driver
    driver = webdriver.Chrome(options=options)
    
    # try-except for crash prevention
    try:
        # link to LTO site
        driver.get("https://www.ltoncr.com/brand-new-motor-vehicle-and-motorcycle/")
        
        # since the relevant section is embedded inside the website
        # we usde iframes to trigger and "wait" for it
        print("debug: Looking for iframe...")
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='npindex']"))
            )
            print("debug: Found iframe, switching to it...")
            driver.switch_to.frame(iframe)
        except Exception as e:
            print(f"Error finding iframe: {e}")
            print("Page source:", driver.page_source)
        
        # find the textbox
        # search_text siya sa html
        # then input the plate number
        input_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search_text"))
        )
        input_box.clear()
        input_box.send_keys(plate_number.strip())
        time.sleep(1)
               
        # from stack overflow
        # trigger event para sa site
        driver.execute_script(
            """
            if (window.jQuery) {
                $('#search_text').trigger('keyup').trigger('change');
            }
            """
        )
        
        # kailangan ng delay for update sa site
        # i-aadjust ata to based sa internet speed
        time.sleep(1.5)
        
        # results based sa list element sa html 
        items = driver.find_elements(By.CSS_SELECTOR, "#result li")
        print(f"Found {len(items)} results")
        
        
        # iterate through the detecte list items
        
        for item in items:
            text = item.text.strip()
            print({text})
            if ":" in text:
                # split the text through colon
                label, value = map(str.strip, text.split(":", 1))
                # then store to a label-value "results" list
                results.append(f"{label}: {value}")
                
                # store in dict
                key = label.lower().replace(" ", "_")
                if key in data:
                    data[key] = value
            # just append if no :
            else:
                results.append(text)
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
    
    # results is for human-readable format
    # data is the "programmatically readable" format
    return results, data

# if irrun galing sa terminal
# if __name__ == "__main__":
#     plate = input("Enter plate number: ")
#     results, data = check_plate(plate)
    
    # print("\nResults:")
    # for result in results:
    #     print(result)
        
    # print("\nStructured Data:")
    # for key, value in data.items():
    #     if value:  # Only print if there's a value
    #         print(f"{key}: {value}")