start_answer = '''
View all tables: /tables
Roll the dice on one of them: /roll {Table}
Show entire table: /show {Table}
Show all tags: /tags
Search tables by tags: /tag {Tag}
Show only tables with certain tag: /sort {Tag}
'''

def send_all_tables(json_list):
    text = ''
    for jl in json_list:
        tags = ''
        for tag in jl['tags']:
            tags += f"{tag['name']}, "

        text += f"{jl['name']}[{tags[:-2]}] - {jl['desc']}\n\n"
    return text
