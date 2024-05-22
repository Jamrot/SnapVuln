origin_list = ['mac', 'ctx', 'salt', 'p12', 'md_type', 'macoid', 'md', 'impl', 'pass', 'hmac', 'key', 'pkcs12_key_gen', 'macalg', 'maclen']
my_list = ['ctx', 'HMAC_CTX', 'mac', 'p12', 'pass', 'impl', 'maclen', 'salt', 'hmac', 'pkcs12_key_gen', 'macalg', 'key', 'md', 'md_type', 'macoid']

# check items in both lists
for item in origin_list:
    if item not in my_list:
        print("origin_list:", item)

# check items in my_list but not in origin_list
for item in my_list:
    if item not in origin_list:
        print("my_list:", item)

