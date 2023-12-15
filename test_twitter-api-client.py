from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import requests
import json
import os
import asyncio
from twitter.search import Search

def login():
    load_dotenv(find_dotenv())
    global EMAIL, USERNAME, PASSWORD, DEBUG
    EMAIL = os.getenv('EMAIL')
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    DEBUG = os.getenv("DEBUG", default="False")

def load_data(query, user):
    # implement this function to get 
    search = Search(email=EMAIL, username=USERNAME, password=PASSWORD, save=True, debug=DEBUG)
    res = search.run(
    limit=1,
    retries=5,
    queries=[
        {
            'category': 'Top',
            'query': f'{query} from:{user}'
        },],)
    print(len(res))
    return

def chat(data):
    url = 'http://localhost:11434/api/generate'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "model": "llama2",
        "prompt": f"You are a datascientist working on creating and storing knowledge, so please extract useful summary from following tweet data \n DATA: {data}"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code==200:
        with open(f'{data}.txt', 'w') as f:
            f.write(f'SUMMARY\n{response.text}\n\n\nDATA\n{data}')
    else:
        print(f"ERROR, status code: {response.status_code} \n \n text: {response.text}")

if __name__ == '__main__':
    login()
    print("test working")
    load_data('Mistral', 'cto_junio')