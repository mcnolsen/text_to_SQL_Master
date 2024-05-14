import json
import csv

# Function to read JSON content
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to get the base file name to match entries between files
def get_base_file_name(file_path):
    return file_path.split('/')[-1]

# Convert decimal points to commas for numerical values except the 'file' field
def convert_decimal_to_comma(entry):
    for key, value in entry.items():
        if isinstance(value, float) and key != 'file':
            entry[key] = str(value).replace('.', ',')
    return entry

paths = []

for n in range(1, 6):
    file_one = f'../proto_{n}/eval_results/results_{n}.json'
    file_two = f'../proto_{n}/eval_results/best_results.json'
    paths.append((file_one, file_two))

fieldnames = ['file', 'bleu', 'sqam', 'bleuLow', 'bleuMedium', 'bleuHigh', 'sqamLow', 'sqamMedium', 'sqamHigh', 'aggregate_precision', 'low_aggregate_precision', 'medium_aggregate_precision', 'high_aggregate_precision', 'aggregate_recall', 'low_aggregate_recall', 'medium_aggregate_recall', 'high_aggregate_recall', 'aggregate_execution_accuracy', 'low_aggregate_execution_accuracy', 'medium_aggregate_execution_accuracy', 'high_aggregate_execution_accuracy', 'aggregate_f1', 'low_aggregate_f1', 'medium_aggregate_f1', 'high_aggregate_f1']

for index, (path_one, path_two) in enumerate(paths, start=1):
    data_one = read_json(path_one)
    data_two = read_json(path_two)
    
    combined_data = []
    for entry_one in data_one:
        for entry_two in data_two:
            if get_base_file_name(entry_one['file']) == get_base_file_name(entry_two['file']):
                combined_entry = {
                    'file': get_base_file_name(entry_one['file']),  # Adjust the 'file' entry here
                    'bleu': entry_one['bleu'],
                    'sqam': entry_one['sqam'],
                    'bleuLow': entry_one['bleuLow'],
                    'bleuMedium': entry_one['bleuMedium'],
                    'bleuHigh': entry_one['bleuHigh'],
                    'sqamLow': entry_one['sqamLow'],
                    'sqamMedium': entry_one['sqamMedium'],
                    'sqamHigh': entry_one['sqamHigh'],
                    'aggregate_precision': entry_two['aggregate_precision'],
                    'low_aggregate_precision': entry_two['low_aggregate_precision'],
                    'medium_aggregate_precision': entry_two['medium_aggregate_precision'],
                    'high_aggregate_precision': entry_two['high_aggregate_precision'],
                    'aggregate_recall': entry_two['aggregate_recall'],
                    'low_aggregate_recall': entry_two['low_aggregate_recall'],
                    'medium_aggregate_recall': entry_two['medium_aggregate_recall'],
                    'high_aggregate_recall': entry_two['high_aggregate_recall'],
                    'aggregate_execution_accuracy': entry_two['aggregate_execution_accuracy'],
                    'low_aggregate_execution_accuracy': entry_two['low_aggregate_execution_accuracy'],
                    'medium_aggregate_execution_accuracy': entry_two['medium_aggregate_execution_accuracy'],
                    'high_aggregate_execution_accuracy': entry_two['high_aggregate_execution_accuracy'],
                    'aggregate_f1': entry_two['aggregate_f1'],
                    'low_aggregate_f1': entry_two['low_aggregate_f1'],
                    'medium_aggregate_f1': entry_two['medium_aggregate_f1'],
                    'high_aggregate_f1': entry_two['high_aggregate_f1'],
                }
                combined_data.append(convert_decimal_to_comma(combined_entry))
    
    # Write the combined data to a separate CSV file for each pair using semicolon as delimiter
    csv_file_name = f'combined_data_proto_{index}.csv'
    with open(csv_file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"{csv_file_name} created successfully.")
