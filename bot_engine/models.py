from django.db import models


# Create your models here.
class Model(models.Model):
    # model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    api = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    version = models.CharField(max_length=10)
    skill_id = models.IntegerField()
    des = models.TextField()
    process = models.CharField(max_length=20)
    # time = models.IntegerField()
    # create_time = models.DateTimeField()
    # update_time = models.DateTimeField()


class SubProcess(models.Model):
    model_pid = models.CharField(max_length=50)
    actions_pid = models.CharField(max_length=50)
    model_id = models.IntegerField()

