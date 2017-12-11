from django.db import models

# Create your models here.

class Room(models.Model):
    name=models.CharField(max_length=32,verbose_name='会议室名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural='会议室'

class UserInfo(models.Model):
    name=models.CharField(max_length=32,verbose_name='用户名')
    pwd=models.CharField(max_length=32,verbose_name='密码')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural='用户表'

class Book(models.Model):
    date=models.DateField(max_length=32,verbose_name='日期')
    time_choice=((1,"8:00"),(2,'9:00'),(3,'10:00'),(4,'11:00'),(5,'12:00'),(6,'13:00'),
                 (7,'14:00'),(8,'15:00'),(9,'16:00'),(10,'17:00'),(11,'18:00'),(12,'19:00'),
                 (13,'20:00'),
                 )
    time=models.IntegerField(choices=time_choice,verbose_name='时间段')
    room=models.ForeignKey('Room',verbose_name='会议室')
    user=models.ForeignKey('UserInfo',verbose_name='用户',null=True)


    class Meta:
        verbose_name_plural='预定表'
        unique_together=(
            ('date','time','room'),
        )


