import re
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

from Chatbot.Common.LoadInitData import PatternInfo

for res in ("stopwords",):
    try:
        nltk.data.find(f"corpora/{res}")
    except LookupError:
        nltk.download(res)

PLACEHOLDER_RE = re.compile(r"<[A-Za-z_][A-za-z0-9_]*>$")
EN_WORD_RE = re.compile(r"\S+")
EN_STOP = set(stopwords.words("english"))
EN_STEM = SnowballStemmer("english")


def lowerWords(tokens: list[str]) -> list[str]:
    result = []
    for token in tokens:
        result.append(token if PLACEHOLDER_RE.match(token) else token.lower())
    return result

# Tokenization
def Tokenize(text: str, lang: str) -> List[str]:
    if lang == "English":
        # Step 1 - <FIQ>, <BWAY>, <R>, <URL>, <IPP>, <IP>, <PORT> 등 텍스트 치환
        tokens = PatternInfo.replaceTokens(text)
        # Step 2 - 공백 기준 토큰화
        tokens = EN_WORD_RE.findall(tokens)
        # Step 3 - FIQ, BWAY, R 등을 제외한 텍스트 소문자화
        tokens = lowerWords(tokens)
        # Step 4 - 불용어 제거
        tokens = [token for token in tokens if not token in EN_STOP]
        # Step 5 - 형태소 분석 (-s, -ing, -ed 등 제거)
        tokens = [EN_STEM.stem(token) if not PLACEHOLDER_RE.match(token) else token for token in tokens]

        return tokens

    else:
        raise Exception("Language not yet supported")


# TF-IDF 의도 분석 코드 추가 예정
