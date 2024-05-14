# If necessary, install the openai Python library by running 
# pip install openai

from openai import OpenAI
import json
from transformers import AutoTokenizer
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API = os.getenv("OPENAI_API")
HF_TOKEN = os.getenv("HF_TOKEN")

# Load the prompts from the queries.txt file
with open("queries.txt", "r") as f:
    prompts = f.readlines()

# Get the queries from the queries.json file
with open("merge_queries.json", "r") as f:
    queries = json.load(f)

    for query in queries:
        prompts.append(query["nl_query"])

prompts_sec = []
# Get security queries from the queries_security.json. Each value is stored in a json object with the key "query"
with open("queries_security.json", "r") as f:
    security_queries = json.load(f)

    for query in security_queries:
        prompts.append(query["query"])
        prompts_sec.append(query["query"])

# A list to store the completions
completions = []
completions_sec = []


# open ai api key
api_key = OPENAI_API
open_ai_endpoint = "https://api.openai.com/v1"
model_name = 'gpt-4-0125-preview'


client = OpenAI(
    api_key=api_key
)


ONE_SHOT_PROMPT = """What are the highest rated hotels in Australia?"""
ONE_SHOT_ANSWER = """We divide the question into sub elements, and match them to known SQL columns or functions. Highest rated hotels, so: ORDER BY rating. Wants to travel to Australia, so: country = 'AU'. Therefore, the SQL statement answer is: SELECT * FROM hotels WHERE country = 'AU' ORDER BY rating DESC;""" 

TWO_SHOT_PROMPT = """We are a family from spain with two children looking to drive to portugal, so we need a hotel. Our car is electric, and we would prefer a hotel that accomodates children who likes to swim, that is relatively cheap."""
TWO_SHOT_ANSWER = """We divide the question into sub elements, and match them to known SQL columns or functions. They want to travel to Portugal, so: country = 'PT'. Driving and car is electric, so: ev_charging_station = 1. Children who likes to swim, so: pool = 1 OR beach_access IN ('private beach', 'beach access') OR child_pool = 1. Relatively cheap: stars <= 3. Therefore, the SQL statement answer is: SELECT * FROM hotels WHERE country = 'PT' AND (pool = 1 OR beach_access IN ('private beach', 'beach access') OR child_pool = 1) AND ev_charging_station = 1 AND stars <= 3;"""

THREE_SHOT_PROMPT = """We are a group of friends looking for places in India with a pool, a kitchen and has good reviews."""
THREE_SHOT_ANSWER = """We divide the question into sub elements, and match them to known SQL columns or functions. Looking for places in India, so: country = 'IN'. With a pool, so: pool = 1. Needs to have a kitchen, so: kitchen = 1. Needs to have good reviews, so: rating >= 8 AND review_count >= 20. Therefore, the SQL statement answer is: SELECT * FROM hotels WHERE country = 'IN' AND pool = 1 AND kitchen = 1 AND rating >= 7 AND review_count >= 20;"""



