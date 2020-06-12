from django.db import models
# import django.utils.timezone as timezone


# Create your models here.
class Model(models.Model):
    # model_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50, default='')
    url = models.CharField(max_length=50)
    api = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    version = models.CharField(max_length=10)
    skill_id = models.IntegerField()
    # des = models.TextField(default='')
    process = models.CharField(max_length=20)
    time = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class SubProcess(models.Model):
    model_pid = models.CharField(max_length=50)
    model_port = models.IntegerField()
    actions_pid = models.CharField(max_length=50)
    actions_port = models.IntegerField()
    model_id = models.IntegerField()

