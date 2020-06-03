import os
from utils.constants import MODEL_DIR
from management.storage import create_project_directory
from rasa.mysql import MySql
from rasa.to_actions import to_actions
from rasa.to_stories import to_stories
from rasa.to_domain import to_domain
from rasa.to_nlu import to_nlu
from rasa.to_default import to_default


# 生成配置文件
def create_config_file(skl_id, first):
    host = "10.108.211.136"  # 数据库的ip地址
    user = "root"  # 数据库的账号
    password = "mySQL#h@d00p"  # 数据库的密码
    port = 3306  # mysql数据库通用端口号
    mysql = MySql(host=host, user=user, password=password, port=port, database='bot')
    pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    # dir_data = os.path.join(pro_dir, 'data')
    if first:
        # 创建目录
        create_project_directory(skl_id)
        # 默认配置文件
        to_default(pro_dir)

    # 开发人员配置的文件
    to_actions(mysql, pro_dir, skl_id)
    to_stories(mysql, pro_dir, skl_id)
    to_domain(mysql, pro_dir, skl_id)
    to_nlu(mysql, pro_dir, skl_id)



