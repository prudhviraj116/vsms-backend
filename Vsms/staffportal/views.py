from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes,authentication_classes
# import json
from.models import Staff_tabel,Staff_depatments,User
# from rest_framework.authtoken.models import Token
from.serilizer import staffSerializer,Staffdepartmentserilizer,Forgetpasswordserilizer,staffSerializers,Staffdepartmentpostserilizer,staffupdateSerializers,AdminSerializer,UserSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .permissions import IsStaff, IsStudent, IsStaffOrStudent
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_204_NO_CONTENT
import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache

    

def demo(request):
    return HttpResponse('staffprotal')



@api_view(['POST'])
def staff_auth_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        if user.user_type == '2':  # Check if the user is staff
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Not authenticated as staff.'}, status=HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid credentials.'}, status=HTTP_400_BAD_REQUEST)
    

'''{
    "username": "pradeep",
    "password": "ThankGod@123"
}'''
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def Staffget(request):
    staffdata=Staff_tabel.objects.all()
    staffdetails=staffSerializer(staffdata,many=True)
    return Response(staffdetails.data,status=HTTP_200_OK)


@api_view(['POST'])

def registerstaff(request):
    staffobj=staffSerializer(data=request.data)
    if staffobj.is_valid():
        print(staffobj)
        staffins=staffobj.save()
        token, created=Token.objects.get_or_create(user=staffins.userrole)
        return Response({'token': token.key},status=HTTP_201_CREATED)
    else:
        return Response(staffobj.errors,status=HTTP_400_BAD_REQUEST)

'''{
    "userrole": {
        "username": "Shalini",
        "email": "Shalini@gmail.com"
    },
    "mobile": 8796543214,
    "Gender": "Female",
    "Image": null,
    "address": "Chennai",
    "desgination": 1
}'''


@api_view(['POST'])

def departmentpost(request):
    depobj=Staffdepartmentpostserilizer(data=request.data)
    if depobj.is_valid():
        depobj.save()
        
        return Response({'message':'staffdepartmentcreated'},status=HTTP_201_CREATED)
    else:
        return Response(depobj.errors,status=HTTP_400_BAD_REQUEST)
'''{
"Departmentname":"HR"
}'''

@api_view(['GET'])
def get_departments(request):
    departments = Staff_depatments.objects.all()
    serializer = Staffdepartmentpostserilizer(departments, many=True)
    return Response(serializer.data, status=HTTP_200_OK)
    

    
@api_view(['GET'])
def Staffdepartments(request):
    staffdepdata=Staff_depatments.objects.all()
    staffdatalist=Staffdepartmentserilizer(staffdepdata,many=True)
    return Response(staffdatalist.data,status=HTTP_200_OK)

def generate_otp():
    otp=random.randint(10000, 99999)
    return otp

def send_otp_email(to_email, otp):
    """Send the OTP to the specified email address."""
    subject = 'Your OTP Code'
    message = f'Hello!,\n The OTP for reseting your VCUBE POrtal is\nYour OTP code is: {otp}'
    from_email=settings.EMAIL_HOST_USER
    to_email=[to_email]
    send_mail(subject, message, from_email,to_email)


def create_and_send_otp(email):
    """Generate an OTP, store it in the cache, and send it via email."""
    otp = generate_otp()
    cache.set(email, otp, timeout=300)#, timeout=300)  # Store OTP in cache for 5 minutes
    send_otp_email(email, otp)

def validate_otp(email, otp):
    """Validate the OTP provided by the user."""
    cached_otp = cache.get(email)
    print(f"Debug - Cached OTP: {cached_otp}, Provided OTP: {otp}")  # Debug log
    
    # Ensure both cached OTP and provided OTP are strings for comparison
    if cached_otp and str(cached_otp) == str(otp):
        cache.delete(email)  # Delete OTP after successful validation
        return True
    return False


"""{
 "email":"Jageesha.nadella@gmail.com",
 "otp":
}"""

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    print(f"Debug - Received Email: {email}, OTP: {otp}")  # Debug log

    if not email or not otp:
        return Response({'error': 'Email and OTP are required.'}, status=HTTP_400_BAD_REQUEST)

    if validate_otp(email, otp):
        return Response({'message': 'OTP is valid.'}, status=HTTP_200_OK)
    else:
        return Response({'error': 'Invalid or expired OTP.'}, status=HTTP_400_BAD_REQUEST)




    

