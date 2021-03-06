# @Time : 2020/4/8 0:40 
# @Author : lijundi
# @File : to_actions.py
# @Software: PyCharm
"""
form_list = [{'name': 'test_form', 'slots': ['location', 'time'], 'action':'123'}]
"""
import os
from rasa.to_domain import to_string_list

head = 'from typing import Any, Text, Dict, List\n' \
       'from rasa_sdk import Action, Tracker\n' \
       'from rasa_sdk.events import Restarted, AllSlotsReset\n' \
       'from rasa_sdk.executor import CollectingDispatcher\n' \
       'from rasa_sdk.forms import FormAction\n' \
       'import requests\n' \
       'import json\n\n\n'

func_name = '    def name(self) -> Text:\n'
func_slots = '    @staticmethod\n' \
             '    def required_slots(tracker: Tracker) -> List[Text]:\n'
func_submit = '    def submit(\n' \
              '        self,\n' \
              '        dispatcher: CollectingDispatcher,\n' \
              '        tracker: Tracker,\n' \
              '        domain: Dict[Text, Any],\n' \
              '    ) -> List[Dict]:\n'
func_submit_return = '        return [Restarted()]\n\n\n'

form_action = '        response = requests.post(url, body)\n' \
              '        dispatcher.utter_message(response.text)\n'

func_slot_null = 'class SlotNull(Action):\n\n' \
                 '    def name(self) -> Text:\n' \
                 '        return "action_slot_null"\n\n' \
                 '    def run(\n' \
                 '        self,\n' \
                 '        dispatcher: CollectingDispatcher,\n' \
                 '        tracker: Tracker,\n' \
                 '        domain: Dict[Text, Any]\n' \
                 '    ) -> List[Dict[Text, Any]]:\n' \
                 '        return [AllSlotsReset()]\n\n\n'


def get_form_list(mysql, skl_id):
    id_sql = 'select iten_id from action where type = 2 and skl_id = ' + str(skl_id)
    id_list = to_string_list(mysql.inquire_all(id_sql))
    form_list = []
    for intent_id in id_list:
        name_reply_sql = 'select name, reply from intent where iten_id = ' + str(intent_id)
        name_reply = mysql.inquire_one(name_reply_sql)
        name = name_reply[0] + '_form'
        action = name_reply[1]
        slots_sql = 'select slot.name from iten_slot inner join slot on iten_slot.slot_id = slot.slot_id ' \
                    'where iten_id = ' + str(intent_id)
        raw_slots = mysql.inquire_all(slots_sql)
        slots = to_string_list(raw_slots)
        fm = dict(name=name, slots=slots, action=action)
        form_list.append(fm)
    return form_list


def to_actions(mysql, path, skl_id):
    form_list = get_form_list(mysql, skl_id)
    # print(form_list)
    actions_path = os.path.join(path, 'actions.py')
    with open(actions_path, 'w', encoding='utf8') as f:
        f.write(head)
        for form in form_list:
            str_list = form['name'].split('_')
            for index in range(0, len(str_list)):
                str_list[index] = str_list[index].capitalize()
            class_name = 'class ' + ''.join(str_list) + '(FormAction):\n\n'
            f.write(class_name)
            f.write(func_name)
            f.write('        return \'' + form['name'] + '\'\n\n')
            f.write(func_slots)
            f.write('        return ' + repr(form['slots']) + '\n\n')
            f.write(func_submit)
            # 写动作
            for slot in form['slots']:
                f.write('        ' + slot + ' = tracker.get_slot(\'' + slot + '\')\n')
            f.write('        url = \'' + form['action'] + '\'\n')
            f.write('        body = {')
            for i in range(0, len(form['slots'])):
                f.write('\'' + form['slots'][i] + '\': ' + form['slots'][i])
                if i < len(form['slots']) - 1:
                    f.write(', ')
                else:
                    f.write('}\n')
            f.write(form_action)
            f.write(func_submit_return)
        f.write(func_slot_null)

