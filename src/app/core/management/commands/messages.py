start_answer = '''
View all tables: /tables
Roll the dice on one of them: /roll {Table}
Show entire table: /show {Table}
Search tables by keyword: /search {Keyword}
'''

def send_all_tables(json_list):
    text = ''
    for jl in json_list:
        text += f"{jl['name']}. {jl['desc']}\n\n"
    return text