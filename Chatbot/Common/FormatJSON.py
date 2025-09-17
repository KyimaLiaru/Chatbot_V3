# Function for extracting keys from the JSON API result
def extractJsonKeys(json):
    key_list = []
    i = 0

    def extract(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_list.append(k)
                if isinstance(v, (dict, list)):
                    extract(v)
        elif isinstance(obj, list):
            if obj:
                extract(obj[0])

    extract(json)
    # print(f"Key List: {key_list}")
    return key_list


# Function for re-formatting the JSON API result
def formatJson(data, keys, indent=0, idx_ref=[0], count=[0], lang="en"):
    # indent: used for adding indents at the front of each line
    # idx_ref: used for saving starting indexes of Array items
    space = "  " * indent
    lines = []

    if isinstance(data, dict):
        for k, v in data.items():
            label = keys[idx_ref[0]] if idx_ref[0] < len(keys) else k
            idx_ref[0] += 1

            if isinstance(v, (dict, list)):
                lines.append(f"{space}- {label}:")
                lines.extend(formatJson(v, keys, indent + 1, idx_ref, count))
            else:
                if isinstance(v, str) and len(v) > 30:
                    if lang == "Korean":
                        text = "... (생략됨)."
                    else:
                        text = "... (truncated)."
                    lines.append(f"{space}- {label}: {v[:30] + text}")
                    continue
                lines.append(f"{space}- {label}: {v}")

    elif isinstance(data, list):
        length = len(data)
        start_idx = idx_ref[0] # Save the starting index of Array items
        for i, item in enumerate(data, start=1):
            count[0] += 1
            lines.append(f"{space}{i}.")
            lines.extend(formatJson(item, keys, indent+1, idx_ref, count))
            if count[0] == length:
                count[0] = 0
            elif i < len(data):
                idx_ref[0] = start_idx  # Return to the starting index of Array key

    return lines
