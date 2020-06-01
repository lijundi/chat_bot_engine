import json
import os
import subprocess
import signal

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from utils.restful import success, fail
from rasa.model_config_file import create_config_file
from bot_engine.models import Model
from management.data_base import save_model, get_models, del_model
from management.model_control import online_model, stop_model, start_model
from bot_engine import tasks
from utils.constants import MODEL_DIR


# Create your views here.
@csrf_exempt
def train(request):
    try:
        data = json.loads(request.body)
        skl_id = data['skl_id']
        # 判断是否为第一次训练
        first = not Model.objects.filter(skill_id=skl_id).exists()
        # 生成配置文件
        # create_config_file(skl_id, first)
        # 保存到数据库
        version = save_model(skl_id, first)
        # 生成训练任务
        tasks.train_model.delay(version, skl_id, os.path.join(MODEL_DIR, str(skl_id), 'train_log.txt'))
    except:
        return fail()
    else:
        result = {"version": version}
        return success(result)


@csrf_exempt
def online(request):
    try:
        data = json.loads(request.body)
        skl_id = data['skl_id']
        model_id = data['model_id']
        res = online_model(model_id, skl_id)
    except:
        return fail()
    else:
        if res:
            return success()
        else:
            return fail()


@csrf_exempt
def test(request):
    data = json.loads(request.body)
    skl_id = data['skl_id']
    pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    actions_port = '5055'
    cmd_actions = 'rasa run actions ' + ' -p ' + actions_port
    with open(os.path.join(pro_dir, 'actions_log.txt'), 'w') as f1:
        p1 = subprocess.Popen(cmd_actions, shell=True, stdout=f1, cwd=pro_dir)
    result = {"version": p1.pid}
    return success(result)


