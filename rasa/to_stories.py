# @Time : 2020/4/7 14:34 
# @Author : lijundi
# @File : to_stories.py
# @Software: PyCharm
"""
story1 = [dict(name='greet', actions=['utter_greet']), dict(name='query_weather', actions=['query_weather_form',
'form{\"name\": \"query_weather_form\"}', 'form{\"name\": null}'])]
story_list = []

raw_story_list = [['intent-greet-notForm',
                   'action-utter_greet',
                   'intent-query_weather-query_weather_form',
                   'action-utter_query_weather'],
                  ['intent-greet-notForm',
                   'action-utter_greet',
                   'intent-query_weather-query_weather_form',
                   'intent-request_search-notForm',
                   'action-utter_request_search',
                   'action-utter_query_weather',
                   'intent-bye-notForm',
                   'action-utter_bye'],
                  ['intent-greet-notForm',
                   'action-utter_greet',
                   'intent-query_weather-query_weather_form',
                   'intent-123-notForm',
                   'action-utter_test',
                   '#stopForm',
                   'intent-request_search-notForm',
                   'action-utter_request_search',
                   'intent-bye-notForm',
                   'action-utter_bye']]
"""
import json
import os

from rasa.file_opt import format_write

qa_story = '## QA story\n' \
           '* QAIntent\n' \
           '  - action_qa_intent\n\n'


def get_raw_story_list(mysql, skl_id):
    sql = 'select nodes, edges from dmdata where skl_id = ' + str(skl_id)
    return to_raw_story_list(mysql.inquire_all(sql))


def to_raw_story_list(results):
    stories = list()
    hasSlot = dict()
    for r in results:
        nodes = json.loads(r[0])
        edges = json.loads(r[1])
        dictionary = dict()
        for node in nodes:
            node_id = node['id']
            if node_id.split('-')[0] == 'start':
                dictionary['start'] = list()
            elif node_id.split('-')[0] == 'slot':
                print(node)
            else:
                # print(node_id)
                dictionary[node_id] = list()
        for edge in edges:
            source_id = edge['sourceId']
            target_id = edge['targetId']
            source_type = source_id.split('-')[0]
            if source_type == 'start':
                dictionary['start'].append(target_id)
            elif source_type == 'slot':
                # print(target_id)
                if target_id in hasSlot:
                    hasSlot[target_id].append(source_id)
                else:
                    hasSlot[target_id] = [source_id]
            else:
                dictionary[source_id].append(target_id)
        path = list()
        dfs(stories, dictionary, 'start', path)
    # print(hasSlot)
    # 再加工
    for story in stories:
        for i in range(0, len(story)):
            str_list = story[i].split('-')
            if str_list[0] == 'intent':
                if story[i] in hasSlot:
                    string = str_list[0] + '-' + str_list[2] + '-' + str_list[2] + '_form'
                else:
                    string = str_list[0] + '-' + str_list[2] + '-notForm'
            elif str_list[0] == 'action':
                string = str_list[0] + '-' + str_list[1]
            elif str_list[0] == '#stopForm':
                string = str_list[0]
            else:
                string = ''
            story[i] = string
    # print(stories)
    return stories


def dfs(res, dictionary, cur, path):
    childs = dictionary[cur]
    if childs:
        for child in childs:
            path.append(child)
            dfs(res, dictionary, child, path)
            path.pop()
    else:
        tmp_path = path[:]  # 切片法复制list
        res.append(tmp_path)
        return


def to_story_list(raw_story_list):
    story_list = []
    for raw_story in raw_story_list:
        story = list()
        item = dict()
        flag = False
        flag2 = False  # 表单中判断是否直接结束
        form_name = ''
        for t in raw_story:
            results = t.split('-')
            if results[0] == 'intent':
                if flag:
                    story.append(item)  # 插入节点
                    flag2 = True
                item = dict(name=results[1])
                if results[2] != 'notForm':  # 表单意图
                    flag = True
                    form_name = results[2]
                    item['actions'] = [results[2], 'form{\"name\": \"' + results[2] + '\"}']
            elif results[0] == 'action':
                if flag:  # 表单中
                    if results[1][6:] == form_name.replace('_form', ''):  # 表单结束
                        if flag2:
                            item['actions'].append(form_name)
                        item['actions'].append('form{\"name\": null}')
                        story.append(item)  # 插入节点
                        flag = False
                        flag2 = False
                    else:  # 表单未结束
                        item['actions'] = [results[1]]
                else:  # 非表单中则直接插入节点
                    item['actions'] = [results[1]]
                    story.append(item)  # 插入节点
            elif results[0] == '#stopForm':  # 表单停止
                item['actions'].append('action_deactivate_form')
                item['actions'].append('form{\"name\": null}')
                item['actions'].append('action_slot_null')
                story.append(item)  # 插入节点
                flag = False
                flag2 = False
        # print(story)
        story_list.append(story)
    return story_list


def to_stories(mysql, path, skl_id, model_type):
    raw_story_list = get_raw_story_list(mysql, skl_id)
    story_list = to_story_list(raw_story_list)
    # print(story_list)
    stories_path = os.path.join(path, 'data', 'stories.md')
    with open(stories_path, 'w', encoding='utf8') as f:
        for story, index in zip(story_list, range(0, len(story_list))):
            story_name = '## story' + str(index) + '\n'
            f.write(story_name)
            for item in story:
                intent_name = item['name']
                action_list = item['actions']
                format_write(f, intent_name, action_list, start='* ')
            f.write('\n')
        if model_type == 'qa':
            f.write(qa_story)

