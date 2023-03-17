import os
import json

from dotenv import load_dotenv
load_dotenv()

home = os.getenv("PROJ_HOME")
articles_filepath = os.path.join(home, "data/chatbot_knowledgebase/subject_matter/article_data.json")

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
