# @Time : 2020/5/7 11:53 
# @Author : lijundi
# @File : restful.py 
# @Software: PyCharm
from django.http import JsonResponse


class HttpCode(object):
    success = 1
    fail = 0


def result(code=HttpCode.success, message="成功", data=None):
    json_dict = {"code": code, "message": message, "data": data}
    return JsonResponse(json_dict)


def success(data=None):
    return result(data=data)


def fail():
    return result(code=HttpCode.fail, message="失败")


