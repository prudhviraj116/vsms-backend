from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.utils import timezone


class Staff_depatments(models.Model):
    Department_id=models.IntegerField(primary_key=True)
    Departmentname=models.CharField(max_length=44)

    def save(self,*args,**kwargs):
        if not self.Department_id:
            department_count = Staff_depatments.objects.count()
            self.Department_id = department_count + 1
            
        super(Staff_depatments,self).save(*args,**kwargs)

    def __str__(self):
        return self.Departmentname


class User(AbstractUser):
    
    USER_TYPE_CHOICES = [
        ('1', 'Admin'),
        ('2', 'Staff'),
        ('3', 'Student'),
    ]
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='Student',max_length=20)




def Generatestaff_id():
    id=random.randint(0,500)
    return id
 
class Staff_tabel(models.Model):
    
    staff_id=models.IntegerField(primary_key=True)
    userrole=models.OneToOneField(User,on_delete=models.CASCADE)
    mobile=models.BigIntegerField(unique=True)
    address=models.CharField(max_length=24)
    Gender=models.CharField(max_length=20,choices=[('Female','Female'),('Male','Male'),('Other','Other')],default='Male')
    Image=models.ImageField(upload_to='Images/studentimages/',default='images/Default.jpg')
    desgination=models.ForeignKey(Staff_depatments,null=True,on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)  # Add this line

    

    objects=models.Manager()
    

    def save(self,*args,**kwargs):
        if not self.staff_id:
            self.staff_id=Generatestaff_id()
            self.userrole.user_type = '2'
            self.userrole.save()
        super(Staff_tabel,self).save(*args,**kwargs)
        
    def __str__(self):
        return self.userrole.username
    
class Admin_tabel(models.Model):
    userrole = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.userrole.pk:  # Check if the user already exists
            self.userrole.user_type = '1'
            self.userrole.save()
        super(Admin_tabel, self).save(*args, **kwargs)

    def __str__(self):
        return self.userrole.username




    