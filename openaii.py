from openai import OpenAI
import json

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

def get_guess_chain(term):
    cnt = 10
    prompt = f"Give something that beats \"{term}\" in a metaphorical fight. Then, give me something that beats that, and so on {cnt} times. Give this to me in JSON format with numbers as the keys"
    response = json.loads(query_chatgpt(prompt))
    results = []
    for i in range(1, cnt+1):
        results.append(response[str(i)])

    return results

def get_guess_deck(term):
    cnt = 10
    prompt = f"Give me {cnt} things that beat \"{term}\" in a metaphorical fight. Give this to me in JSON format with numbers as the keys"
    response = json.loads(query_chatgpt(prompt))
    results = []
    for i in range(1, cnt+1):
        results.append(response[str(i)])

    return results

# Example usage
# prompt = "Give something that beats \"The end of time\" in a metaphorical fight. Then, give me something that beats that, and so on 10 times. Give this to me in JSON format with numbers as the keys"
# response = query_chatgpt(prompt)
# print(json.loads(response))
print(get_guess_chain("Love"))
print(get_guess_deck("Love"))