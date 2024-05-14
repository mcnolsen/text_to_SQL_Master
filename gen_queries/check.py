import json
import os

def count_json_objects(directory):
    total_objects = 0
    for file in os.listdir(directory):
        if file.endswith('.json'):
            with open(os.path.join(directory, file), 'r') as json_file:
                data = json.load(json_file)
                # Check if data is a list (assuming each item in the list is an object)
                if isinstance(data, list):
                    total_objects += len(data)
                # If the data is a dictionary (single object), just add 1 to the count
                elif isinstance(data, dict):
                    total_objects += 1
                else:
                    # If the data is neither a list nor a dictionary, you might want to handle it differently
                    print(f"File {file} contains data that is not a list or dict.")
    
    return total_objects

# Example usage
directory = './'
total_objects = count_json_objects(directory)
print(f"Total number of objects in JSON files: {total_objects}")