start_answer = '''
View all tables: /tables
Roll the dice on one of them: /roll {Table}
Show entire table: /show {Table}
Show all tags: /tags
Search tables by tag: /tag {Tag}
'''

def send_all_tables(json_list):
    text = ''
    for jl in json_list:
        tags = ''
        for tag in jl['tags']:
            tags += f"{tag['name']}, "

        text += f"{jl['name']}[{tags[:-2]}] - {jl['desc']}\n\n"
    return text

def send_table_by_tag(json_list):
    text = ''
    for jl in json_list:
        text += f"{jl['name']} - {jl['desc']}\n\n"

    return text

def send_full_table(json_list):
    m_list = []
    text = f"{json_list['name']}:\n"

    for entry in json_list['entries']:
        text += f"- {entry}\n"
        print(len(text))
        if len(text) >= 2000:
            m_list.append(text)
            text = ''

    m_list.append(text)
    return m_list

def send_all_tags(json_list):
    text = ''
    for jl in json_list:
        text += f"{jl['name']}\n"

    return text