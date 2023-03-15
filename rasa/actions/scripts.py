from fuzzywuzzy import fuzz, process
from actions import knowledgebase
import random

from importlib import reload
reload(knowledgebase)


def get_title_matches(subject, threshold=90, scorer=fuzz.WRatio):
    matches = process.extract(subject, knowledgebase.title_aliases, scorer=scorer, limit=5)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches

def get_text(article_id):
    text = knowledgebase.text_id_lookup[article_id][0]
    return text


def get_fave_exhibit():
    rand_id = random.choice(knowledgebase.exhibit_ids)
    rand_exhibit = [exhibit["title"] for exhibit in knowledgebase.exhibits if exhibit["id"] == rand_id][0]
    fun_facts = []
    for exhibit in knowledgebase.exhibits:
        if exhibit["id"] == rand_id:
            fun_facts += exhibit["fun-facts"]
    if fun_facts:
        rand_fun_fact = random.choice(fun_facts)
    else:
        rand_fun_fact = None
    return rand_id, rand_exhibit, rand_fun_fact
