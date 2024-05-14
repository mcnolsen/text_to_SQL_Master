import os
import json
import itertools

# Assuming the path to the directory with JSON files
json_files_directory = './'

# Check if the directory exists and list all JSON files
if os.path.exists(json_files_directory):
    json_files = [f for f in os.listdir(json_files_directory) if f.endswith('.json')]
else:
    json_files = []

# Function to generate all possible SQL queries from combinations
def generate_all_possible_queries(combinations):
    # Generate all possible permutations for each group
    all_group_permutations = []
    for group in combinations:
        if len(group) > 1:
            # Generate all non-empty permutations of each group
            group_permutations = [f"({ ' OR '.join(permutation) })" for i in range(1, len(group)+1) for permutation in itertools.permutations(group, i)]
        else:
            group_permutations = group
        all_group_permutations.append(group_permutations)
    
    # Generate all combinations of group permutations
    all_combinations = list(itertools.product(*all_group_permutations))
    
    # Combine groups with ' AND ' to form full queries
    full_queries = ['SELECT * FROM hotels WHERE ' + ' AND '.join(combination) for combination in all_combinations]
    return full_queries

# Function to modify the SQL query structure and create combinations
def modify_sql_query_structure(file_path, directory):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    transformed_data = []

    for item in data:
        # Transform 'sql_query' into a list 'sql_queries' if not already a list
        if 'sql_query' in item:
            item['sql_queries'] = [item.pop('sql_query')]

        if 'combinations' in item:
            # Generate all possible SQL queries from combinations
            item['sql_queries'].extend(generate_all_possible_queries(item['combinations']))
            # Remove the 'combinations' key
            item.pop('combinations')

        transformed_data.append(item)

    # Ensure the finished directory exists
    finished_directory = os.path.join(directory, 'permutations')
    if not os.path.exists(finished_directory):
        os.makedirs(finished_directory)

    # Save the modified data back to the file
    with open(f'{finished_directory}/{os.path.basename(file_path)}', 'w', encoding='utf-8') as file:
        json.dump(transformed_data, file, indent=4)

# Apply the modification to each JSON file
for json_file in json_files:
    file_path = os.path.join(json_files_directory, json_file)
    modify_sql_query_structure(file_path, json_files_directory)