system_instruct = """Based on the provided SQL table schema and question below, return a single SQL SELECT * query that will answer the user's question, and that is compatible with MySQL. Return only the raw SQL SELECT statement needed to answer the question, and NOTHING else. Do not explain your choices, or include comments in the SQL QUERY response. Always end the SQL response with ";", and always do SELECT *. Do not attempt to query columns or tables not listed in the schema. The available countries and cities are listed below. Do not use countries or cities that are not listed below."""
system_prompt = f"""{system_instruct}\n\n------------\nSCHEMA: \nTable Name: hotels\nid: Unique INT value identifying the hotel.\nname: Varchar, name of the hotel\nhotel_url: Varchar, url for the hotel.\ncountry: Varchar, the country in ISO 3166 Alpha2 format. For example 'DK' for Denmark and 'US' for the United States.\nstate: Varchar, the state name if any in English.\ncity: Varchar, the city name if any in English. For example 'Copenhagen'. If the city is in two words, the format is 'Los-Angeles'.\naddress: Varchar, the street address of the hotel. For example \"Guldblommevej 10, 4. th\".\nrating: Decimal(4,2), the average hotel review rating from customers over all of the reviews. Min 1 and max 10.\nreview_count: Int, the number of reviews of the hotel. Min: 0, median: 637, average: 1273, max: 33166\nstars: Smallint, the amount of stars for the hotel\ndescription: Text, the description of the hotel by the hotel itself. Often includes some of the amenities, and can also include if it is close to landmarks or other locations.\nlat: Varchar, the latitude of the hotel\nlon: Varchar, the longitude of the hotel\nspa: tinyint, whether the hotel has spa or not. 1 if it does, and 0 if it does not.\nfitness_center: tinyint, whether the hotel has a fitness center or not. 1 if it does, and 0 if it does not.\npool: tinyint, whether the hotel has a pool or not. 1 if it does, and 0 if it does not.\nparking: enum('no', 'free', 'surcharge'), the availability and pricing for parking at the hotel.\nwifi: enum('no', 'free', 'surcharge'), the availability and pricing for wifi service at the hotel.\nbar: tinyint, whether the hotel has a bar or not. 1 if it does, and 0 if it does not.\ncribs: tinyint, whether cribs are available for small children. 1 if available, and 0 if not.\nrestaurant: tinyint, whether the hotel has a restaurant or not. 1 if it does, and 0 if it does not.\naircondition: tinyint, whether the hotel rooms are equipped with air conditioning. 1 if they are, and 0 if they are not.\nairport_shuttle: enum('no', 'possible', 'free'), the availability and pricing for airport shuttle service.\nwashing_and_drier: tinyint, whether the hotel offers laundry facilities such as washing machines and driers. 1 if it does, and 0 if it does not.\nev_charging_station: tinyint, whether the hotel has an electric vehicle charging station. 1 if it does, and 0 if it does not.\nocean_view: tinyint, whether the hotel offers rooms with an ocean view. 1 if it does, and 0 if it does not.\npet_friendly: enum('no pets', 'pets allowed on request'), the hotel policy on pets. If pets allowed, charges may apply.\ncasino: tinyint, whether the hotel has a casino. 1 if it does, and 0 if it does not.\nkitchen: tinyint, whether the hotel rooms include a kitchen. 1 if they do, and 0 if they do not.\nwater_park: tinyint, whether the hotel includes access to a water park. 1 if it does, and 0 if it does not.\nbeach_access: enum('no', 'private beach', 'beach access'), the type of beach access provided by the hotel.\ngolf: tinyint, whether the hotel has a golf course or golf facilities. 1 if it does, and 0 if it does not.\nadults_only: tinyint, whether the hotel is adults only or not. 1 if it is, and 0 if it is not.\nkids_friendly_buffet: tinyint, whether the hotel has a kids friendly buffet. 1 if it has, and 0 if it does not.\nchild_pool: tinyint, whether the hotel has a pool for children. 1 if it has, and 0 if it does not.\nplayground: tinyint, whether the hotel has a playground. 1 if it has, and 0 if it does not.\nincreased_accessibility: tinyint, whether the hotel advertises increased accessibility for people with a handicap. 1 if it does, and 0 if it does not.\nunit_wheelchair_accessible: tinyint, whether the entire unit is wheelchair accessible for people with a handicap. 1 if it is, and 0 if it is not.\n\n------------\nCities and countries available as values: ["Available Cities: Copenhagen, Aarhus, Roskilde, Odense, Aalborg, Skagen, Bornholm, Sonderborg, Ibiza-Island, Palma-de-Mallorca, Mallorca, Barcelona, Madrid, Malaga, Canary-Islands, Bilbao, Tenerife, Valencia, Algeciras, Alicante, Rome, Milan, Genoa, Venice, Palermo, Catania, Cagliari, Sassari, Paris, Bordeaux, Nice, Marseille, Corsica, French-Riviera, Monaco, Stockholm, Helsingborg, Gothenburg, Malmo, Kiruna, Visby, Oslo, Bergen, Trondheim, Stavanger, Tromso, Berlin, Munchen, Hamborg, Bremen, Stuttgart, Mannheim, Dresden, Athens, Mykonos, Thera, Thessaloniki, Chania, Corfu, Crete, Rhodes, Volos, London, Manchester, Edinburgh, Glasgow, Aberdeen, Liverpool, Southampton, Oxford, Cardiff, Swansea, Wrexham, Leicester, Belfast, Lisburn, Northern-Ireland, Wales, Scotland, Istanbul, Cappadocia, Antalya, Bodrum, Prague, Cesky-Krumlov, Carlsbad, Pilsen, Zurich, Basel, Geneve, Bern, Luzern, Vienna, Salzburg, Innsbruck, Hallstatt, Amsterdam, Rotterdam, Maastricht, Eindhoven, Cancun, Warsaw, Krakow, Gdansk, Poznan, Katowice, Lodz, Wroclaw, Dublin, Limerick, Cork, Reykjavik, Akureyri, Hafnarfjordur, Sydney, Melbourne, Brisbane, Perth, Adelaide, Gold-Coast, Cairns, Bangkok, Chiang-Mai, Phuket, Krabi, Koh-Samui, Ayutthaya, Kanchanaburi, Tokyo, Kyoto, Osaka, Hiroshima, Nagoya, Sapporo, Yokohama, Los-Angeles, Miami, Boston, Mumbai, Tulum, Mexico-City, Guadalajara, Playa-del-Carmen, Los-Cabos, La-Paz, San-Miguel-de-Allende, Puerto-Vallarta, Oaxaca, Senglea, Cospicua, Birgu, Porto, Madeira, Lisbon, Budapest, Lake-Balaton, Eger, Pecs, Debrecen, Szeged, Szentendre, Vilnius, Kaunas, Klaipda, Trakai, Brasilia, Rio-de-Janeiro, Florianopolis, Salvador, Sao-Paulo, Foz-do-Iguacu \nAvailable Countries: DK, ES, IT, FR, MC, SE, NO, DE, GR, GB, TR, CZ, CH, AT, NL, MX, PL, IE, IS, AU, TH, JP, US, IN, MT, PT, HU, LT, BR\"]"""
create_table_statement = """CREATE TABLE hotels (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(300),
	hotel_url VARCHAR(600),
	country VARCHAR(300) NOT NULL,
	state VARCHAR(300) DEFAULT 'Unknown',
	city VARCHAR(300) DEFAULT 'Unknown',
	address VARCHAR(500),
	rating DECIMAL(4,2),
	review_count INT,
	stars SMALLINT,
	description TEXT,
	lat VARCHAR(100),
	lon VARCHAR(100),
	spa tinyint DEFAULT 0,
	fitness_center tinyint DEFAULT 0,
	pool tinyint DEFAULT 0,
	parking ENUM('no', 'free', 'surcharge') DEFAULT 'no',
	wifi ENUM('no', 'free', 'surcharge') DEFAULT 'no',
	bar tinyint DEFAULT 0,
	cribs tinyint DEFAULT 0,
	restaurant tinyint DEFAULT 0,
	aircondition tinyint DEFAULT 0,
	airport_shuttle ENUM('no', 'possible', 'free') DEFAULT 'no',
	washing_and_drier tinyint DEFAULT 0,
	ev_charging_station tinyint DEFAULT 0,
	ocean_view tinyint DEFAULT 0,
	pet_friendly ENUM('no pets', 'pets allowed on request') DEFAULT 'no pets',
	casino tinyint DEFAULT 0,
	kitchen tinyint DEFAULT 0,
	water_park tinyint DEFAULT 0,
	beach_access ENUM('no', 'private beach', 'beach access') DEFAULT 'no',
	golf tinyint DEFAULT 0,
	adults_only tinyint DEFAULT 0, 
    kids_friendly_buffet tinyint DEFAULT 0, 
    child_pool tinyint DEFAULT 0, 
    playground tinyint DEFAULT 0, 
    increased_accessibility tinyint DEFAULT 0, 
    unit_wheelchair_accessible tinyint DEFAULT 0
)"""


