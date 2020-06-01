import os
import signal
import subprocess
from bot_engine.models import Model, SubProcess
from utils.constants import MODEL_DIR
from rasa.to_default import to_endpoints


def run(model_id):
    m = Model.objects.filter(id=model_id).values('url', 'skl_id')[0]
    model_url = m['url']
    skl_id = m['skl_id']
    pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    # 分配端口
    model_port = '5005'
    actions_port = '5055'
    # 重写endpoint配置文件 写入actions服务器运行的端口
    enps = 'action_endpoint:\n' \
           ' url: \"http://localhost:' + actions_port + '/webhook\"\n'
    to_endpoints(enps, pro_dir)
    # 生成命令 转义字符的问题
    cmd_model = 'rasa run -m ' + model_url + ' -p ' + model_port
    cmd_actions = 'rasa run actions ' + ' -p ' + actions_port
    # 创建子进程
    with open(os.path.join(pro_dir, 'actions_log.txt'), 'w') as f1:
        p1 = subprocess.Popen(cmd_actions, shell=True, stdout=f1, cwd=pro_dir)
    with open(os.path.join(pro_dir, 'model_log.txt'), 'w') as f2:
        p2 = subprocess.Popen(cmd_model, shell=True, stdout=f2, cwd=pro_dir)
    # 判断是否运行成功
    if p1.returncode is None and p2.returncode is None:
        print("run model: " + model_id)
        # 保存到数据库
        sp = SubProcess(model_id=model_id, model_pid=p2.pid, actions_pid=p1.pid)
        sp.save()
        return True
    else:
        print("fail to run model")
        return False


def stop(model_id):
    sp_list = SubProcess.objects.filter(id=model_id).values()
    sp = sp_list[0]
    # linux适用
    os.kill(int(sp['model_pid']), signal.SIGKILL)
    os.kill(int(sp['actions_pid']), signal.SIGKILL)
    print("stop model: " + model_id)


def check_running_model(skl_id):
    if Model.objects.filter(skill_id=skl_id, status='online').exists():
        model_id = Model.objects.filter(skill_id=skl_id, status='online').values('model_id')['model_id']
        Model.objects.filter(id=model_id).update(status='offline')
        Model.objects.filter(skill_id=skl_id, status='stop').update(status='offline')
        stop_model(model_id)


def online_model(model_id, skl_id):
    check_running_model(skl_id)
    Model.objects.filter(id=model_id).update(status='online')
    run(model_id)


def stop_model(model_id):
    Model.objects.filter(id=model_id).update(status='stop')
    stop(model_id)


def start_model(model_id):
    Model.objects.filter(id=model_id).update(status='online')
    run(model_id)


