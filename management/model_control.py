import os
import signal
import subprocess
import socket
from bot_engine.models import Model, SubProcess
from utils.constants import MODEL_DIR
from rasa.to_default import to_endpoints


def run(model_id):
    m = Model.objects.filter(id=model_id).values('url', 'skill_id')[0]
    model_url = m['url']
    skl_id = m['skill_id']
    pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    # 分配端口
    model_port, actions_port = get_free_ports(8300, 8400)
    # 重写endpoint配置文件 写入actions服务器运行的端口
    enps = 'action_endpoint:\n' \
           ' url: \"http://localhost:' + actions_port + '/webhook\"\n'
    to_endpoints(enps, pro_dir)
    # 生成命令 转义字符的问题
    cmd_model = 'rasa run -m ' + model_url + ' -p ' + model_port + ' --enable-api --log-file out.log'
    cmd_actions = 'rasa run actions ' + ' -p ' + actions_port
    # 创建子进程
    with open(os.path.join(pro_dir, 'actions_log.txt'), 'w') as f1:
        p1 = subprocess.Popen(cmd_actions, shell=True, stdout=f1, cwd=pro_dir)
    with open(os.path.join(pro_dir, 'model_log.txt'), 'w') as f2:
        p2 = subprocess.Popen(cmd_model, shell=True, stdout=f2, cwd=pro_dir)
    # 判断是否运行成功
    if p1.returncode is None and p2.returncode is None:
        print("run model: " + str(model_id))
        # 记录api
        api = 'http://127.0.0.1:' + model_port + '/webhooks/rest/webhook'
        Model.objects.filter(id=model_id).update(api=api, status='online')
        # 保存到数据库
        sp = SubProcess(model_id=model_id, model_pid=p2.pid, model_port=model_port, actions_pid=p1.pid, actions_port=actions_port)
        sp.save()
        return True
    else:
        print("fail to run model")
        return False


def stop(model_id):
    sp = SubProcess.objects.filter(model_id=model_id).values()[0]
    # linux适用
    os.kill(int(sp['model_pid']), signal.SIGINT)
    os.kill(int(sp['actions_pid']), signal.SIGINT)
    # 删除记录
    SubProcess.objects.filter(model_id=model_id).delete()
    print("stop model: " + str(model_id))


def check_running_model(skl_id):
    # 一个机器人只有一个模型在运行
    if Model.objects.filter(skill_id=skl_id, status='online').exists():
        model_id = Model.objects.filter(skill_id=skl_id, status='online').values('id')[0]['id']
        Model.objects.filter(id=model_id).update(status='offline', api='')
        stop(model_id)
    else:
        Model.objects.filter(skill_id=skl_id, status='stop').update(status='offline')


def online_model(model_id):
    skl_id = Model.objects.get(id=model_id).skill_id
    check_running_model(skl_id)
    return run(model_id)


def stop_model(model_id):
    Model.objects.filter(id=model_id).update(status='stop', api='')
    stop(model_id)


def start_model(model_id):
    return run(model_id)


def get_free_ports(start, end):
    m_port = end
    # a_port = 0
    for i in range(start, end):
        if not_used(i) and is_free_port(i):
            m_port = i
            print("m_port:" + str(m_port))
            break
    for i in range(m_port+1, end):
        if not_used(i) and is_free_port(i):
            a_port = i
            print("a_port:" + str(a_port))
            return str(m_port), str(a_port)
    raise Exception(print("no free ports"))


def is_free_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', port))
        s.shutdown(2)
        return False
    except Exception as e:
        print(e)
        return True


def not_used(port):
    used_ports_dict = SubProcess.objects.all().values('model_port', 'actions_port')
    for i in used_ports_dict:
        if port == i['model_port'] or port == i['actions_port']:
            return False
    return True

