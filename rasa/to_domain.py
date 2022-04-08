# @Time : 2020/3/31 19:25 
# @Author : lijundi
# @File : to_domain.py
# @Software: PyCharm
"""
intent_list = ['greet', 'goodbye', 'inform']
form_list = ['to_do_list_form']
entity_list = ['item', 'time']
slot_list = ['item', 'time']
action_list = ['utter_greet', 'utter_goodbye', 'utter_ask_item']
response_slot_list = [['utter_ask_who', 'who', '1,2,3'], ['utter_ask_where', 'where', '1,2,3']]
response_intent_list = [['utter_greet', 'hello', 'text'], ['utter_goodbye', 'bye', 'richText']]
"""
import os
from rasa.file_opt import format_write, response_format_write

session_opt = '\n\nsession_config:\n' \
              '    session_expiration_time: 60\n' \
              '    carry_over_slots_to_new_session: true\n\n'


def to_string_list(_list):
    string_list = []
    for i in _list:
        string_list.append(i[0])
    return string_list


def get_intents(mysql, skl_id):
    sql = 'select name from intent where skl_id = ' + str(skl_id)
    results = mysql.inquire_all(sql)
    return to_string_list(results)


def get_forms(mysql, skl_id):
    id_sql = 'select iten_id from action where type = 2 and skl_id = ' + str(skl_id)
    id_list = to_string_list(mysql.inquire_all(id_sql))
    forms = []
    for intent_id in id_list:
        sql = 'select name from intent where iten_id = ' + str(intent_id)
        name = mysql.inquire_one(sql)
        forms.append(name[0]+'_form')
    return forms


def get_slots(mysql, skl_id):
    # sql = 'select intent.name, slot.name from iten_slot inner join slot inner join intent ' \
    #       'on iten_slot.iten_id = intent.iten_id and iten_slot.slot_id = slot.slot_id ' \
    #       'where slot.skl_id = ' + str(skl_id)
    sql = 'select name from slot where skl_id = ' + str(skl_id)
    results = mysql.inquire_all(sql)
    return to_string_list(results)


def get_action(mysql, skl_id):
    # id_sql = 'select distinct iten_id from action where type = 1 and skl_id = ' + str(skl_id)
    # id_list = to_string_list(mysql.inquire_all(id_sql))
    # iten_action_sql = 'select name, iten_id from action where type = 0 and skl_id = ' + str(skl_id)
    # iten_actions = mysql.inquire_all(iten_action_sql)
    # ask_sql = 'select name from action where type = 1 and skl_id = ' + str(skl_id)
    # asks = to_string_list(mysql.inquire_all(ask_sql))
    # actions = []
    # for r in iten_actions:
    #     if r[1] not in id_list:
    #         actions.append(r[0])
    # actions.extend(asks)
    # return actions
    sql = 'select name from action where (type = 0 or type = 1) and skl_id = ' + str(skl_id)
    results = mysql.inquire_all(sql)
    return to_string_list(results)


