from django.shortcuts import render
from django.http import Http404
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.authentication import TokenAuthentication
from.models import Student_tabel,Batch,Fee,Attendancelist,Session,Task,DailyVideo, Notification,Placement

from staffportal.models import User,Staff_tabel
from.Serializer import StudentSerilizer,BatchSerializer,SessionSerializer,AttendanceSerializer,StudentSerializerss,LabSessionDataSerializer,StudentUpdateSerializer,StudentSerializerres,SessionSerializers,TaskSerializer,DailyVideoSerializer,studentupdateSerializers,NotificationSerializer,PlacementSerializer,StudentprofileSerializerres,StudentSerilizer,StudentSerilizers
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_401_UNAUTHORIZED,HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.authtoken.models import Token
from datetime import date
from django.contrib.auth import authenticate

from django.db.models import F
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.dateparse import parse_datetime
import datetime



# Create your views here.

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def Studentlist(request):
    staffdata=Student_tabel.objects.all()
    staffdetails=StudentSerilizer(staffdata,many=True)
    return Response(staffdetails.data,status=HTTP_200_OK)

@api_view(['POST'])
def student_create(request):
    if request.method == 'POST':
        serializer = StudentSerilizer(data=request.data)
        if serializer.is_valid():
            student_ins=serializer.save()
            token=Token.objects.create(user=student_ins.userrole)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
# # {
#     "userrole": {
#       "username": "papu",
#       "email": "papu@gmail.com"
#     },
#     "mobile_no": 9976543258,
#     "batch": "Dj-01",
#    "fee": {
#         "amount_paid": 900.00,
#         "fee_status": "pending",
#         "total_amount":27000
#      }

#   }

#   }

