import re
import json
import os
def adjust_query_values(query, column_rules, general_rules):
    """
    Adjust specific values in the SQL query based on the provided column rules, apply general rules such as removing LIMIT and everything after it if specified,
    and ensure the query ends with a semicolon.
    
    :param query: The original SQL query.
    :param column_rules: A dictionary of rules for adjusting specific column values.
                         Each rule consists of a column name, a range of values to adjust, and the target value to set.
                         Example: {'review_count': {'range': (100, 1000), 'target': 100}}
    :param general_rules: A dictionary of general adjustment rules for the query, such as removing LIMIT and everything after.
                          Example: {'remove_limit_and_after': True}
    :return: The adjusted SQL query.
    """
    # Apply column adjustments
    for column, rules in column_rules.items():
        pattern = fr"({column}\s*>\s*=?\s*)(\d+)"
        
        def replacement_func(match):
            value = int(match.group(2))
            if rules['range'][0] <= value <= rules['range'][1]:
                return f"{match.group(1)}{rules['target']}"
            return match.group(0)

        query = re.sub(pattern, replacement_func, query, flags=re.IGNORECASE)

    # Apply general adjustments
    if general_rules.get('remove_limit_and_after', False):
        query = re.sub(r"\sLIMIT\s+.+$", ";", query, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove ORDER BY RAND() until the LIMIT
    if general_rules.get('remove_order_by_rand', False):
        query = re.sub(r"\sORDER BY\sRAND\(\)\sLIMIT", " LIMIT", query, flags=re.IGNORECASE)

    # Ensure the query ends with a semicolon
    if not query.strip().endswith(';'):
        query += ';'

    return query

# Load configurations from another JSON file
with open('query_configurations.json', 'r') as config_file:
    query_configs = json.load(config_file)


def process_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json") and filename != 'query_configurations.json':
            full_path = os.path.join(directory_path, filename)
            with open(full_path, 'r') as queries_file:
                queries = json.load(queries_file)
            
            # Process each query using the provided configurations
            adjusted_queries = []
            for index, query in enumerate(queries):
                column_rules = query_configs.get(str(index), {}).get('column_rules', {})
                general_rules = query_configs.get(str(index), {}).get('general_rules', {})
                adjusted_query = adjust_query_values(query, column_rules, general_rules)
                adjusted_queries.append(adjusted_query)
            
            # Save the adjusted queries to a new file
            modified_filename = os.path.splitext(full_path)[0] + "_semantic.json"
            with open(modified_filename, 'w') as output_file:
                json.dump(adjusted_queries, output_file, indent=4)

# Specify the directory containing your JSON files
directory_path = '../proto_3/cleaned'
process_files_in_directory(directory_path)