def get_response(mysql, skl_id):
    slot_response = []
    intent_response = []
    form1_response = []
    form2_response = []
    # # 查iten_slot表
    # intent_slot_sql = 'select name, iten_id, slot_id from action where type = 1 and skl_id = ' + str(skl_id)
    # intent_slot_result = mysql.inquire_all(intent_slot_sql)
    # for item in intent_slot_result:
    #     ask_sql = 'select ask from iten_slot where iten_id = ' + str(item[1]) + ' and slot_id = ' + str(item[2])
    #     ask = mysql.inquire_one(ask_sql)
    #     r = [item[0], ask[0]]
    #     response.append(r)
    # 查slot表
    slot_sql = 'select action.name, slot.ask, slot.answer from action inner join slot on action.slot_id = slot.slot_id ' \
               'where action.skl_id = ' + str(skl_id)
    slot_result = mysql.inquire_all(slot_sql)
    for item in slot_result:
        r = [item[0], item[1], item[2]]
        slot_response.append(r)
    # 查intent表
    intent_sql = 'select action.name, intent.reply, intent.answertype from action inner join intent on action.iten_id = intent.iten_id ' \
                 'where action.type = 0 and action.skl_id = ' + str(skl_id)
    # 富文本返回的表单
    form1_sql = 'select action.name, intent.reply, intent.answertype from action inner join intent on action.iten_id = intent.iten_id ' \
                 'where intent.reply_type = 1 and action.type = 2 and action.skl_id = ' + str(skl_id)
    # 接口返回的表单
    form2_sql = 'select action.name, intent.answertype from action inner join intent on action.iten_id = intent.iten_id ' \
               'where intent.reply_type = 2 and action.type = 2 and action.skl_id = ' + str(skl_id)
    intent_result = mysql.inquire_all(intent_sql)
    for item in intent_result:
        r = [item[0], item[1], item[2]]
        intent_response.append(r)
    form1_result = mysql.inquire_all(form1_sql)
    for item in form1_result:
        r = [item[0], item[1], item[2]]
        form1_response.append(r)
    form2_result = mysql.inquire_all(form2_sql)
    for item in form2_result:
        r = [item[0], item[1]]
        form2_response.append(r)
    return slot_response, intent_response, form1_response, form2_response


def transfer_response(response):
    # 双引号和右斜杠转义
    tr_response = ""
    for ch in response:
        if ch == "\"" or ch == "\\":
            tr_response += "\\" + ch
        else:
            tr_response += ch
    return tr_response


def trans_response_json(res):
    # 双引号
    return res.replace('\"', "\\\"")

def to_domain(mysql, path, skl_id, model_type):
    # print(get_intents(mysql, 115))
    # print(get_forms(mysql, 115))
    # print(get_response(mysql, 115))
    intent_list = get_intents(mysql, skl_id)
    form_list = get_forms(mysql, skl_id)
    entity_list = slot_list = get_slots(mysql, skl_id)
    action_list = get_action(mysql, skl_id)
    action_list.append("action_slot_null")
    if model_type == 'qa':
        action_list.append('action_qa_intent')
    slot_response_list, intent_response_list, form1_response_list, form2_response_list = get_response(mysql, skl_id)
    domain_path = os.path.join(path, 'domain.yml')
    with open(domain_path, 'w', encoding='utf8') as f:
        format_write(f, "intents:", intent_list, end='\n')
        if form_list:
            format_write(f, "forms:", form_list, end='\n')
        if entity_list:
            format_write(f, "entities:", entity_list, end='\n')
        if slot_list:
            format_write(f, "slots:")
            for item in slot_list:
                format_write(f, item + ':', blank=2)
                format_write(f, "type: unfeaturized", blank=4)
            format_write(f, '')
        if action_list:
            format_write(f, "actions:", action_list, end='\n')
        if slot_response_list or intent_response_list or form1_response_list or form2_response_list:
            format_write(f, "responses:")
            for item in slot_response_list:
                response_format_write(f, item[0], trans_response_json(item[1]), 'answer', item[2], 2, '\n')
                # format_write(f, item[0] + ":", ['text: ' + "\"" + transfer_response(item[1]) + "\""], 2, '\n')
            for item in intent_response_list:
                if item[2] == 'json' or item[2] == 'ivr':
                    item[1] = item[1].replace('<p>', '').replace('</p>', '')
                    response_format_write(f, item[0], trans_response_json(item[1]), 'answerType', item[2], 2, '\n')
                else:
                    response_format_write(f, item[0], transfer_response(item[1]), 'answerType', item[2], 2, '\n')
            for item in form1_response_list:
                if item[2] == 'json' or item[2] == 'ivr':
                    item[1] = item[1].replace('<p>', '').replace('</p>', '')
                    response_format_write(f, item[0], trans_response_json(item[1]), 'answerType', item[2], 2, '\n')
                else:
                    response_format_write(f, item[0], transfer_response(item[1]), 'answerType', item[2], 2, '\n')
            for item in form2_response_list:
                response_format_write(f, item[0], "{my_var}", 'answerType', item[1], 2, '\n')
        f.write(session_opt)
