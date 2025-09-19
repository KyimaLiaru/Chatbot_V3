import re
from typing import List

import nltk
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import TreebankWordTokenizer

from Chatbot.Common.LoadInitData import PatternInfo

# --- NLTK 리소스 보장 (없으면 받아서 캐싱) ---
for res in ("stopwords", "wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{res}")
    except LookupError:
        nltk.download(res)

# POS tagger (버전에 따라 이름이 다를 수 있어 둘 다 시도)
try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    try:
        nltk.download("averaged_perceptron_tagger_eng")
    except Exception:
        # 구버전 백업
        try:
            nltk.data.find("taggers/averaged_perceptron_tagger")
        except LookupError:
            nltk.download("averaged_perceptron_tagger")

# 토큰화헤서 제외할 단어 및 특수토큰 정규식 정의
KEEP_STOPWORDS = {"what","who","where","when","why","how", "can", "could"}
PLACEHOLDER_RE = re.compile(r"<[A-Za-z_][A-za-z0-9_]*>$")

# 제거할 문장부호 정의
PUNCT_DROP = {",", "'", "?", "."}

# --- 토크나이저 / 리소스 로드 ---
TB = TreebankWordTokenizer()
EN_STOP = set(stopwords.words("english"))
EN_STOP_FILTERED = EN_STOP - KEEP_STOPWORDS
LEMM = WordNetLemmatizer()

# <FIQ>, <BWAY>, <URL> 등 과 같은 태그는 소문자 변형 대상에서 제외
def lowerWords(tokens: list[str]) -> list[str]:
    result = []
    for token in tokens:
        result.append(token if PLACEHOLDER_RE.match(token) else token.lower())
    return result

# 기본 형태소 추출
def get_wordnet_pos(tag: str):
    if   tag.startswith('J'): return wordnet.ADJ
    elif tag.startswith('V'): return wordnet.VERB
    elif tag.startswith('N'): return wordnet.NOUN
    elif tag.startswith('R'): return wordnet.ADV
    return wordnet.NOUN  # 기본: 명사

# 기본 형태 단어로 변형 (예. policies -> policy, detailed -> detail)œ
def lemmatize_tokens(tokens: list[str]) -> list[str]:
    # 레마 대상만 분리 ()
    plain = [t for t in tokens if not PLACEHOLDER_RE.match(t)]
    if not plain:
        return tokens
    tagged = pos_tag(plain)  # [('information','NN'), ('informs','VBZ'), ...]
    lemmas = [LEMM.lemmatize(w, get_wordnet_pos(t)) for w, t in tagged]

    # 원래 자리로 합치기
    out, j = [], 0
    for t in tokens:
        if PLACEHOLDER_RE.match(t):
            out.append(t)
        else:
            out.append(lemmas[j]); j += 1
    return out

# Tokenization
def Tokenize(text: str, lang: str) -> List[str]:
    if lang == "English":
        # Step 1 - 특수 토큰 (FIQ, BWAY, R, URL, IP, PORT 등) 마스킹 처리
        text = PatternInfo.maskTokens(text)
        # Step 2 - Treebank 토큰화
        tokens = TB.tokenize(text)
        # Step 3 - 문장부호 (. , ? ')제거
        tokens = [token for token in tokens if token not in PUNCT_DROP]
        # Step 4 - FIQ, BWAY, R 등을 제외한 텍스트 소문자화
        tokens = lowerWords(tokens)
        # Step 5 - 불용어 제거
        tokens = [token for token in tokens if not token in EN_STOP_FILTERED]
        # Step 6 - 마스킹된 특수 토큰 해제 처리
        tokens = PatternInfo.unmaskTokens(tokens)
        # Step 7 - 형태소 분석 (-s, -ing, -ed 등 제거)
        tokens = lemmatize_tokens(tokens)

        return tokens
    else:
        raise Exception("Language not yet supported")


# TF-IDF 의도 분석 코드 추가 예정
