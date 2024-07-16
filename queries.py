from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the WebDriver (e.g., ChromeDriver)
driver = webdriver.Chrome()
driver.get("https://www.whatbeatsrock.com")
time.sleep(1)

def beats(guess):
    textbox = driver.find_element(By.TAG_NAME, "input")
    # Enter text into the text box
    textbox.clear()
    textbox.send_keys(guess)

    button = driver.find_element(By.TAG_NAME, "button")
    button.click()

    next_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//p[normalize-space(text())='whatbeatsrock.com']"))
    )
    try:
        # Locate the button element with the text "next" using a case-insensitive XPath
        trigger = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='next']"))
        )
        return True
    except:
        return False

def hit_next():
    button = driver.find_element(By.TAG_NAME, "button")
    button.click()

def refresh():
    driver.refresh()
    time.sleep(1)


cur_word = "rock"

for guess in ["lava", "water", "blankets", "puppies", "hammer"]:
    win = beats(guess)
    print(cur_word, win, guess)
    time.sleep(1)

    if win:
        hit_next()
        cur_word = guess
    else:
        refresh()
        cur_word = "rock"
    

# Wait for the result (adjust the time as necessary)
input()
driver.quit()