# Start timer
start = time.time()

# Loop through the prompts and get the completions
for prompt in prompts:
    messages = [
            {
                "role": "system",
                "content": f"""{system_prompt}\n\n"""   
            },
            {
                "role": "user", 
                "content": f"QUESTION: {ONE_SHOT_PROMPT}"},
            {
                "role": "assistant",
                "content": ONE_SHOT_ANSWER
            },
            {
                "role": "user",
                "content": f"QUESTION: {TWO_SHOT_PROMPT}"
            },
            {
                "role": "assistant",
                "content": TWO_SHOT_ANSWER
            },
            {
                "role": "user",
                "content": f"QUESTION: {THREE_SHOT_PROMPT}"
            },
            {
                "role": "assistant",
                "content": THREE_SHOT_ANSWER
            },
            {
                "role": "user",
                "content": f"QUESTION: {prompt}"
            }
    ]
    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=1000,
        temperature=0.00,
        stop=["<|im_end|>", ";"]
    )

    print(chat_completion.choices[0].message.content)
    if prompt in prompts_sec:
        completions_sec.append(chat_completion.choices[0].message.content)
    else:
        # Add the output to the completions list
        completions.append(chat_completion.choices[0].message.content)

# Save the completions to a JSON file in the proto_1 directory
with open(f"./proto_4/completion_gpt.json", "w") as f:
    json.dump(completions, f, indent=4)

# Makes sure the directory exists
os.makedirs("./proto_4/security", exist_ok=True)

with open(f"./proto_4/security/completion_sec.json", "w") as f:
    json.dump(completions_sec, f, indent=4)

# End timer
end = time.time()
print(f"Time taken: {end - start} seconds")


