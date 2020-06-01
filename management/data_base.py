
from bot_engine.models import Model


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
    return Model.objects.filter(skl_id=skl_id).values()


def del_model(model_id):
    Model.objects.filter(id=model_id).delete()

