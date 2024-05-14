import json
import os 
import re
def get_sql_result(sql_query):
    # Remove SQL comments
    sql_query_lines = sql_query.split('\n')
    cleaned_lines = []
    for line in sql_query_lines:
        comment_start = line.find('--')
        if comment_start != -1:
            line = line[:comment_start]
        cleaned_lines.append(line)
    sql_query = '\n'.join(cleaned_lines)

    # If ``` sql is present, use only the sql part
    if '```sql' in sql_query:
        sql_query = sql_query.split('```sql')[1]
        # Nested, since we only want to remove it, if ```sql is present. Otherwise, it might be part of the query, however that is very unlikely
        if '```' in sql_query:
            sql_query = sql_query.split('```')[0]

    # Preprocessing to remove everything before the first SELECT
    sql_query = sql_query.replace('select', '')
    first_select_index = sql_query.upper().find("SELECT")
    if first_select_index > -1:
        sql_query = sql_query[first_select_index:]
    else:
        print("No SELECT found in query.")
    
        # Remove everything after **Note
    if '\n\n' in sql_query:
        sql_query = sql_query.split('\n\n')[0]

    
    sql_query = sql_query.replace('"', '')
    sql_query = sql_query.replace('[', '', 1)  # Only replace the first occurrence
    sql_query = sql_query.replace(']', '', 1)  # Only replace the first occurrence
    # sql_query = sql_query.lower()
    sql_query = sql_query.replace('\\', '') # Remove escape characters

    
    # sql_query = sql_query.replace('--', '')
    sql_query = sql_query.replace('\n', ' ')  # Replace all newline characters with a single space
    sql_query = sql_query.split(';')[0] + ';'  # Keep everything before the first semicolon and add semicolon back
    sql_query = sql_query.replace('```', '')
    sql_query = ' '.join(sql_query.split())
    
    # If space before ; remove it
    if ' ;' in sql_query:
        sql_query = sql_query.replace(' ;', ';')
    return sql_query


def get_queries():
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
    directory = os.path.join(current_dir, "..", "proto_2")  # Path to the proto_1 directory
    cleaned_directory = os.path.join(directory, "cleaned")  # Path to the cleaned directory

    # Check if the cleaned directory exists, if not create it
    if not os.path.exists(cleaned_directory):
        os.makedirs(cleaned_directory)

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            target_file = os.path.join(directory, filename)
            with open(target_file, "r") as f:
                data = json.load(f)
                results = [get_sql_result(query) for query in data]

            # Construct the output filename by adding '_cleaned' before the '.json' extension
            output_filename = filename.rsplit('.', 1)[0] + '_cleaned.json'
            output_file_path = os.path.join(cleaned_directory, output_filename)

            # Write the results to the output file in the cleaned folder
            with open(output_file_path, "w") as f_out:
                json.dump(results, f_out, indent=4)

if __name__ == "__main__":
    get_queries()