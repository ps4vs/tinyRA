from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import requests
import json
import os
import asyncio
import gradio as gr
from twitter.search import Search


def login():
    load_dotenv(find_dotenv())
    global EMAIL, USERNAME, PASSWORD, DEBUG
    EMAIL = os.getenv("EMAIL")
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    DEBUG = os.getenv("DEBUG", default="False")


def load_data(query, user):
    # implement this function to get
    search = Search(
        email=EMAIL, username=USERNAME, password=PASSWORD, save=True, debug=DEBUG
    )
    res = search.run(
        limit=1,
        retries=5,
        queries=[
            {"category": "Top", "query": f"{query} from:{user}"},
        ],
    )
    full_text = res[0][0]["content"]["itemContent"]["tweet_results"]["result"][
        "legacy"
    ]["full_text"]
    return res, full_text


def chat(text):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama2",
        "prompt": f"Analyze the following data to extract key claims and any realistic meta knowledge that can be derived from them. Present these findings from a first-person perspective, without mentioning the data's origin as a tweet or your role as a data scientist. Data provided: {text}",
        "stream": False,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        with open(f"{text[0:4]}.txt", "w") as f:
            f.write(f"SUMMARY\n{response.text}\n\n\nDATA\n{data}")
    else:
        print(f"ERROR, status code: {response.status_code} \n \n text: {response.text}")
    return response.text


def generate_claims(query, author):
    login()
    res, full_text = load_data(query, author)
    response = chat(full_text)
    summary = json.loads(response)["response"]
    return full_text, summary


if __name__ == "__main__":
    interface = gr.Interface(
        fn=generate_claims,
        inputs=[gr.Textbox(lines=1), gr.Textbox(lines=1)],
        outputs=["text", "text"],
    )
    interface.launch()

# create a loop and place it in context, it contains necessary context which is shared across all the crawl, extract, cluster, and create files
# the preprocessing involves, scraping relevant tweets from authors timeline
# associated replies, and conversation history of the author for each tweet should be created
# this is stored along with meta-data created such as author, and summarised tweet history and passed to extract.