@api_view(['GET','PUT'])
def update_student(request,mobile_number):
    
    if not mobile_number:
        return Response({'error': 'Mobile number is required'}, status=HTTP_400_BAD_REQUEST)
    
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_number)
    except Student_tabel.DoesNotExist:
        return Response({'error': 'Student profile not found or not registered by staff.'}, status=HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        seriaObj = StudentSerilizer(student)
        return Response(seriaObj.data,status=HTTP_200_OK)
    
    if request.method == 'PUT':
        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

# {
# "password":"ThankGod@123",
# "address":"Hydrabad",
# "Qulification":"B.tech",
# "Gender":"Female",
# "Image":null
# }

@api_view(['PUT'])
def upload_image(request, pk):
    try:
        student = Student_tabel.objects.get(pk=pk)
    except Student_tabel.DoesNotExist:
        return Response({'error': 'Student not found'}, status=HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        image = request.FILES.get('image')  # Ensure this matches the field name in your request
        if image:
            student.Image = image
            student.save()
            return Response(StudentSerilizer(student).data, status=HTTP_200_OK)
        return Response({'error': 'No image provided'}, status=HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def make_payment(request, student_id):
    try:
        # Fetch the Fee instance associated with the given student_id
        fee_instance = Fee.objects.get(student__student_id=student_id)

        # Get the amount_paid from the request data
        amount_paid = request.data.get('amount_paid')
        
        # Validate amount_paid
        if amount_paid is None:
            return Response({'error': 'Amount paid is required.'}, status=HTTP_400_BAD_REQUEST)

        try:
            amount_paid = float(amount_paid)
        except ValueError:
            return Response({'error': 'Invalid amount paid.'}, status=HTTP_400_BAD_REQUEST)

        # Update the amount paid and save
        fee_instance.update_amount_paid(amount_paid)

        # Return success response
        return Response({'message': 'Payment successful.'}, status=HTTP_200_OK)
    
    except Fee.DoesNotExist:
        return Response({'error': 'Fee details not found for the given student ID.'}, status=HTTP_404_NOT_FOUND)
# {"amount_paid":4000}



          
@api_view(['GET'])
def batch_list(request):
    batches = Batch.objects.all()
    serializer = BatchSerializer(batches, many=True)
    return Response(serializer.data)

#create new batch
@api_view(['POST'])
def create_new_batch(request):
    batchseril=BatchSerializer(data=request.data)
    if batchseril.is_valid():
        batchseril.save()
        return Response({'message': 'new batch created successfully'}, status=HTTP_201_CREATED)
    else:
        return Response(batchseril.errors, status=HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def students_in_batch(request, batch_id):
    students = Student_tabel.objects.filter(batch_id=batch_id)
    serializer = StudentSerializerss(students, many=True)
    return Response(serializer.data)

def get_students_with_attendance(batch_id, id):
    try:
        batch = Batch.objects.get(batch_id=batch_id)
    except Batch.DoesNotExist:
        raise Http404("Batch does not exist")
    
    try:
        session = Session.objects.get(id=id, batch=batch)
        print(session.id)
    except Session.DoesNotExist:
        session = None

    students = Student_tabel.objects.filter(batch=batch)
    
    
    student_attendance = []

    for student in students:
        
        try:
            # attendance_records = Attendancelist.objects.filter(student=student,session=session)
            attendance_records_student = Attendancelist.objects.filter(student=student)
            # Print or log to debug
            print(f"Student: {student.student_id}")
            print(f"Session: {session.id}")
            print(list(attendance_records_student.values()))

            # Filter attendance records for the specific session
            attendance_records_session = attendance_records_student.filter(session=session)
            print(attendance_records_session )
            if attendance_records_session:
                attendance_record = attendance_records_session.latest('marked_at')
                if attendance_record.present:
                    attendance_status = 'present'
                else:
                    attendance_status = 'absent'
            else:
                attendance_status = 'Absent'

        except Attendancelist.DoesNotExist:
            raise Attendancelist.DoesNotExist
        
        student_data = {
            'student_id': student.student_id,
            'username': student.userrole.username,
            'attendance_status': attendance_status
        }
        student_attendance.append(student_data)

    return student_attendance

@api_view(['GET'])
def batch_students_attendance_view(request, batch_id, id):
    students_attendance = get_students_with_attendance(batch_id, id)
    
    serialized_students = []
    for student_data in students_attendance:
        serialized_student = {
            'student_id': student_data['student_id'],
            'username': student_data['username'],
            'attendance_status': student_data['attendance_status']
        }
        serialized_students.append(serialized_student)

    return Response({'students': serialized_students})

'''
#to view all sessions created
@api_view(['GET'])
def batch_students_attendance_view(request, batch_id, session_date):
    students_attendance = get_students_with_attendance(batch_id, session_date)
    
    serialized_students = []
    for student_data in students_attendance:
        serialized_student = {
            'student_id': student_data['student_id'],
            'username': student_data['username'],
            'attendance_status': student_data['attendance_status']
        }
        serialized_students.append(serialized_student)

    return Response({'students': serialized_students})'''


#to view all sessions created
@api_view(['GET'])
def get_sessions(request):
    sessions = Session.objects.all()
    serializer = SessionSerializer(sessions, many=True)
    return Response(serializer.data)

#to view paticular batch sessions
@api_view(['GET'])
def get_sessions_by_batch(request, batch_id,session_type):
    try:
        batch = Batch.objects.get(batch_id=batch_id)
        sessions = Session.objects.filter(batch=batch,session_type=session_type)
        serializer = SessionSerializers(sessions, many=True)
        return Response(serializer.data)
    except Batch.DoesNotExist:
        return Response({"error": "Batch not found"}, status=HTTP_404_NOT_FOUND)
    


#for create the Lab session to paticular batch
@api_view(['POST'])
def create_lab_sessions(request):
    serializer = SessionSerializer(data=request.data)
     # Assuming session_date is passed in the request
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Session is created'}, status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    

'''{
    "batch":"Dj-01",
     "session_date":"2024-07-17",
     "session_type":"Lab"
     
}'''


       
    

#to mark attendance
@api_view(['POST'])
def mark_attendance(request, batch_id):
       # Extract data from the request
    data = request.data.copy()
    data['batch'] = batch_id  # If needed to add batch_number to the request data

    # Create a serializer instance with the request data
    serializer = AttendanceSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()  # Save the validated data
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)# Extract and validate session data
    
    

    
''' {
    "student": "Dj-02-2",
    "session":1,
    "present": true,
    "marks": 85.00,
    "marked_at": "2024-07-29"
}'''


#to get the attendance of a student in paticular batch  for paticular session
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    try:
        student = request.user.student_tabel  # Assuming 'student_tabel' is related name
        batch = student.batch
        sessions = Session.objects.filter(batch=batch)
        
        student_attendance = []
        
        for session in sessions:
            try:
                attendance = Attendancelist.objects.get(student=student, session=session)
                # serializer = AttendanceSerializer(attendance)
                
                present = 'present' if attendance.present else 'absent'
                marks = attendance.marks
            except Attendancelist.DoesNotExist:
                present = 'absent'
                marks = 0
                # serializer = None

            student_data = {
                'student_id': student.student_id,
                'username': student.userrole.username,
                'session_type': session.session_type,
                'present': present,
                'marks': marks
            }

            student_attendance.append(student_data)

        return Response(student_attendance, status=200)
    
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=404)
    except Session.DoesNotExist:
        return Response({"error": "Sessions not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def studentdetails(request):
    try:
        # student=Student_tabel.objects.get(mobile_no=mobile_no)
        student = request.user.student_tabel
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializerss(student)
        return Response(serializer.data, status=HTTP_200_OK)

    if request.method in ['PUT']:
        data = request.data
        serializer = StudentprofileSerializerres(student,data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    return Response({"error": "Method not allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)
{     
     "Gender": "Male",
      "address": "PUNE",
      "Qulification": "B.Tech",
      "batch": "Dj-02"
}

#to count the sessions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_session_data(request):
    user = request.user 
    try:
        student = Student_tabel.objects.get(userrole=user)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    lab_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='Lab'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = lab_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in lab_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
    
    
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
       

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekelytest_session_data(request):
    user = request.user 
    try:
        student = Student_tabel.objects.get(userrole=user)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    weekelytest_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='Weekelytest'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = weekelytest_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in weekelytest_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
        

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekelymock_session_data(request):
    user = request.user 
    try:
        student = Student_tabel.objects.get(userrole=user)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    weekelymock_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='WeekelyMock'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = weekelymock_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in weekelymock_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
  
    
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
        

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)



#to get the balance _due fee students in a batch
@api_view(['GET'])
def get_students_with_outstanding_fees(request, batch_id,status):
     
    # Validate batch_number
     if not batch_id:
        return Response({'error': 'Batch number is required'}, status=400)

    # Filter students by batch number
     students_query = Student_tabel.objects.filter(batch_id=batch_id)
     if status=='ALL':
         students_query = students_query
    # Apply fee status filter if not 'ALL'
     if status == 'paid':
        students_query = students_query.filter(fee__fee_status='paid')
     elif status == 'pending':
        students_query = students_query.filter(fee__fee_status='pending')
    
    # Serialize the data
     serializer = StudentSerilizers(students_query, many=True)
     return Response(serializer.data)



# to delete the students

@api_view(['GET','DELETE'])
def Deletestudent(request,mobile_no):
    studentobj = Student_tabel.objects.get(mobile_no=mobile_no)
    user = studentobj.userrole
    if request.method == 'GET':
        seriaObj = StudentSerializerres(studentobj)
        return Response(seriaObj.data,status=HTTP_200_OK)
    
    if request.method == 'DELETE':
        user.delete()
        studentobj.delete()
        return Response(status = HTTP_200_OK)
    
#login for student
@api_view(['POST'])
def student_auth_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        if user.user_type == '3':  # Check if the user is a student
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Not authenticated as student.'}, status=HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid credentials.'}, status=HTTP_400_BAD_REQUEST)
    


def attendance_view(request):
    student = request.user.student_tabel
      # Replace with the correct way to access the logged-in student's profile
    sessions = Session.objects.get(session_type='Lab')  # Adjust this query based on your requirements
    grouped_records = []
    for session in sessions:
        attendance_records=Attendancelist.objects.get(student=student, session=session)
        grouped_records.append(attendance_records)

    return Response(grouped_records,status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_logout(request):
    try:
        # Retrieve the token from the request
        token = Token.objects.get(user=request.user)
        
        # Delete the token to log the user out
        token.delete()
        
        return Response({'message': 'Successfully logged out'}, status=HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'error': 'No token found for this user'}, status=HTTP_404_NOT_FOUND)
    

@api_view(['GET', 'POST'])
def add_task(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        parser_classes = (MultiPartParser, FormParser)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    



@api_view(['GET'])
def get_tasks_by_batch(request, batch_id):
    """
    List all tasks or filter tasks based on batch_id.
    """
    tasks = Task.objects.filter(batch_id=batch_id)
    
    if not tasks.exists():
        return Response({"error": "No tasks found for this batch"}, status=404)
    
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_daily_video(request):
    serializer = DailyVideoSerializer(data=request.data)
    if serializer.is_valid():
         # Remove this line since upload_date is auto-managed by the model
        # video_date = serializer.validated_data['upload_date']

        #video_date = serializer.validated_data['upload_date']
        
        # Check if a video with the same date already exists
        #existing_video = DailyVideo.objects.filter(upload_date__date=video_date, batch_id=serializer.validated_data['batch']).first()
        #if existing_video:
           # return Response({'error': 'A video with the same date and batch already exists'}, status=HTTP_400_BAD_REQUEST)
        
        # Save the new video
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_daily_video(request):
    date_str = request.query_params.get('date')
    batch_id = request.query_params.get('batch')
    
    if date_str and batch_id:
        try:
            date = parse_datetime(date_str)
            if date is None:
                raise ValueError("Invalid date format")
            
            videos = DailyVideo.objects.filter(upload_date__date=date, batch_id=batch_id)
            serializer = DailyVideoSerializer(videos, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Missing date or batch parameter'}, status=HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def updatestudentget(request,mobile_no):
    try:
        studentobj = Student_tabel.objects.get(mobile_no=mobile_no)
    except Student_tabel.DoesNotExist:
        return Response({'error': 'Student not found'}, status=HTTP_404_NOT_FOUND)

    
    if request.method == 'GET':
        seriaObj = StudentSerilizer(studentobj)
        return Response(seriaObj.data,status=HTTP_200_OK)
    

    
@api_view(['PUT'])
def updatestudent(request, mobile_no):
    try:
        studentobj = Student_tabel.objects.get(mobile_no=mobile_no)
    except Student_tabel.DoesNotExist:
        return Response({'error': 'Student not found'}, status=HTTP_404_NOT_FOUND)
    
    serializer = studentupdateSerializers(studentobj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Student updated successfully!'}, status=HTTP_200_OK)
    else:
        # Log serializer errors for debugging
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


    
'''
  {
    "username": "pradeep",
    "email": "pradeep@gmail.com",
    "mobile_no": "9876543295",
    "batch": "Dj-01",
    "amount_paid": "500.00",
    "fee_status": "paid",
    "total_amount":"1000.00"
}'''

    
'''
 {
    "username": "pradeep",
    "email": "pradeep@gmail.com",
    "mobile_no": 9876543295,
    "batch": "Dj-01",
    "Gender": "Female",
    "address": "Hydrabad",
    "Qulification":"B.tech"
}'''



@api_view(['GET'])
def notification_list(request):
    """
    Retrieve a list of notifications.
    """
    notifications = Notification.objects.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
def notification_create(request):
    """
    Create a new notification.
    """
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def mark_notification_as_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk)
        notification.read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)




@api_view(['GET'])
def placementnotifi_list(request):
    """
    Retrieve a list of notifications.
    """
    notifications = Placement.objects.all()
    serializer = PlacementSerializer(notifications, many=True)
    return Response(serializer.data, status=HTTP_200_OK)




@api_view(['POST'])
def placementnotifi_create(request):
    """
    Create a new notification.
    """
    serializer =PlacementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def count_staff(request):
    staff_count = Staff_tabel.objects.count()
    return JsonResponse({'staff_count': staff_count})

@api_view(['GET'])
def count_students(request):
    student_count = Student_tabel.objects.count()
    return JsonResponse({'student_count': student_count})

@api_view(['GET'])
def student_graph_data(request):
    today = datetime.date.today()
    past_month = today - datetime.timedelta(days=30)
    data = [
        {'date': (past_month + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
         'count': Student_tabel.objects.filter(created_at__date=past_month + datetime.timedelta(days=i)).count()}
        for i in range(31)
    ]
    return JsonResponse(data, safe=False)

@api_view(['GET'])
def staff_graph_data(request):
    today = datetime.date.today()
    past_month = today - datetime.timedelta(days=30)
    data = [
        {'date': (past_month + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
         'count': Staff_tabel.objects.filter(created_at__date=past_month + datetime.timedelta(days=i)).count()}
        for i in range(31)
    ]
    return JsonResponse(data, safe=False)





#staff viewing student performance
@api_view(['GET'])
def lab_performance(request,mobile_no): 
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    lab_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='Lab'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = lab_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in lab_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
    
    
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
       

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)


@api_view(['GET'])
def weekely_test_performance(request,mobile_no): 
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    lab_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='Weekelytest'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = lab_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in lab_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
    
    
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
       

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)


@api_view(['GET'])
def weekely_mock_performance(request,mobile_no): 
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no)
    except Student_tabel.DoesNotExist:
        return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)
    
    # Query lab sessions for the student's batch
    lab_sessions = Session.objects.filter(
        batch=student.batch,
        session_type='WeekelyMock'
    )
    
    # Calculate total lab sessions
    total_lab_sessions = lab_sessions.count()
    
    # Initialize counters
    days_present = 0
    days_absent = 0
    
    # Check attendance for each lab session
    for session in lab_sessions:
        # Check if attendance record exists for this session and student
        attendance_record = Attendancelist.objects.filter(
            student=student,
            session=session,
              # Assuming you want to check today's attendance
        ).first()
        
        if attendance_record:
            if attendance_record.present:
                days_present += 1
            else:
                days_absent += 1
        else:
            days_absent += 1  # No attendance record found means absent
    
    
    # Prepare response data
    response_data = {
        'total_lab_sessions': total_lab_sessions,
        'days_present': days_present,
        'days_absent': days_absent,
       

    }
    
    # Serialize data and return response
    serializer = LabSessionDataSerializer(response_data)
    return Response(serializer.data)


@api_view(['GET'])
def staff_view_weekelyTest(request,mobile_no):
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no)  # Assuming you have set up a way to access the logged-in student
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="Weekelytest")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'session_type':attendance.session.session_type,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def staff_attendance_view_Lab(request,mobile_no):
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no) # Assuming you have set up a way to access the logged-in student
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="Lab")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'session_type':attendance.session.session_type,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def staff_attendance_view_WeekelyMock(request,mobile_no):
    try:
        student = Student_tabel.objects.get(mobile_no=mobile_no)  
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="WeekelyMock")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'session_type':attendance.session.session_type,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    