@api_view(['POST'])
def verifyemail(request):
    email=request.data.get('email')
    try:
        userobj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User with this email not found"}, status=HTTP_404_NOT_FOUND)
    if userobj:
        create_and_send_otp(email)
        return Response({'message': 'OTP send to mail'}, status=HTTP_201_CREATED)

    

'''{
 "email":"Jageesha.nadella@gmail.com"
}'''

    
@api_view(['PUT'])
def change_password(request, email):
    try:
        userobj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=HTTP_404_NOT_FOUND)

    serializer = Forgetpasswordserilizer(userobj, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password changed successfully.'}, status=HTTP_200_OK)
    
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


'''{
 "password":"Newpassword123"
}'''



@api_view(['GET'])
@permission_classes([IsAuthenticated,IsStaff])

def stafflogindetails(request):
    try:
        staff = request.user.staff_tabel
        serializer = staffSerializers(staff)  # Use your serializer to serialize the staff data
       
        return Response(serializer.data, status=200)
    except Staff_tabel.DoesNotExist:
        return Response({"error": "Staff not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def staff_logout(request):
    try:
        # Delete the token to log the user out
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out.'}, status=HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)






@api_view(['GET'])
def updatestaffapiget(request,mobile):
    staffobj = Staff_tabel.objects.get(mobile=mobile)
    
    
    if request.method == 'GET':
        seriaObj =staffSerializer(staffobj)
        # username=seriaObj.data['userrole']['username']
        
        return Response(seriaObj.data,status=HTTP_200_OK)
@api_view(['PUT'])
def updatestaffapi(request,mobile):
    staffobj = Staff_tabel.objects.get(mobile=mobile)    
    if request.method == 'PUT':
       

       seriaObj=staffupdateSerializers(staffobj,data=request.data)
       if seriaObj.is_valid() == True:
        
           seriaObj.save()
           
           return Response(status = HTTP_200_OK)
       else:
           
           return Response(seriaObj.errors,status = HTTP_400_BAD_REQUEST)


'''{ 
    "username": "Shalini",       
    "email": "Shalini@gmail.com",                
    "mobile": "1234567890",           
    "address": "chennai",         
    "Gender": "Female",                   
    "desgination": 1 
}'''


'''{ 
    "username": "Shalini",       
    "email": "Shalini@gmail.com",                
    "mobile": "1234567890",           
    "address": "chennai",         
    "Gender": "Female",                   
    "desgination": 1 
}'''
    


@api_view(['GET'])
#@authentication_classes([TokenAuthentication])
#@permission_classes([IsAuthenticated])
def get_all_staff_details(request):
    try:
        # Retrieve all staff members
        staff_data = Staff_tabel.objects.all()
        serializer = staffSerializers(staff_data, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

    
@api_view(['GET'])
def count_staff(request):
    staff_count = Staff_tabel.objects.count()
    return JsonResponse({'staff_count': staff_count})


'''
@api_view(['POST'])
def registerAdmin(request):
    adminobj=AdminSerilizer(data=request.data)
    if adminobj.is_valid():
        print(adminobj)
        adminins=adminobj.save()
        token, created=Token.objects.get_or_create(user=adminins.userrole)
        return Response({'token': token.key},status=HTTP_201_CREATED)
    else:
        return Response(adminobj.errors,status=HTTP_400_BAD_REQUEST)'''

'''
{
    "userrole": {
        "username": "Vcubeadmin1",
        "email": "Vcubeadmin1@gmail.com",
       "password":"Vcubeadmin@123",
       "confirm_Password":""Vcubeadmin@123"
}
}'''

@api_view(['POST'])
def registerAdmin(request):
    admin_serializer = AdminSerializer(data=request.data)
    if admin_serializer.is_valid():
        admin_instance = admin_serializer.save()
        token, created = Token.objects.get_or_create(user=admin_instance.userrole)
        return Response({'token': token.key}, status=HTTP_201_CREATED)
    else:
        return Response(admin_serializer.errors, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def admin_auth_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        if user.user_type == '1':  # Check if the user is an admin
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Not authenticated as admin.'}, status=HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid credentials.'}, status=HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    except (AttributeError, Token.DoesNotExist):
        return Response({'error': 'No active session found.'}, status=HTTP_400_BAD_REQUEST)