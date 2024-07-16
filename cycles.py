from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from openai import OpenAI
import json
from collections import defaultdict
from num2words import num2words

client = OpenAI(
  organization='org-l2pRwWb7f6nB1IOdIPnv2gXD',
  project='proj_IUyyuJ47uRgjW9UkQXmYYACS',
  api_key="sk-svcacct-p31xcYc34wTKTFbuHZ91T3BlbkFJlJ0b9O4PgCxIX5CHDdJg"
)

def query_chatgpt(prompt):
    # Send a request to the model
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    # Return the text of the response
    return response.choices[0].message.content.strip()

def trim_junk(arr):
    res = []
    for x in arr:
        if "metaphorical" in x:
            continue
        if " beats " in x:
            continue
        if "in a fight" in x:
            continue
        
        res.append(x)
    return res

def get_guess_chain(term, cnt=10):
    prompt = f"Give something that beats \"{term}\" in a metaphorical fight. Then, give me something that beats that, and so on {cnt} times. Give this to me in JSON format with numbers as the keys"
    response = json.loads(query_chatgpt(prompt))
    results = []
    for i in range(1, cnt+1):
        results.append(response[str(i)])

    return trim_junk(results)

def get_guess_deck(term, cnt=10):
    prompt = f"Give me {cnt} things that beat \"{term}\" in a metaphorical fight. Give this to me in JSON format with numbers as the keys"
    response = json.loads(query_chatgpt(prompt))
    print(response)
    results = []
    for i in range(1, cnt+1):
        results.append(response[str(i)])

    return trim_junk(results)

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

    next_button = WebDriverWait(driver, 30).until(
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

def resume(targ):
    refresh()
    guesses = ["math", "nothing", targ]
    for guess in guesses:
        win = beats(guess)
        if not win:
            print("Failed to resume to", targ, "at", guess)
            clean_crash()
        time.sleep(0.3)
        hit_next()


isNukes = True
num = 1
while True:

    guess = num2words(num).replace('-', ' ')
    if isNukes:
        guess += " nukes"
    else:
        guess += " pacifists"

    win = beats(guess)
    time.sleep(0.3)
    if win:
        hit_next()
        if isNukes:
            num += 1
        isNukes = not isNukes
        continue
    else:
        # We lost... resume to the last # of nukes, then add 2, then pacifists
        refresh()
        time.sleep(0.5)

        assert beats("a nuke")
        hit_next()
        assert beats("a pacifist")
        hit_next()
        assert beats(num2words(num) + " nukes"), "Failed to win with " + str(num) + " nukes"
        hit_next()
        num += 2
        isNukes = False