@api_view(['DELETE'])
def DeleteAttendence(request, session ,student):
    Attendence = Attendancelist.objects.get(session=session,student=student)
    
    if request.method == 'DELETE':
        
        Attendence.delete()
        return Response(status = HTTP_200_OK)
    



#to get the attendance of a student in paticular batch  for paticular session
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance_view_weekelyTest(request):
    try:
        student = request.user.student_tabel  # Assuming you have set up a way to access the logged-in student
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="Weekelytest")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance_view_Lab(request):
    try:
        student = request.user.student_tabel  # Assuming you have set up a way to access the logged-in student
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="Lab")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'session_type':attendance.session.session_type,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance_view_WeekelyMock(request):
    try:
        student = request.user.student_tabel  # Assuming you have set up a way to access the logged-in student
        batch = student.batch
        sessions = Session.objects.filter(batch=batch,session_type="WeekelyMock")  # Get all sessions for the student’s batch

        # Create a dictionary to hold the attendance records
        attendance_dict = {}

        for session in sessions:
            # Check if an attendance record exists for the student and session
            attendance = Attendancelist.objects.filter(student=student, session=session).first()
            if attendance:
                # Record found
                attendance_dict[session.id] = {

                    'session_date':attendance.session.session_date,
                    'session_type':attendance.session.session_type,
                    'present': attendance.present,
                    'marks': attendance.marks
                }
            else:
                # Record not found
                attendance_dict[session.id] = {
                    'session_date': session.session_date,
                    'present': False,
                    'marks': 0
                }

        # Serialize the sessions
        

        # Prepare the data for the response
        
        return Response(attendance_dict,status=200 )
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
 



