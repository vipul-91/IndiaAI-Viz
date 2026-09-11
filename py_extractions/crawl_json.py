import json
import pandas as pd

# Load the JSON file
with open("people.json", "r") as f:
    people_data = json.load(f)["data"]

def get_nested_value(d, keys, default=""):
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d if d is not None else default

records = []
records_with_content = []

for idx, person in enumerate(people_data, start=1):
    # Fix LinkedIn URL
    linkedin = person.get("linkedIn", "")
    if linkedin and not linkedin.startswith("http"):
        linkedin = "https://www." + linkedin.lstrip("/")

    # Fix Twitter URL
    twitter = person.get("twitter", "")
    if twitter and not twitter.startswith("http"):
        twitter = "https://www." + twitter.lstrip("/")

    # Clean excerpt/content/highlights in fallback order
    excerpt = person.get("excerpt")
    content = person.get("content")
    highlights = person.get("highlights")

    if excerpt:
        cleaned_excerpt = " ".join(excerpt.split())
    elif content:
        cleaned_excerpt = " ".join(content.split())
    elif highlights:
        cleaned_excerpt = " ".join(highlights.split())
    else:
        cleaned_excerpt = ""

    record = {
        "No.": idx,
        "people": person.get("title", ""),
        "designation": person.get("author_designation", ""),
        "company": person.get("author_description", ""),
        "category": person.get("head_category", ""),
        "country": get_nested_value(person, ["country", "name"]),
        "linkedIn": linkedin,
        "twitter": twitter,
        "feature-1": "",
        "feature-2": "",
        "category-1": "",
        "category-2": "",
        "category-3": "",
        "excerpt": cleaned_excerpt,
    }

    # Collect up to 2 featured tags
    featured_tags = person.get("featured_tags", [])
    for i in range(min(2, len(featured_tags))):
        record[f"feature-{i+1}"] = featured_tags[i].get("name", "")

    # Collect up to 3 categories
    categories = person.get("categories", [])
    for i in range(min(3, len(categories))):
        record[f"category-{i+1}"] = categories[i].get("name", "")

    records.append(record)

    # Save separately if original content or highlights exist
    if content or highlights:
        records_with_content.append(record)

# Save all entries
df_all = pd.DataFrame(records)
df_all.to_excel("indiaai_people_cleaned.xlsx", index=False)

# Save filtered entries with content/highlights
df_content = pd.DataFrame(records_with_content)
df_content.to_excel("indiaai_people_with_content_only.xlsx", index=False)

print("✔ Saved:")
print("- Full: indiaai_people_cleaned.xlsx")
print("- Filtered (content or highlights): indiaai_people_with_content_only.xlsx")