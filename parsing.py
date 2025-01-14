import re

import stanza

stanza.download('ru')
nlp_ru_lemma = stanza.Pipeline('ru', processors='tokenize,lemma,pos,depparse')

def delete_inside_parentheses_and_brackets(text):
    result = re.sub(r"\([^()]*\)", "", text)
    result = re.sub(r'\[[^\]]*\]', '', result)
    return result

def extract_case(feature_string):
    match = re.search(r'Case=([^|]+)', feature_string)
    if match:
        return match.group(1)
    return None

def process_text(txt):
    test_ppl = nlp_ru_lemma(delete_inside_parentheses_and_brackets(txt))
    values = []
    for sentence in test_ppl.sentences:
        for word in sentence.words:
            # print(word)
            if word.upos == 'ADP':
                dep = sentence.words[word.head - 1]
                main = sentence.words[dep.head - 1]
                if dep.upos != 'NOUN':
                    continue
                # print(main.text, word.text, dep.text)
                prep = word.lemma.lower() if word.text.lower() != 'подо' else 'под'
                values.append((main.text.lower(), main.lemma.lower(),prep , dep.text.lower(), dep.lemma.lower(), extract_case(dep.feats), sentence.text, 3,main.upos ))
    return values