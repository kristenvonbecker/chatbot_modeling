from actions.knowledgebase import articles, exhibits
import random
from fuzzywuzzy import fuzz, process

from importlib import reload

reload(articles)
reload(exhibits)


def get_article_title_matches(subject, threshold=75, scorer=fuzz.WRatio):
    matches = process.extract(subject, articles.title_aliases, scorer=scorer, limit=5)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches


def get_article_text(article_id):
    text = articles.text_id_lookup[article_id][0]
    return text


def get_exhibit_alias_matches(alias, threshold=75, scorer=fuzz.WRatio):
    matches = process.extract(alias, exhibits.name_aliases, scorer=scorer, limit=3)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches


def get_exhibit_ids(alias):
    ids = []
    for exhibit_id, aliases in exhibits.alias_id_lookup.items():
        if alias in aliases:
            ids.append(exhibit_id)
    return ids


def get_exhibit_name(exhibit_id):
    exhibit_name = exhibits.alias_id_lookup[exhibit_id][0]
    return exhibit_name


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


def get_exhibit_location(exhibit_id):
    location_code = [exhibit["location"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    location = location_dict.get(location_code)
    return location, location_code


def get_exhibit_creator(exhibit_id):
    names = [exhibit["creators"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    return names


def get_exhibit_date(exhibit_id):
    year = [exhibit["year"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    return year


def get_about_exhibit(exhibit_id):
    short_sum = [exhibit["short-summary"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    medium_sum = [exhibit["medium-summary"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    fun_facts = [exhibit["fun-facts"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    return short_sum, medium_sum, fun_facts


def get_related_exhibit(exhibit_id):
    related_ids = [exhibit["related_exhibits"] for exhibit in exhibits.exhibits if exhibit["id"] == exhibit_id][0]
    return related_ids


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
