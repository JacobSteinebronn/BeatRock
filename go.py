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

def dump_data():
    out_data = {k: {kk: list(s) for kk, s in guess_data[k].items()} for k in guess_data}
    with open("data.json", 'w') as file:
        json.dump(out_data, file, indent=2)

def clean_crash():
    driver.quit()
    dump_data()
    
    exit(0)

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
        
    # state.cur_chain = guesses
    state.word = targ
    state.queue = []


guess_data = defaultdict(lambda: defaultdict(set))
with open("data.json") as file:
    data = json.load(file)
    for k, v in data.items():
        for kk, vv in v.items():
            guess_data[k][kk] = set(vv)

class State:
    def __init__(self):
        self.queue= []
        self.word= "rock"
        self.cur_chain= ["rock"]

state = State()

dats = 4
try:
    while True:
        if not state.queue:
            print("Querying chain for", state.word)
            state.queue = get_guess_chain(state.word)
            continue
            
        guess = state.queue.pop(0).lower()

        if guess in state.cur_chain or guess in guess_data[state.word]["loses"]:
            print("Boutta fail with", guess+", querying big list for", state.word)

            sizes = [10, 20, 50]
            for siz in sizes:
                queried_deck = get_guess_deck(state.word)
                deck = set(queried_deck) - set(state.cur_chain) - guess_data[state.word]["loses"]
                if len(deck) == 0:
                    print(queried_deck, deck)
                    continue
                
                print(queried_deck, deck)
                state.queue = [list(deck)[0]]
                break
            
            continue

        if dats == 0:
            dats = 4
            dump_data()

        print("Guessing", guess, "for", state.word, state.cur_chain)
        win = beats(guess)
        print(win)
        time.sleep(0.5)

        if win:
            guess_data[state.word]["beats"].add(guess)
            state.cur_chain.append(guess)
            hit_next()
            state.word = guess
        else:
            guess_data[state.word]["loses"].add(guess)
            dump_data()
            resume(state.word)

except Exception as e:
    print(e)
    clean_crash()  

# Wait for the result (adjust the time as necessary)
clean_crash()
