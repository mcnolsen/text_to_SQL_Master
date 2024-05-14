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

cursor = db.cursor(dictionary=True)

def list_json_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

# For each json file in the cleaned directory, run the queries and save the results in a folder called model_results, and a subfolder for each query
json_files = list_json_files('../proto_5/cleaned/')


def execute_query(query):
    try:
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()
    except Exception as e:
        results = [{'name':'Failed to execute query.'}]
    return results

if __name__ == "__main__":
    json_files = list_json_files('../proto_4/cleaned/')
    for file_path in json_files:
        with open(file_path, 'r') as json_file:
            queries = json.load(json_file)

        # Only do the first 30 queries. We do not want to drop the database
        for index, query in enumerate(queries):
            results = execute_query(query)
            # Save the results to a JSON file, using the custom encoder. The file name is the same as the input file, but in the model_results directory
            # Split the file name and extension
            file_name_without_extension, extension = os.path.splitext(os.path.basename(file_path))

            # Ensure the directory exists
            os.makedirs(f'model_results/{file_name_without_extension}', exist_ok=True)
            with open(f'model_results/{file_name_without_extension}/{index}.json', 'w') as f:
                json.dump(results, f, cls=DecimalEncoder, indent=4)