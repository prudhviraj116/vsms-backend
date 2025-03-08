from django.db import models
from staffportal.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail


from django.conf import settings

import os

from django.conf import settings
from rest_framework.authtoken.models import Token
# Create your models here.

class Batch(models.Model):
    batch_id = models.CharField(max_length=20, primary_key=True)
    batch_name = models.CharField(max_length=50,unique=True)
    # Add any other batch-related fields as needed

    def __str__(self):
        return self.batch_name
  


class Student_tabel(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    userrole=models.OneToOneField(User,on_delete=models.CASCADE)
    mobile_no = models.BigIntegerField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Link student to a batch
    Gender=models.CharField(max_length=20,choices=[('Female','Female'),('Male','Male'),('Other','Other')],default='Male')
    address=models.CharField(max_length=24,null=True)
    Image=models.ImageField(upload_to='Images/staffimages/',blank=True,null=True)
    Qulification=models.CharField(max_length=10,null=True)
    resume = models.FileField(upload_to='resumes/',blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Add this line

    objects=models.Manager()

    
    def __str__(self):
        return self.userrole.username

    
    def save(self, *args, **kwargs):
        if not self.student_id:
        # Generate student_id if it's not set
    
            # Get the batch_id associated with this student
            batch_id = self.batch.batch_id

            # Count existing students in this batch
            existing_students_count = Student_tabel.objects.filter(batch=self.batch).count()

            # Generate new student_id
            new_student_id = f"{batch_id}-{existing_students_count + 1}"

            self.student_id = new_student_id
            self.userrole.user_type = '3'
            self.userrole.save()
         
        super().save(*args, **kwargs)



class Fee(models.Model):
    student = models.OneToOneField(Student_tabel, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('pending', 'Pending')], default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Fee details for Student ID: {self.student.student_id}"

    def update_amount_paid(self, amount):
        if amount <= 0:
            raise ValueError("Amount to be paid must be positive.")
        
        # Add the new payment amount to the existing amount_paid
        if isinstance(amount, float):
            amount = int(amount)
        self.amount_paid += amount
        
        # Ensure amount_paid does not exceed total_amount
        if self.amount_paid > self.total_amount:
            self.amount_paid = self.total_amount
        
        # Update the fee status based on the amount paid
        if self.amount_paid >= self.total_amount:
            self.fee_status = 'paid'
        else:
            self.fee_status = 'pending'
        
        self.save()

    @property
    def balance_due(self):
        return self.total_amount- self.amount_paid
        
class Session(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    session_date = models.DateField()
    session_type = models.CharField(max_length=50,choices=[('Lab', 'Lab'), ('Weekelytest', 'WeekelyTest'),('WeekelyMock', 'WeekelyMock')], default='Lab')  # labsession, mockinterviewsession, weeklytestsession
    def __str__(self):
        return f"{self.session_type} - {self.session_date}"
    class Meta:
        # Ensure no duplicate sessions for the same batch, date, and type
        unique_together = ['batch', 'session_date', 'session_type']
    
class Attendancelist(models.Model):
    student = models.ForeignKey(Student_tabel, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    marked_at = models.DateField(null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.student} - {self.session.session_type} - Present: {self.present}"
    class Meta:
        unique_together = ('student', 'session')
    
    

class DailyVideo(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='daily_videos/')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    upload_date = models.DateTimeField()

    def __str__(self):
        return self.title





class Task(models.Model):
    TASK_TYPES = [
        ('Weekly Test', 'Weekly Test'),
        ('Lab Task', 'Lab Task'),
        ('Notification', 'Notification'),
    ]
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    content = models.TextField()
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.task_type}: {self.content[:50]}'

    






class Notification(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Add this field to track read status

    def __str__(self):
        return f"Notification from {self.name}"
    




class Placement(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.name}"
    





# @receiver(post_save, sender=Student_tabel)
# def send_student_creation_email(sender, instance, created, **kwargs):
#     if created:
#         subject = 'Welcome to Our Platform!'
#         html_message = render_to_string('email/student_creation_email.html', {'user': instance})
#         plain_message = strip_tags(html_message)  # Strip HTML tags for plain text email
#         from_email = settings.EMAIL_HOST_USER
#         to_email = instance.email
#         send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)





@receiver(post_save, sender=Student_tabel)
def send_student_creation_email(sender, instance, created, **kwargs):
        if created:
            
            subject = 'Welcome to Vcube, {}!'.format(instance.userrole.username)
        message = '''
Hello {username},

Welcome to Vcube!

We are thrilled to have you join our platform. Your account has been successfully created, and you are now enrolled in your course. To get started, please log in to your account and explore the resources we have prepared for you.

If you have any questions or need assistance, feel free to reach out to our support team.

Best regards,
The Vcube Team
        '''.format(username=instance.userrole.username)
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.userrole.email
        
        send_mail(subject, message, from_email, [to_email], fail_silently=False)


@receiver(post_save, sender=Task)
def send_task_email(sender, instance, created, **kwargs):
        if created:  # Ensure this runs only when a new task is created
            students = Student_tabel.objects.filter(batch=instance.batch)
            recipient_emails = [student.userrole.email for student in students]

            subject = f'New Task Assigned: {instance.task_type}'
            message = f"""
            Hello Students,

            We hope you're doing well!

            A new task has been assigned to you on the vcube portal. Here are the details:


            Task Type: {instance.task_type}
            Content: {instance.content}

            Please log in to the vcube portal to view and complete your task before the due date.

            Best regards,
            The vcube Team
            """

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                recipient_emails,
                fail_silently=False,
    )