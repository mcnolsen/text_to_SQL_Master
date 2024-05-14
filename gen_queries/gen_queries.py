from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API")
instruction = """
Task:
Create a natural language query for a end-user looking to book a hotel. For each of these, note which combination of attributes can solve it. It should be based on the following schema:

SCHEMA:
Table Name: hotels\nid: Unique INT value identifying the hotel.\nname: Varchar, name of the hotel\nhotel_url: Varchar, url for the hotel.\ncountry: Varchar, the country in ISO 3166 Alpha2 format. For example 'DK' for Denmark and 'US' for the United States.\nstate: Varchar, the state name if any in English.\ncity: Varchar, the city name if any in English. For example 'Copenhagen'. If the city is in two words, the format is 'Los-Angeles'.\naddress: Varchar, the street address of the hotel. For example \"Guldblommevej 10, 4. th\".\nrating: Decimal(4,2), the average hotel review rating from customers over all of the reviews. Min 1 and max 10.\nreview_count: Int, the number of reviews of the hotel. Min: 0, median: 637, average: 1273, max: 33166\nstars: Smallint, the amount of stars for the hotel\nlat: Varchar, the latitude of the hotel\nlon: Varchar, the longitude of the hotel\nspa: tinyint, whether the hotel has spa or not. 1 if it does, and 0 if it does not.\nfitness_center: tinyint, whether the hotel has a fitness center or not. 1 if it does, and 0 if it does not.\npool: tinyint, whether the hotel has a pool or not. 1 if it does, and 0 if it does not.\nparking: enum('no', 'free', 'surcharge'), the availability and pricing for parking at the hotel.\nwifi: enum('no', 'free', 'surcharge'), the availability and pricing for wifi service at the hotel.\nbar: tinyint, whether the hotel has a bar or not. 1 if it does, and 0 if it does not.\ncribs: tinyint, whether cribs are available for small children. 1 if available, and 0 if not.\nrestaurant: tinyint, whether the hotel has a restaurant or not. 1 if it does, and 0 if it does not.\naircondition: tinyint, whether the hotel rooms are equipped with air conditioning. 1 if they are, and 0 if they are not.\nairport_shuttle: enum('no', 'possible', 'free'), the availability and pricing for airport shuttle service.\nwashing_and_drier: tinyint, whether the hotel offers laundry facilities such as washing machines and driers. 1 if it does, and 0 if it does not.\nev_charging_station: tinyint, whether the hotel has an electric vehicle charging station. 1 if it does, and 0 if it does not.\nocean_view: tinyint, whether the hotel offers rooms with an ocean view. 1 if it does, and 0 if it does not.\npet_friendly: enum('no pets', 'pets allowed on request'), the hotel policy on pets. If pets allowed, charges may apply.\ncasino: tinyint, whether the hotel has a casino. 1 if it does, and 0 if it does not.\nkitchen: tinyint, whether the hotel rooms include a kitchen. 1 if they do, and 0 if they do not.\nwater_park: tinyint, whether the hotel includes access to a water park. 1 if it does, and 0 if it does not.\nbeach_access: enum('no', 'private beach', 'beach access'), the type of beach access provided by the hotel.\ngolf: tinyint, whether the hotel has a golf course or golf facilities. 1 if it does, and 0 if it does not.\nadults_only: tinyint, whether the hotel is adults only or not. 1 if it is, and 0 if it is not.\nkids_friendly_buffet: tinyint, whether the hotel has a kids friendly buffet. 1 if it has, and 0 if it does not.\nchild_pool: tinyint, whether the hotel has a pool for children. 1 if it has, and 0 if it does not.\nplayground: tinyint, whether the hotel has a playground. 1 if it has, and 0 if it does not.\nincreased_accessibility: tinyint, whether the hotel advertises increased accessibility for people with a handicap. 1 if it does, and 0 if it does not.\nunit_wheelchair_accessible: tinyint, whether the entire unit is wheelchair accessible for people with a handicap. 1 if it is, and 0 if it is not.
Cities and countries available as values: 
Available Cities: Copenhagen, Aarhus, Roskilde, Odense, Aalborg, Skagen, Bornholm, Sonderborg, Ibiza-Island, Palma-de-Mallorca, Mallorca, Barcelona, Madrid, Malaga, Canary-Islands, Bilbao, Tenerife, Valencia, Algeciras, Alicante, Rome, Milan, Genoa, Venice, Palermo, Catania, Cagliari, Sassari, Paris, Bordeaux, Nice, Marseille, Corsica, French-Riviera, Monaco, Stockholm, Helsingborg, Gothenburg, Malmo, Kiruna, Visby, Oslo, Bergen, Trondheim, Stavanger, Tromso, Berlin, Munchen, Hamborg, Bremen, Stuttgart, Mannheim, Dresden, Athens, Mykonos, Thera, Thessaloniki, Chania, Corfu, Crete, Rhodes, Volos, London, Manchester, Edinburgh, Glasgow, Aberdeen, Liverpool, Southampton, Oxford, Cardiff, Swansea, Wrexham, Leicester, Belfast, Lisburn, Northern-Ireland, Wales, Scotland, Istanbul, Cappadocia, Antalya, Bodrum, Prague, Cesky-Krumlov, Carlsbad, Pilsen, Zurich, Basel, Geneve, Bern, Luzern, Vienna, Salzburg, Innsbruck, Hallstatt, Amsterdam, Rotterdam, Maastricht, Eindhoven, Cancun, Warsaw, Krakow, Gdansk, Poznan, Katowice, Lodz, Wroclaw, Dublin, Limerick, Cork, Reykjavik, Akureyri, Hafnarfjordur, Sydney, Melbourne, Brisbane, Perth, Adelaide, Gold-Coast, Cairns, Bangkok, Chiang-Mai, Phuket, Krabi, Koh-Samui, Ayutthaya, Kanchanaburi, Tokyo, Kyoto, Osaka, Hiroshima, Nagoya, Sapporo, Yokohama, Los-Angeles, Miami, Boston, Mumbai, Tulum, Mexico-City, Guadalajara, Playa-del-Carmen, Los-Cabos, La-Paz, San-Miguel-de-Allende, Puerto-Vallarta, Oaxaca, Senglea, Cospicua, Birgu, Porto, Madeira, Lisbon, Budapest, Lake-Balaton, Eger, Pecs, Debrecen, Szeged, Szentendre, Vilnius, Kaunas, Klaipda, Trakai, Brasilia, Rio-de-Janeiro, Florianopolis, Salvador, Sao-Paulo, Foz-do-Iguacu
Available Countries: DK, ES, IT, FR, MC, SE, NO, DE, GR, GB, TR, CZ, CH, AT, NL, MX, PL, IE, IS, AU, TH, JP, US, IN, MT, PT, HU, LT, BR

Levels of difficulty:
Low-level (simple): Exact match between 
Medium-level: When the LLM cannot direct match all of the words used in the query to attributes. Can be a low amount of filler. Can also use synonyms.
High level: When the LLM cannot direct match all of the words used in the query to attributes. Can be a varying amount of filler information. Can also use synonyms. 2 or more synonyms or interpretations for the LLM to figure out how to map to a SQL query. For example that small children means that it should search for cribs. SQL query answering this should still be based on the schema.

Answer format:
```json {"level_of_difficulty": "insert level of difficulty here","nl_query": "Insert natural language query here", "sql_query": "Insert sql query here", "combinations": [Insert combinations of values in arrays, that can answer the question]}```
"""

