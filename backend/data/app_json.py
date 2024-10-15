import json
import hashlib
import random
import string

def generate_salt(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_hash(data, salt):
    string_to_hash = f"{data}-{salt}"
    hash_object = hashlib.sha256(string_to_hash.encode())
    return hash_object.hexdigest()

input_filename = 'data/error.json'
# input_filename = 'member.json'
with open(input_filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

processed_data = []
for entry in data:
    name = entry['name']
    email = entry['email']
    durations = entry['durations']
    projects = entry['projects']
    core_or_not = entry['core_or_not']

    data_to_store = {
        'name': name,
        'email': email,
        'durations': durations,
        'projects': [],
        'core_or_not': core_or_not,
        'salt': {},
        'hash': {}
    }

    for i, project in enumerate(projects, start=1):
        salt = generate_salt()
        hash_value = generate_hash(project, salt)
        data_to_store['projects'].append(project)
        data_to_store['salt'][f'salt_{i}'] = salt
        data_to_store['hash'][f'hash_{i}'] = hash_value

    core_salt = generate_salt()
    core_hash = generate_hash(str(core_or_not), core_salt)

    core_index = len(projects) + 1
    data_to_store['salt'][f'salt_{core_index}'] = core_salt
    data_to_store['hash'][f'hash_{core_index}'] = core_hash

    processed_data.append(data_to_store)

output_filename = 'data/error_output.json'
# output_filename = 'processed_data.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

print(f"Processed data saved to {output_filename}")
