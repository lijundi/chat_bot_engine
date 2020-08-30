import os
from utils.constants import MODEL_DIR


def create_project_directory(skl_id):
    pro_dir = os.path.join(MODEL_DIR, str(skl_id))
    dir_data = os.path.join(pro_dir, 'data')
    dir_models = os.path.join(pro_dir, 'models')
    if not os.path.exists(dir_data):
        os.makedirs(dir_data)
    if not os.path.exists(dir_models):
        os.makedirs(dir_models)


