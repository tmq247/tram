import os
import yaml
from typing import List

languages = {}
languages_present = {}

def get_string(lang: str):
    return languages.get(lang)

lang_dir = r"./strings/langs/"
with open(os.path.join(lang_dir, "vn.yml"), encoding="utf8") as file:
    languages["vn"] = yaml.safe_load(file)
    languages_present["vn"] = languages["vn"]["name"]

for filename in os.listdir(lang_dir):
    if filename.endswith(".yml") and filename != "vn.yml":
        language_name = filename[:-4]
        file_path = os.path.join(lang_dir, filename)
        try:
            with open(file_path, encoding="utf8") as file:
                languages[language_name] = yaml.safe_load(file)
            for item in languages["vn"]:
                if item not in languages[language_name]:
                    languages[language_name][item] = languages["vn"][item]
            languages_present[language_name] = languages[language_name]["name"]
        except KeyError as e:
            print(f"Missing 'name' key in {filename}. Error: {e}")
            exit(1)
        except Exception as e:
            print(f"Error loading language file {filename}: {e}")
            exit(1)
