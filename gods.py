from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

import time
from openai import OpenAI
import json
from collections import defaultdict
from num2words import num2words
import random
import datetime



# Initialize the WebDriver (e.g., ChromeDriver)
driver = webdriver.Chrome()
driver.get("https://www.whatbeatsrock.com")
time.sleep(1)

def close_alert_if_present():
    try:
        # Wait for the alert to be present
        WebDriverWait(driver, 0.3).until(EC.alert_is_present())
        
        # Switch to the alert
        alert = driver.switch_to.alert
        
        # Print alert text (optional)
        print(f"Alert detected: {alert.text}")
        
        # Accept the alert to close it
        alert.accept()
        print(f"Alert closed, waiting 5 minutes: {datetime.datetime.now()}")
        time.sleep(300)
    except NoAlertPresentException:
        # If no alert is present, continue
        print("No alert detected.")
    except TimeoutException as e:
        return
    except Exception as e:
        # Handle other exceptions
        print(f"Error handling alert: {e}")
        raise e

def beats(guess):
    time.sleep(0.1)
    textbox = driver.find_element(By.TAG_NAME, "input")
    # Enter text into the text box
    textbox.clear()
    textbox.send_keys(guess)

    button = driver.find_element(By.TAG_NAME, "button")
    button.click()

    try:
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//p[normalize-space(text())='whatbeatsrock.com']"))
        )
    except Exception as e:
        # This exception happens on timeout :( or on alert :)
        # Trying to find the "next" button 
        print(f"Be slow?\n {e}")
        try:
            trigger = WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='next']"))
            )
        except:
            pass
        print(f"Sleepin, {datetime.datetime.now()}")
        time.sleep(300)
        button.click()
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//p[normalize-space(text())='whatbeatsrock.com']"))
        )


    try:
        # Locate the button element with the text "next" using a case-insensitive XPath
        trigger = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='next']"))
        )
        return True
    except Exception as e:
        print(e)
        return False


def hit_next():
    time.sleep(0.1)
    # Scroll into view using JavaScript
    button = driver.find_element(By.TAG_NAME, "button")
    driver.execute_script("arguments[0].scrollIntoView();", button)
    
    # Wait for the button to be clickable
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='next']"))
    )
    button.click()

def refresh():
    driver.refresh()
    time.sleep(1)

class God:
    def __init__(self, name, targ):
        self.name = name
        self.targ = targ
    
    def __str__(self):
        if self.targ == "__NOTHING":
            return f"A person named {self.name} who breaks rocks"
        return f"A person named {self.name} who is stronger, smarter, and faster than {self.targ}"
    
    def to_json(self):
        return {
            "name": self.name,
            "targ": self.targ,
        }

all_names = set()
with open("./names.txt") as file:
    lines = file.readlines()
    for line in lines:
        all_names.add(line.strip())

class Data:
    def __init__(self):
        with open("./data_gods.json") as file:
            data = json.load(file)
            self.chain = [God(d["name"], d["targ"]) for d in data["chain"]]
            self.names = set(data["names"])

    def write(self):
        data = {
            "chain": [g.to_json() for g in self.chain],
            "names": sorted(list(self.names))
        }
        with open("./data_gods.json", "w") as file:
            json.dump(data, file, indent=2)

    # Assumes we start from a refreshed website
    def resume_last(self):
        last = self.chain[-1]
        assert beats(f"A person named {last.targ} who breaks rocks"), f"Couldn't resume to {last}"
        hit_next()
        assert beats(str(last)), f"Failed to resume from target!"
        hit_next()

    def gen_next_guesses(self, cnt=5):
        new_targ = self.chain[-1].name
        newnames = list(all_names - self.names)
        assert len(newnames) >= cnt
        res = set()
        while len(res) < cnt:
            res.add(newnames[random.randint(0, len(newnames) - 1)])

        return [God(name, new_targ) for name in res]

state = Data()
state.resume_last()

win_msg = "Hello, UCF PT! This is my challenge: Can you do better?"
while True:
    print(len(state.chain), "Wins")

    state.write()
    time.sleep(1)
    # If we fail 5 times in a row, give up and just increment
    guesses = state.gen_next_guesses()
    for guess in guesses:
        if beats(str(guess)):
            state.chain.append(guess)
            state.names.add(guess.name)
            hit_next()
            break
        refresh()
        state.resume_last()
    else:
        print(f"Failed five times in a row! Evicting {state.chain[-1]}")
        last_name = state.chain[-1].name
        state.chain = state.chain[:-1]
        state.names.remove(last_name)
