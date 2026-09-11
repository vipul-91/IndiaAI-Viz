import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://indiaai.gov.in/people/all"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
              "q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# inspect the page and adjust these selectors based on the site's structure
people = soup.select("div.some-person-container")
data = []
for person in people:
    name_el = person.select_one("h4")
    role_el = person.select_one(".role")
    comp_el = person.select_one(".company")
    if name_el and role_el and comp_el:
        data.append({
            "Name": name_el.get_text(strip=True),
            "Role": role_el.get_text(strip=True),
            "Company": comp_el.get_text(strip=True)
        })
        time.sleep(0.2)  # optional delay to reduce server strain

df = pd.DataFrame(data)
df.to_excel("indiaai_people.xlsx", index=False)
print(f"Extracted {len(df)} records.")