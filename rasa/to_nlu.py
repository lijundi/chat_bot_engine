# @Time : 2020/4/7 13:37 
# @Author : lijundi
# @File : to_nlu.py
# @Software: PyCharm
import json
import os

nlu = {
    'rasa_nlu_data': {
        'regex_features': [],
        'lookup_tables': [],
        'entity_synonyms': []
        # 'common_examples': [
        #     dict(intent="greet", text="hey"),
        #     dict(intent="greet", text="hello"),
        #     dict(intent="inform", entities=[
        #         dict(start=7, end=11, value="9:00", entity="time")
        #     ], text="now is 9:00"),
        # ]
    }
}


def get_examples(mysql, skl_id):
    examples = list()
    nlu_sql = 'select text, iten_name, text_id from nludata where (status = 1 or status = 2) and skl_id = ' + str(skl_id)
    nlu_results = mysql.inquire_all(nlu_sql)
    for item in nlu_results:
        nlu_slot_sql = 'select start, end, word, slot_name from nludata_slot where text_id = ' + str(item[2])
        nlu_slot_results = mysql.inquire_all(nlu_slot_sql)
        ns_list = list()
        for nsr in nlu_slot_results:
            ns = dict(start=nsr[0], end=nsr[1], value=nsr[2], entity=nsr[3])
            ns_list.append(ns)
        ex = dict(intent=item[1], text=item[0])
        if ns_list:
            ex['entities'] = ns_list
        examples.append(ex)
    print(examples)
    return examples


def to_nlu(mysql, path, skl_id):
    nlu['rasa_nlu_data']['common_examples'] = get_examples(mysql, skl_id)
    json_str = json.dumps(nlu, indent=4)
    nlu_path = os.path.join(path, 'data', 'nlu.json')
    with open(nlu_path, 'w', encoding='utf8') as json_file:
        json_file.write(json_str)

