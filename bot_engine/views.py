import json
import os
import subprocess
import signal
import shutil
import datetime
import pytz

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize

from utils.restful import success, fail
from rasa.model_config_file import create_config_file
from bot_engine.models import Model, SubProcess
from management.data_base import save_model, get_models, del_model, get_port_from_api, get_tracker_api
from management.model_control import online_model, stop_model, start_model, get_free_ports
from bot_engine import tasks
from utils.constants import MODEL_DIR


# Create your views here.
@csrf_exempt
def train(request):
    try:
        data = json.loads(request.body)
        skl_id = data['skl_id']
        model_type = data['model_type']  # chat, qa
        # 判断是否为第一次训练
        first = not Model.objects.filter(skill_id=skl_id).exists()
        # 生成配置文件
        create_config_file(skl_id, first, model_type)
        # 保存到数据库
        version = save_model(skl_id, first)
        # 生成训练任务
        tasks.train_model.delay(version, skl_id, os.path.join(MODEL_DIR, str(skl_id), 'train_log.txt'))
    except Exception as e:
        print(e)
        return fail()
    else:
        result = {"version": version}
        return success(result)


@csrf_exempt
def online(request):
    try:
        data = json.loads(request.body)
        model_id = data['model_id']
        res = online_model(model_id)
    except Exception as e:
        print(e)
        return fail()
    else:
        if res:
            # api = Model.objects.get(id=model_id).api
            # result = {"api": api}
            return success()
        else:
            return fail()


@csrf_exempt
def stop(request):
    try:
        data = json.loads(request.body)
        model_id = data['model_id']
        stop_model(model_id)
    except Exception as e:
        print(e)
        return fail()
    else:
        return success()


@csrf_exempt
def start(request):
    try:
        data = json.loads(request.body)
        model_id = data['model_id']
        res = start_model(model_id)
    except Exception as e:
        print(e)
        return fail()
    else:
        if res:
            return success()
        else:
            return fail()


@csrf_exempt
def get_by_skl_id(request):
    try:
        data = json.loads(request.body)
        skl_id = data['skl_id']
        models = get_models(skl_id)
        # json_data = serialize('json', models)  # str
        # models = json.loads(json_data)
    except Exception as e:
        print(e)
        return fail()
    else:
        return success(models)


@csrf_exempt
def delete_by_model_id(request):
    try:
        data = json.loads(request.body)
        model_id = data['model_id']
        res = del_model(model_id)
    except Exception as e:
        print(e)
        return fail()
    else:
        if res:
            return success()
        else:
            return fail()


@csrf_exempt
def get_online_model(request):
    try:
        data = json.loads(request.body)
        skl_id = data['skl_id']
        sender = data['sender']
        if Model.objects.filter(skill_id=skl_id, status='online').exists():
            m = Model.objects.filter(skill_id=skl_id, status='online').values('id', 'api')[0]
            tracker = get_tracker_api(get_port_from_api(m['api']), str(sender))
            result = {'model_id': m['id'], 'api': m['api'], 'tracker': tracker}
            return success(result)
        return fail()
    except Exception as e:
        print(e)
        return fail()


# @csrf_exempt
# def reset_model(request):
#     try:
#         data = json.loads(request.body)
#         skl_id = data['skl_id']
#         if Model.objects.filter(skill_id=skl_id, status='online').exists():
#             model_id = Model.objects.filter(skill_id=skl_id, status='online').values('id')[0]['id']
#             stop_model(model_id)
#             if online_model(model_id):
#                 return success()
#         return fail()
#     except Exception as e:
#         print(e)
#         return fail()

@csrf_exempt
def test(request):
    # data = json.loads(request.body)
    # skl_id = data['skl_id']
    # version = data['version']
    # pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    # actions_port = '5055'
    # cmd_actions = 'rasa run actions ' + ' -p ' + actions_port
    # with open(os.path.join(pro_dir, 'actions_log.txt'), 'w') as f1:
    #     p1 = subprocess.Popen(cmd_actions, shell=True, stdout=f1, cwd=pro_dir)
    # model_id = Model.objects.filter(skill_id=123, status='offline').values('id')[0]['id']
    # for i in range(9, 9):
    #     #     print(i)
    # model_port, actions_port = get_free_ports(8300, 8400)
    # sp = SubProcess(model_id=1, model_pid=2, model_port=model_port, actions_pid=3,
    #                 actions_port=actions_port)
    # sp.save()
    # result = {"m": model_port, "a": actions_port}
    # data = json.loads(request.body)
    # model_id = data['model_id']
    # skl_id = Model.objects.get(id=model_id).skill_id
    # result = {'skl_id': skl_id}
    # pro_dir = os.path.join(MODEL_DIR, str(1))
    # shutil.rmtree(pro_dir)
    # save_model(1, True)
    # with open(os.path.join(MODEL_DIR, 'train_log.txt'), 'r') as f:
    #     out_str = f.read(50)
    # if 'Nothing changed' in out_str:
    #     result = {'status': 'ok'}
    # create_time = Model.objects.get(version="V1", skill_id=1).create_time
    # end_time = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC'))
    # result = {'time': (end_time-create_time).seconds}
    # else:
    tracker = get_tracker_api(get_port_from_api('http://10.108.211.136:8300/webhooks/rest/webhook'), '0001')
    result = {'out_string': tracker}
    return success(result)


def clear_sub_process():
    sp_list = SubProcess.objects.all().values()
    for sp in sp_list:
        os.kill(int(sp['model_pid']), signal.SIGINT)
        os.kill(int(sp['actions_pid']), signal.SIGINT)
    SubProcess.objects.all().delete()
    print("clear SubProcess data in MySql")
    Model.objects.all().update(status="offline")
    print("set all models offline")


clear_sub_process()


