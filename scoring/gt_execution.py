import json
import os
import mysql.connector
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')

# Custom JSON Encoder that converts Decimal to str
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)

# Connect to the MySQL database
db = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_DATABASE,
)

# Load the first queries
with open('gt.json', 'r') as json_file:
    gt = []
    queries = json.load(json_file)
    for query in queries:
        gt.append(query['sql_queries'])

# Load the remaining queries
with open('../merge_queries.json', 'r') as json_file:
    gt_remaining = json.load(json_file)

    for query in gt_remaining:
        gt.append(query['sql_queries'])

cursor = db.cursor(dictionary=True)

for gt_index, gt_list in enumerate(gt):
    for query_index, query in enumerate(gt_list):
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()

        # Ensure the directory exists
        os.makedirs('gt_results', exist_ok=True)
        os.makedirs(f'gt_results/{gt_index}', exist_ok=True)
        
        # Save the results to a JSON file, using the custom encoder
        with open(f'gt_results/{gt_index}/{query_index}.json', 'w') as f:
            json.dump(results, f, cls=DecimalEncoder, indent=4)

cursor.close()