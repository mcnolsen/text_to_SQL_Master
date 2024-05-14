from nltk.translate.bleu_score import sentence_bleu
from SQAM.sqam import sql_query_accuracy
import json
import os

difficulty = []
# Import the ground truths from the gt.json file
with open('gt.json', 'r') as json_file:
    gt = []
    queries = json.load(json_file)

    for query in queries:
        gt.append(query["sql_queries"])
        difficulty.append(query["level_of_difficulty"])

# Import the rest of the ground truths from the merge_queries.json file
with open('../merge_queries.json', 'r') as json_file:
    queries = json.load(json_file)

    for query in queries:
        gt.append(query["sql_queries"])
        difficulty.append(query["level_of_difficulty"])

def list_json_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

results = []
resultsLow = []
resultsMedium = []
resultsHigh = []

# Scoring function comparing cleaned predictions and the gt.json. There are more ground truth answers for each question, so we take the highest.
def score(predictions, gt):
    # Initialize scores
    bleu = 0
    bleuLow = 0
    bleuMedium = 0
    bleuHigh = 0
    sqam = 0
    sqamLow = 0
    sqamMedium = 0
    sqamHigh = 0

    # 30 because there are 30 questions, and the rest are the 'security' questions
    for i in range(len(gt)):
        # Initialize individual scores
        bleu_individual = 0
        sqam_individual = 0

        for j in range(len(gt[i])):
            current_bleu = sentence_bleu([gt[i][j]], predictions[i])
            current_sqam = sql_query_accuracy(gt[i][j], predictions[i])

            if current_bleu > bleu_individual:
                bleu_individual = current_bleu
            if current_sqam > sqam_individual:
                sqam_individual = current_sqam

        bleu += bleu_individual
        sqam += sqam_individual

        # Add the scores to the correct difficulty level
        if difficulty[i] == 'low':
            bleuLow += bleu_individual
            sqamLow += sqam_individual
        elif difficulty[i] == 'medium':
            bleuMedium += bleu_individual
            sqamMedium += sqam_individual
        elif difficulty[i] == 'high':
            bleuHigh += bleu_individual
            sqamHigh += sqam_individual
        

    # Average scores
    bleu /= len(predictions)
    sqam /= len(predictions)

    bleuLow /= difficulty.count('low')
    sqamLow /= difficulty.count('low')
    bleuMedium /= difficulty.count('medium')
    sqamMedium /= difficulty.count('medium')
    bleuHigh /= difficulty.count('high')
    sqamHigh /= difficulty.count('high')




    return bleu, sqam, bleuLow, sqamLow, bleuMedium, sqamMedium, bleuHigh, sqamHigh

# Change the number depending on the proto iteration to evaluation
proto_number = 4

if __name__ == "__main__":
    json_files = list_json_files(f'../proto_{proto_number}/cleaned/')
    for file_path in json_files:
        with open(file_path, 'r') as json_file:
            predictions = json.load(json_file)
        bleu, sqam, bleuLow, sqamLow, bleuMedium, sqamMedium, bleuHigh, sqamHigh = score(predictions, gt)

        # Add the results to the list
        results.append({
            'file': file_path,
            'bleu': bleu,
            'sqam': sqam,
            'bleuLow': bleuLow,
            'sqamLow': sqamLow,
            'bleuMedium': bleuMedium,
            'sqamMedium': sqamMedium,
            'bleuHigh': bleuHigh,
            'sqamHigh': sqamHigh
        })

        print(f"File: {file_path}, average BLEU: {bleu}, average SQAM: {sqam}, low BLEU: {bleuLow}, low SQAM: {sqamLow}, medium BLEU: {bleuMedium}, medium SQAM: {sqamMedium}, high BLEU: {bleuHigh}, high SQAM: {sqamHigh}")

# Output the results to a json file
results = sorted(results, key=lambda x: x['file'])

with open(f'results_{proto_number}.json', 'w') as f:
    json.dump(results, f, indent=4)
