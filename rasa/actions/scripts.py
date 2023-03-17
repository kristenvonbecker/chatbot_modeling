from fuzzywuzzy import fuzz, process
from actions.knowledgebase import articles, exhibits
import random

from importlib import reload
reload(articles)
reload(exhibits)


def get_article_title_matches(subject, threshold=90, scorer=fuzz.WRatio):
    matches = process.extract(subject, articles.title_aliases, scorer=scorer, limit=5)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches


def get_article_text(article_id):
    text = articles.text_id_lookup[article_id][0]
    return text


def get_exhibit_id(alias):
    matches = []
    for exhibit in exhibits:
        if alias in exhibit["aliases"]:
            matches.append(exhibit["id"])
    matches = list(set(matches))
    return matches


location_dict = {
    "Gallery 1": "Bernard and Barbro Osher Gallery 1: Human Phenomena",
    "Gallery 2": "Gallery 2: Tinkering",
    "Gallery 3": "Bechtel Gallery 3: Seeing & Reflections",
    "Gallery 4": "Gordon and Betty Moore Gallery 4: Living Systems",
    "Gallery 5": "Gallery 5: Outdoor Exhibits",
    "Gallery 6": "Fisher Bay Observatory Gallery 6: Observing Landscapes",
    "Entrance": "the Exploratorium entrance",
    "Crossroads": "Crossroads: Getting Started",
    "Bay Walk": "the Koret Foundation Bay Walk",
    "Plaza": "the Plaza",
    "Atrium": "the Ray and Dagmar Dolby Atrium",
    "Jetty": "the San Francisco Marina Jetty",
    "NOT ON VIEW": "NOT ON VIEW"
}


def get_exhibit_location(id):
    location_code = [exhibit["location"] for exhibit in exhibits.exhibits if exhibit["id"] == id][0]
    location = location_dict.get(location_code)
    return location, location_code


def get_fave_exhibit():
    rand_id = random.choice(exhibits.exhibit_ids)
    rand_exhibit = [exhibit["title"] for exhibit in exhibits.exhibits if exhibit["id"] == rand_id][0]
    fun_facts = []
    for exhibit in exhibits.exhibits:
        if exhibit["id"] == rand_id:
            fun_facts += exhibit["fun-facts"]
    if fun_facts:
        rand_fun_fact = random.choice(fun_facts)
    else:
        rand_fun_fact = None
    return rand_id, rand_exhibit, rand_fun_fact
