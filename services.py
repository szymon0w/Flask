import wikipedia as wikipedia
import re

def get_definition(term_to_find: str):
    wikipedia.set_lang("pl")
    word = wikipedia.search(term_to_find)[0]
    try:
        summary = wikipedia.summary(word, auto_suggest=False, redirect=True)
    except wikipedia.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            summary = wikipedia.summary(e.options[0], auto_suggest=True)
    # if len(summary.split(". ")[0]) > 2:
    #     return re.sub(r"\(.+?\)", '', ". \n".join(summary.split(". ")[:2]))
    # else:
    return re.sub(r"\(.+?\)", '', ". \n".join(summary.split(". ")))