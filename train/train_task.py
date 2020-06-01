# @Time : 2020/5/10 22:33 
# @Author : lijundi
# @File : train_task.py 
# @Software: PyCharm
from bot_engine.models import Model


def create_train_task(version, skl_id):
    # 查询是否为第一次训练模型
    model_list = Model.objects.filter(skl_id=skl_id)
    # with open('123.txt', 'w') as f:
    #     p = subprocess.Popen('rasa train', shell=True, stdout=f, cwd=os.path.join('d:\\', 'rasaProject', '123'))
    #     p.wait()
    if model_list:
        return "v1"
    else:
        # 生成默认配置文件
        return 1
    # 写入数据库
