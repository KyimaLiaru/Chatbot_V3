import requests
import json

from Common.GetErrorMessage import GetErrorMessage

def queryLLM(query: str, model: str = "mistral", temperature: float = 0.2, retry=[0]):
    payload = {
        "model": model,
        "prompt": query,
        "temperature": temperature,
        "format": "json",
        "stream": False
    }

    # Case 1: "stream": True
    # try:
    #     response = requests.post("http://localhost:11434/api/generate", json=payload, stream=False, timeout=60)
    #     response.raise_for_status()
    #
    #     full_response = ""
    #     for line in response.iter_lines(decode_unicode=True):
    #         if line:
    #             try:
    #                 chunk = json.loads(line)
    #                 full_response += chunk.get("response", "")
    #             except json.JSONDecodeError:
    #                 continue
    #     return json.loads(full_response.strip())

    # Case 2: "stream": False
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=False, timeout=60)
        response.raise_for_status()

        result = response.json()["response"]
        # full_response = result.get("response", "").strip().replace("'", '\\\"')


        # print("\nflag =====bot start===========")
        # try:
        #     print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
        # except Exception as e:
        #     print("NO JSON")
        #     print(result)
        # print("===========bot end============\n")

        try:
            return json.loads(result)
        except Exception as e:
            print("Chat.ONE | LLM returned non-JSON object, trying again...")
            retry[0] += 1
            if retry[0] < 10:
                return queryLLM(query, model, temperature, retry)
            else:
                retry[0] = 0

    except Exception as e:
        return GetErrorMessage(e)
        # print(f"Chat.ONE | Error querying model: {str(e)}")
