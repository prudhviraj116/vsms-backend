from django.contrib import admin
from .models import Student_tabel,Batch,Fee,DailyVideo,Attendancelist,Session
# Register your models here.

admin.site.register(Student_tabel)
admin.site.register(Batch)
admin.site.register(Fee)
admin.site.register(Attendancelist)
admin.site.register(Session)

admin.site.register(DailyVideo)
