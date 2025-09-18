import fasttext
import os, re

model_path = os.path.join(os.path.dirname(__file__), "../Data/lid.176.bin")
model = fasttext.load_model(model_path)

def detectlanguage(text: str) -> str:
    HANGUL_RE = re.compile(
        r'[\u1100-\u11FF\uA960-\uA97F\uD7B0-\uD7FF\uFFA0-\uFFDC\u3131-\u318E\uAC00-\uD7A3]'
    )
    isKorean = HANGUL_RE.search(text)

    if isKorean:
        return 'Korean'
    else:
        try:
            labels, probabilities = model.predict(text)
            lang_code = labels[0].replace("__label__", "")
            if lang_code == "es":
                return "Spanish"
            else:
                return "English"
        except Exception as e:
            print(f"Chat.ONE | Language Detection Error: {e}")
            return "English"