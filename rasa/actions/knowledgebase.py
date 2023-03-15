import os
import json

from dotenv import load_dotenv
load_dotenv()

home = os.getenv("PROJ_HOME")
exhibits_filepath = os.path.join(home, "data/chatbot_knowledgebase/institutional/exhibits.json")
galleries_filepath = os.path.join(home, "data/chatbot_knowledgebase/institutional/galleries.json")
articles_filepath = os.path.join(home, "data/chatbot_knowledgebase/subject_matter/article_data.json")

with open(exhibits_filepath, "r") as f:
    exhibits = json.load(f)

exhibit_ids = [exhibit["id"] for exhibit in exhibits]

with open(galleries_filepath, "r") as f:
    galleries = json.load(f)

gallery_ids = [gallery["id"] for gallery in galleries]

with open(articles_filepath, "r") as f:
    articles = json.load(f)

title_aliases = []
alias_id_lookup = {}
text_id_lookup = {}

for article in articles:
    article["aliases"].insert(0, article["title"])
    del article["title"]
    title_aliases += article["aliases"]
    alias_id_lookup.update({
        article["article_id"]: article["aliases"]
    })
    text_id_lookup.update({
        article["article_id"]: article["paragraphs"]
    })
