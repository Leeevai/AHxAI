import json
import requests
import requests
from urllib.parse import quote_plus

def get_docs(base_url: str, topic: str, tokens: int = 5_000) -> str:

    topic = quote_plus(topic)

    url = f"{base_url}/llms.txt?topic={topic}&tokens={tokens}"

    response = requests.get(url)

    if response.status_code == 200:
        llms_text_data = response.text
    else:
        llms_text_data = f"Failed to fetch data. Status code: {response.status_code}"

    return llms_text_data

# def get_docs(url: str) -> str:
#     response = requests.get(url)

#     if response.status_code == 200:
#         llms_text_data = response.text
#     else:
#         llms_text_data = f"Failed to fetch data. Status code: {response.status_code}"

#     delimiter = "----------------------------------------"

#     doc_list = list(map(lambda x: x.strip(), llms_text_data.split(delimiter)))
    
#     return doc_list

def pretty_print_dict(d: dict) -> None:
    print(json.dumps(d, indent=4, sort_keys=False))

def parse_snippet(text: str) -> dict:
    sections = {
        "TITLE": "",
        "DESCRIPTION": "",
        "SOURCE": "",
        "LANGUAGE": "",
        "CODE": ""
    }

    lines = text.strip().splitlines()
    current_key = None
    code_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("TITLE:"):
            current_key = "TITLE"
            sections["TITLE"] = stripped[len("TITLE:"):].strip()
        elif stripped.startswith("DESCRIPTION:"):
            current_key = "DESCRIPTION"
            sections["DESCRIPTION"] = stripped[len("DESCRIPTION:"):].strip()
        elif stripped.startswith("SOURCE:"):
            current_key = "SOURCE"
            sections["SOURCE"] = stripped[len("SOURCE:"):].strip()
        elif stripped.startswith("LANGUAGE:"):
            current_key = "LANGUAGE"
            sections["LANGUAGE"] = stripped[len("LANGUAGE:"):].strip()
        elif stripped.startswith("CODE:"):
            current_key = "CODE"
            # Expect code block to follow in triple backticks, skip this line
            continue
        elif stripped.startswith("```") and current_key == "CODE":
            # Toggle code block start/end
            if code_lines:
                break  # We've finished collecting code
            else:
                continue
        elif current_key == "CODE":
            code_lines.append(line)

    sections["CODE"] = "\n".join(code_lines)
    return sections
