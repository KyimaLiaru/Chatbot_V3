import fasttext
import os

model_path = os.path.join(os.path.dirname(__file__), "../Data/lid.176.bin")
model = fasttext.load_model(model_path)

def detectlanguage(text: str) -> str:
    try:
        labels, probabilities = model.predict(text)
        lang_code = labels[0].replace("__label__", "")
        if lang_code == "ko":
            return "Korean"
        elif lang_code == "es":
            return "Spanish"
        else:
            return "English"
    except Exception as e:
        print(f"Chat.ONE | Language Detection Error: {e}")
        return "en"