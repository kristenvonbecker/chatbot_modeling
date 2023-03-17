import os
import json

from dotenv import load_dotenv
load_dotenv()

home = os.getenv("PROJ_HOME")
exhibits_filepath = os.path.join(home, "data/chatbot_knowledgebase/institutional/exhibits.json")

with open(exhibits_filepath, "r") as f:
    exhibits = json.load(f)

exhibit_ids = [exhibit["id"] for exhibit in exhibits]

name_aliases = []
alias_id_lookup = {}

for exhibit in exhibits:
    exhibit["aliases"].insert(0, exhibit["title"])
    name_aliases += exhibit["aliases"]
    if exhibit["id"] in alias_id_lookup.keys():
        alias_id_lookup[exhibit["id"]] += exhibit["aliases"]
    else:
        alias_id_lookup.update({
            exhibit["id"]: exhibit["aliases"]
        })
