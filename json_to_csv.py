import json
import csv

AUTHORS_JSON_PATH = '/Users/AB/Dropbox/Dev/CWP/authors.json'
NARRATIVES_JSON_PATH = '/Users/AB/Dropbox/Dev/CWP/narratives.json'

with open(AUTHORS_JSON_PATH, 'r') as f:
    authors = json.load(f)

with open(NARRATIVES_JSON_PATH, 'r') as f:
    narratives = json.load(f)

with open('narratives.csv', 'w') as csvfile:
    # fieldnames = ['id', 'name', 'model']
    fieldnames = ['id', 'author_id', 'name', 'year', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in narratives:
        row = {}
        # row['id'] = int(item['pk'])
        # row['name'] = item['fields']['name']
        # row['model'] = item['model']
        row['id'] = int(item['pk'])
        row['author_id'] = item['fields']['author_id']
        author = [x for x in authors if x['pk'] == row['author_id']][0]
        row['name'] = author['fields']['name']
        row['year'] = int(item['fields']['year'])
        row['text'] = item['fields']['text']

        writer.writerow(row)
