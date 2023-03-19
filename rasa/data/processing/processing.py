import spacy
from unidecode import unidecode
import contractions
from word2number import w2n

nlp = spacy.load('en_core_web_sm')


def remove_whitespace(text):
    text = ' '.join(text.strip().split())
    return text


def remove_accents(text):
    text = unidecode(text)
    return text


def expand_contractions(text):
    text = contractions.fix(text)
    return text


def preprocess(text,
               accented_chars=True,
               contractions=True,
               convert_num=True,
               whitespace=True,
               lemmatization=True,
               lowercase=True,
               punctuation=True,
               remove_num=False,
               special_chars=True,
               stop_words=True):

    if whitespace:
        text = remove_whitespace(text)
    if accented_chars:
        text = remove_accents(text)
    if contractions:
        text = expand_contractions(text)
    if lowercase:
        text = text.lower()

    doc = nlp(text)
    proc_text = []

    for token in doc:
        flag = False
        this_token = token.text
        if stop_words and token.is_stop and token.pos_ != 'NUM':  # removes stop words which aren't numbers
            flag = True
        elif punctuation and token.pos_ == 'PUNCT':  # removes punctuation
            flag = True
        elif special_chars and token.pos_ == 'SYM':  # removes special characters
            flag = True
        elif remove_num and (token.pos_ == 'NUM' or token.text.isnumeric()):  # removes numbers
            flag = True
        if convert_num and token.pos_ == 'NUM' and not flag:  # converts number words to numerals
            try:
                this_token = w2n.word_to_num(token.text)
            except ValueError:
                pass
        if lemmatization and token.lemma_ != "-PRON-" and not flag:  # gets lemmas, ignoring pronouns
            this_token = token.lemma_
        if this_token != "" and not flag:  # appends (converted and/or lemmatized) unflagged tokens to clean_text
            proc_text.append(this_token)

    return ' '.join(proc_text)