# open ai api key
api_key = OPENAI_KEY
open_ai_endpoint = "https://api.openai.com/v1"
model_name = 'gpt-4-0125-preview'

# A list to store the completions
completions = []


client = OpenAI(
    api_key=api_key
)

user_prompt = "Provide 3 queries of varying difficulty focusing on hotels in europe without mentioning anything about children or electric vehicle, focusing on activities. Do not comment on it, and provide raw JSON. One should be low-level, one medium-level, and one high-level. The high level should have 2 or more synonyms or interpretations for the LLM to figure out how to map to a SQL query. For example that small children means that it should search for cribs. SQL query answering this should still be based on the schema."


messages = [
    {
        "role": "system",
        "content": f"""{instruction}\n\n"""   
    },
    {"role": "user", "content": f"Provide one high level query."},
    {"role": "assistant", "content": f"""Since children who likes to swim can be answered with pool = 1 OR beach_access IN ('private beach', 'beach access') OR child_pool = 1, we add them in a list in the combinations, as each of these alone can satisfy the requirement.```json {{"level_of_difficulty": "high", "nl_query": "We are a family from spain with two children looking to drive to portugal, so we need a hotel. Our car is electric, and we would prefer a hotel that accomodates children who likes to swim, that is relatively cheap.", "sql_query": "SELECT * FROM hotels WHERE country = 'PT' AND (pool = 1 OR beach_access IN ('private beach', 'beach access') OR child_pool = 1) AND ev_charging_station = 1 AND stars <= 3;", "combinations": [["country = 1"], ["ev_charging_station = 1"], ["pool = 1", "beach_access IN ('private beach', 'beach access'", "child_pool = 1"], ["stars <= 3"]]}}```"""},
    {"role": "user", "content": f"Provide one medium level query."},
    {"role": "assistant", "content": """```json{"level_of_difficulty": "medium","nl_query": "I want a pet-friendly accommodation in Nice with a spot for my car.","sql_query": "SELECT * FROM hotels WHERE city = 'Nice' AND pet_friendly = 'pets allowed on request' AND parking != 'no';","combinations": [["city = 'Nice'"], ["pet_friendly = 'pets allowed on request'"], ["parking != 'no'"]]}```"""}
    , {"role": "user", "content": f"Provide one high level query."},
    {"role": "assistant", "content": """```json   {
    "level_of_difficulty": "high",
    "nl_query": "We are a couple looking for a romantic getaway in Cancun that allows us to bring our dog, has a private place for our car, and offers a cozy place to have drinks in the evening. A good internet connection is a must for a bit of work.",
    "sql_query": "SELECT * FROM hotels WHERE city = 'Cancun' AND pet_friendly = 'pets allowed on request' AND parking = 'free' AND bar = 1 AND wifi = 'free';",
    "combinations": [
      [
        "city = 'Cancun'"
      ],
      [
        "pet_friendly = 'pets allowed on request'"
      ],
      [
        "parking = 'free'"
      ],
      [
        "bar = 1"
      ],
      [
        "wifi = 'free'"
      ]
    ]
  }```"""},
    {
        "role": "user", 
        "content": f"{user_prompt}"
    }
]

for i in range(10):
    chat_completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=1000,
            temperature=1,
            stop=["<|im_end|>"]
        )

    # The content returned by the completion
    completion_content = chat_completion.choices[0].message.content
    print(completion_content)

    # Extract JSON blocks
    json_blocks = re.findall(r"```json\s+(.*?)\s+```", completion_content, re.DOTALL)

    # Parse and print each JSON block
    for block in json_blocks:
        try:
            json_data = json.loads(block)
            completions.append(json_data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    messages.append({"role": "assistant", "content": completion_content})
    messages.append({"role": "user", "content": user_prompt})

# Save the completions to a file
with open("completions.json", "w") as f:
    json.dump(completions, f, indent=2)



