import os
import shutil
from bot_engine.models import Model
from utils.constants import MODEL_DIR


def newest_version(v_list):
    version = 'V0'
    for v in v_list:
        tmp = v['version']
        if int(tmp[1:]) > int(version[1:]):
            version = tmp
    # 版本号迭代加一
    v_num = int(version[1:]) + 1
    return 'V' + str(v_num)


def save_model(skl_id, first):
    status = 'offline'
    process = '训练中'
    if first:
        version = "V1"
    else:
        version = newest_version(Model.objects.filter(skill_id=skl_id).values('version'))
    m = Model(status=status, process=process, version=version, skill_id=skl_id)
    m.save()
    return version


def get_models(skl_id):
    return list(Model.objects.filter(skill_id=skl_id).values())


def del_model(model_id):
    m = Model.objects.filter(id=model_id).values('process', 'status', 'url', 'skill_id')[0]
    if m['process'] != '训练中' and m['status'] != 'online':
        # 删除文件
        if m['process'] != '训练失败':
            os.remove(m['url'])
        # 删除数据库
        Model.objects.filter(id=model_id).delete()
        # 判断是否存在模型
        if not Model.objects.filter(skill_id=m['skill_id']).exists():
            pro_dir = os.path.join(MODEL_DIR, str(m['skill_id']))
            shutil.rmtree(pro_dir)
        return True
    else:
        return False

