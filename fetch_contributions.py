import requests
import json

GITHUB_USERNAME = "Vlor999"

GRAPHQL_URL = "https://api.github.com/graphql"

query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
""" % GITHUB_USERNAME

headers = {
    "Authorization": f"Bearer {TOKEN_GH}",
    "Content-Type": "application/json",
}

response = requests.post(GRAPHQL_URL, json={"query": query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    with open("contributions.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Données de contributions sauvegardées !")
else:
    print(f"❌ Erreur : {response.status_code}, {response.text}")
