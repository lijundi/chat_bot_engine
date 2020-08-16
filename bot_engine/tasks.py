# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import subprocess
import os
import datetime
import pytz
from utils.constants import MODEL_DIR
from bot_engine.models import Model


@shared_task
def add(x, y):
    print(x + y)
    return x + y


@shared_task
def train_model(version, skl_id, std_out):
    print("开始训练")
    with open(std_out, 'w') as f:
        p = subprocess.Popen('rasa train', shell=True, stdout=f, cwd=os.path.join(MODEL_DIR, str(skl_id)))
        ret = p.wait()
    # 没有训练出新模型算训练失败
    with open(std_out, 'r') as f:
        out_str = f.read(50)
    if 'Nothing changed' in out_str:
        ret = 1
    # 是否训练成功
    if ret == 0:
        # 获取模型url
        models_dir = os.path.join(MODEL_DIR, str(skl_id), 'models')
        lists = os.listdir(models_dir)
        lists.sort(key=lambda x: os.path.getmtime(os.path.join(models_dir, x)))
        model_url = os.path.join(models_dir, lists[-1])
        print(model_url)
        if "nlu" in model_url:
            print("失败")
            Model.objects.filter(version=version, skill_id=skl_id).update(process="训练失败")
        else:
            Model.objects.filter(version=version, skill_id=skl_id).update(url=model_url)
            print("成功")
            create_time = Model.objects.get(version=version, skill_id=skl_id).create_time
            end_time = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC'))
            print("用时：" + str((end_time-create_time).seconds))
            Model.objects.filter(version=version, skill_id=skl_id).update(process="训练成功", time=(end_time-create_time).seconds)
    else:
        print("失败")
        Model.objects.filter(version=version, skill_id=skl_id).update(process="训练失败")
    return


@shared_task
def xsum(numbers):
    return sum(numbers)

