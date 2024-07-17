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
import random

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
    time.sleep(0.1)
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

class Data:
    def __init__(self):
        with open("./data_punct.json") as file:
            data = json.load(file)
            self.chain = data["chain"]
            self.num = data["last_count"]
            self.unresumables = set(data["unresumables"])
            self.unmathables = set(data["unmathables"])

    def write(self):
        data = {
            "chain": self.chain,
            "last_count": self.num,
            "unresumables": sorted(list(self.unresumables)),
            "unmathables": sorted(list(self.unmathables))
        }
        with open("./data_punct.json", "w") as file:
            json.dump(data, file, indent=2)

    # Returns True if we can resume to the word, and performs
    # the resumption - else false, and the website is refreshed
    def _try_rock_resume(self, word):
        if word in self.unresumables:
            return False
        win = beats(word)
        if win:
            hit_next()
            return True
        refresh()
        print("For the last time, rock |" + word + "|")
        self.unresumables.add(word)
        self.write()
        return False

    def _try_math_resume(self, word):
        if word in self.unmathables:
            return False
        assert beats("math"), "Failed math"
        hit_next()
        time.sleep(0.3)
        assert beats("nothing"), "Failed nothing"
        hit_next()
        time.sleep(0.3)
        if beats(self.chain[-1]):
            hit_next()
            return True
        print("For the last time, math |" + word + "|")
        refresh()
        self.unmathables.add(word)
        self.write()
        return False

    def _try_resume(self, word):
        if self._try_rock_resume(word):
            return True
        if self._try_math_resume(word):
            return True
        return False

    # Assumes we start from a refreshed website
    def resume_last(self):
        resume_path = []
        for i in range(len(self.chain) - 1, -1, -1):
            if self._try_resume(self.chain[i]):
                # We have resumed to this word, so we just need to guess to the end now
                resume_path = self.chain[i+1:]
                break
        else:
            raise Exception(f"Somehow we couldn't resume! {self}")
        
        for word in resume_path:
            print("Resuming on " + str(resume_path))
            assert beats(word), "Failed resumption on known chain!"
            hit_next()

    def gen_next_guesses(self, cnt=5):
        res = []
        
        for tries in range(1000):
            if len(res) >= cnt:
                break
            spaces = random.randint(1, 10)
            num_punct = random.randint(0, 1)
            punct = ""
            for i in range(num_punct):
                punct += ".!_,"[random.randint(0, 3)]
            
            obj = "Pacifist" if "nuke" in self.chain[-1].lower() else "Nuke"

            guess = num2words(self.num).replace('-', ' ') + " "*spaces + obj
            if self.num > 1:
                guess += "s"
            guess += punct
            if guess in self.chain:
                continue
            res.append(guess)
        else:
            raise Exception(f"Failed to gen {cnt} guesses after 1000 tries")

        return res

state = Data()
state.resume_last()
while True:
    state.write()
    # If we fail 5 times in a row, give up and just increment
    guesses = state.gen_next_guesses()
    for guess in guesses:
        print(f"Guessing {guess} on {state.chain[-1]}")
        if beats(guess):
            state.chain.append(guess)
            hit_next()
            break
        refresh()
        state.resume_last()
    else:
        state.num += 1