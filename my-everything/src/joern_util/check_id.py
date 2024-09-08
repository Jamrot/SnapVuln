import os
import re


filepath = '/app/slicing-snapvuln/pkcs12_gen_mac.dot'
ids = []
duplicated_ids = []
# match node_id
with open(filepath, 'r') as f:
    lines = f.readlines()
    for line in lines:
        match = re.search(r' nodeid=(\d+) ', line)
        if match:
            match_id = match.group(1)
            if match_id in ids:
                duplicated_ids.append(match_id)
            ids.append(match_id)


for i in range(5537809, 5537809+1000):
    if str(i) not in ids:
        print(i)
        print(duplicated_ids)
        print(len(duplicated_ids))
        print(len(ids))
        break