from rest_framework import serializers
from.models import Student_tabel,Batch,Fee,Attendancelist,Session,Task,DailyVideo,Notification,Placement
from django.contrib.auth.hashers import make_password
from staffportal.models import User
from django.utils import timezone


class FeeSerializer(serializers.ModelSerializer):
     balance_due = serializers.SerializerMethodField()
     class Meta:
        model = Fee
        fields = ['amount_paid','fee_status','total_amount','balance_due']
     def create(self, validated_data):
        student = self.context['student']
        amount_paid =validated_data.get('amount_paid')
        fee_status= validated_data.get('fee_status')
        total_amount = validated_data.get('total_amount')
        if total_amount is None:
            raise serializers.ValidationError({'total_amount': 'This field is required.'})

        # Create Fee instance with provided total_amount
        fee_instance = Fee.objects.create(
            student=student,
            total_amount=total_amount,
            amount_paid=amount_paid,  # Initial amount_paid should be 0
            fee_status=fee_status  # Initial status should be 'pending'
        )
        return fee_instance
     def get_balance_due(self, obj):
        return obj.balance_due
     

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        extra_kwargs = {'password': {'write_only': True}}
          
 

class StudentSerilizer(serializers.ModelSerializer):
    userrole = UserSerializer()
    fee = FeeSerializer()
    class Meta:
        model=Student_tabel
        fields=['userrole','mobile_no','batch','fee']
    def validate(self,data):
        if data['mobile_no']<999999999 or data['mobile_no']>9999999999:
            raise serializers.ValidationError({'error':'mobile number must be 10 digits'})
        return data
    def validate(self, data):
        if 'mobile_no' in data:
            mobile_no = data['mobile_no']
            # Check if a Student_tabel with the given mobile number already exists
            if Student_tabel.objects.filter(mobile_no=mobile_no).exists():
                raise serializers.ValidationError({"mobile_no": "Student with this mobile number is already registered."})
        return data
    def create(self, validated_data):
        user_data = validated_data.pop('userrole')
        fee_data = validated_data.pop('fee')
        user = User.objects.create(username=user_data['username'], email=user_data['email'])
        student = Student_tabel.objects.create(userrole=user, **validated_data)

        # Create Fee object using FeeSerializer, passing context with student instance
        fee_serializer = FeeSerializer(data=fee_data, context={'student': student})
        fee_serializer.is_valid(raise_exception=True)
        fee = fee_serializer.save()

        student.fee = fee  # Link the created Fee instance to the Student_tabel instance
        # student.save()

        return student
    
class StudentUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = Student_tabel
        fields = ['password','address', 'Qulification', 'Gender', 'Image']

    def update(self, instance, validated_data):
       user = instance.userrole
       password = validated_data.pop('password', None)
       if password:
            if user.password and user.check_password(password):
                raise serializers.ValidationError({'password': 'Password has already been set and cannot be updated.'})
            user.set_password(password)
            user.save()
        
       instance.address = validated_data.get('address', instance.address)
       instance.Qulification = validated_data.get('Qulification', instance.Qulification)
       instance.Gender = validated_data.get('Gender', instance.Gender)
       instance.Image = validated_data.get('Image', instance.Image)
       instance.save()
       return instance


class StudentSerializerss(serializers.ModelSerializer):
     userrole = UserSerializer()
     class Meta:
        model = Student_tabel
        fields = '__all__' 

class StudentprofileSerializerres(serializers.ModelSerializer):
    class Meta:
        model=Student_tabel
        fields=['mobile_no','address', 'Qulification', 'Gender', 'Image','resume']


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student_tabel.objects.all())
    class Meta:
        model = Attendancelist
        fields = ['student', 'session', 'present', 'marked_at', 'marks']



class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['batch', 'session_date', 'session_type']
    def validate(self, data):
        # Check if a session with the same batch, date, and type already exists
        batch = data['batch']
        session_date = data['session_date']
        session_type = data['session_type']

        existing_session = Session.objects.filter(
            batch=batch,
            session_date=session_date,
            session_type=session_type
        ).exists()

        if existing_session:
            raise serializers.ValidationError("Session already exists for this batch, date, and type.")
         # Check if the session_date is in the future
        if session_date > timezone.now().date():
            raise serializers.ValidationError("The session date cannot be in the future.")

        return data
    
class SessionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
    
class StudentSerializerres(serializers.ModelSerializer):
    username = serializers.CharField(source='userrole.username')
    email = serializers.EmailField(source='userrole.email')
    class Meta:
        model = Student_tabel
        fields = ['student_id', 'username','email', 'mobile_no', 'batch', 'Gender', 'address', 'Image', 'Qulification']

class LabSessionDataSerializer(serializers.Serializer):
    total_lab_sessions = serializers.IntegerField()
    days_present = serializers.IntegerField()
    days_absent = serializers.IntegerField()     
# @api_view(['POST'])
# def add_marks(request):
#     try:
#         serializer = MarksSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# urlpatterns = [
#     path('add_marks/', views.add_marks, name='add_marks'),
#     # Other paths...
# ]


  # Use the same Task model
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'task_type', 'content', 'image', 'batch']


        

class DailyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyVideo
        fields = ['title', 'video_file', 'batch', 'upload_date']
        # Add extra validation if needed
        extra_kwargs = {
            'upload_date': {'required': True}  # Make sure upload_date is required if it needs to be provided
        }



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = '__all__'






'''class studentupdateSerializers(serializers.ModelSerializer):
    # Flatten the user-related fields directly in the StaffSerializer
    username = serializers.CharField(source='userrole.username')
    email = serializers.EmailField(source='userrole.email')
    amount_paid = serializers.DecimalField(source='fee.amount_paid', max_digits=10, decimal_places=2, default=0)
    fee_status = serializers.CharField(source='fee.fee_status', default='pending')
    total_amount = serializers.DecimalField(source='fee.total_amount', max_digits=10, decimal_places=2)
    
    class Meta:
        model = Student_tabel
        fields = [ 'username', 'email', 'mobile_no','batch', 'amount_paid', 'fee_status', 'total_amount']

    def validate(self, data):
        # Extract user data from the flattened fields
        username = data.get('userrole', {}).get('username', self.instance.userrole.username)
        email = data.get('userrole', {}).get('email', self.instance.userrole.email)
        
        # Check for uniqueness of username and email, excluding the current instance
        if User.objects.exclude(pk=self.instance.userrole.pk).filter(username=username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        if User.objects.exclude(pk=self.instance.userrole.pk).filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        
        return data

    def update(self, instance, validated_data):
        # Extract and update the related User instance
        user_data = validated_data.pop('userrole', {})
        user_instance = instance.userrole

        # Update user instance fields
        user_instance.username = user_data.get('username', user_instance.username)
        user_instance.email = user_data.get('email', user_instance.email)
       
        user_instance.save()
        fee_data = validated_data.pop('fee', {})
        if fee_data:
            fee_instance, created = Fee.objects.get_or_create(student=instance)
            fee_instance.amount_paid = fee_data.get('amount_paid', fee_instance.amount_paid)
            fee_instance.fee_status = fee_data.get('fee_status', fee_instance.fee_status)
            fee_instance.total_amount = fee_data.get('total_amount', fee_instance.total_amount)
            fee_instance.save()
        # Update staff instance fields
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        
        instance.batch = validated_data.get('batch', instance.batch)
        instance.save()
        return instance'''



class studentupdateSerializers(serializers.ModelSerializer):
    # Flatten the user-related fields directly in the StaffSerializer
    username = serializers.CharField(source='userrole.username')
    email = serializers.EmailField(source='userrole.email')
    amount_paid = serializers.DecimalField(source='fee.amount_paid', max_digits=10, decimal_places=2, default=0)
    fee_status = serializers.CharField(source='fee.fee_status', default='pending')
    total_amount = serializers.DecimalField(source='fee.total_amount', max_digits=10, decimal_places=2)
    
    class Meta:
        model = Student_tabel
        fields = [ 'username', 'email', 'mobile_no','batch', 'amount_paid', 'fee_status', 'total_amount']

    def validate(self, data):
        # Extract user data from the flattened fields
        username = data.get('userrole', {}).get('username', self.instance.userrole.username)
        email = data.get('userrole', {}).get('email', self.instance.userrole.email)
        
        # Check for uniqueness of username and email, excluding the current instance
        if User.objects.exclude(pk=self.instance.userrole.pk).filter(username=username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        if User.objects.exclude(pk=self.instance.userrole.pk).filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        
        return data

    def update(self, instance, validated_data):
        # Extract and update the related User instance
        user_data = validated_data.pop('userrole', {})
        user_instance = instance.userrole

        # Update user instance fields
        user_instance.username = user_data.get('username', user_instance.username)
        user_instance.email = user_data.get('email', user_instance.email)
       
        user_instance.save()
        fee_data = validated_data.pop('fee', {})
        if fee_data:
            fee_instance, created = Fee.objects.get_or_create(student=instance)
            fee_instance.amount_paid = fee_data.get('amount_paid', fee_instance.amount_paid)
            fee_instance.fee_status = fee_data.get('fee_status', fee_instance.fee_status)
            fee_instance.total_amount = fee_data.get('total_amount', fee_instance.total_amount)
            fee_instance.save()
        # Update staff instance fields
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        
        instance.batch = validated_data.get('batch', instance.batch)
        instance.save()
        return instance
    





class StudentSerilizers(serializers.ModelSerializer):
    userrole = UserSerializer()
    fee = FeeSerializer()
    class Meta:
        model=Student_tabel
        fields=['userrole','mobile_no','batch','fee','student_id']
    def validate(self,data):
        if data['mobile_no']<999999999 or data['mobile_no']>9999999999:
            raise serializers.ValidationError({'error':'mobile number must be 10 digits'})
        return data
    def validate(self, data):
        if 'mobile_no' in data:
            mobile_no = data['mobile_no']
            # Check if a Student_tabel with the given mobile number already exists
            if Student_tabel.objects.filter(mobile_no=mobile_no).exists():
                raise serializers.ValidationError({"mobile_no": "Student with this mobile number is already registered."})
        return data
    def create(self, validated_data):
        user_data = validated_data.pop('userrole')
        fee_data = validated_data.pop('fee')
        user = User.objects.create(username=user_data['username'], email=user_data['email'])
        student = Student_tabel.objects.create(userrole=user, **validated_data)

        # Create Fee object using FeeSerializer, passing context with student instance
        fee_serializer = FeeSerializer(data=fee_data, context={'student': student})
        fee_serializer.is_valid(raise_exception=True)
        fee = fee_serializer.save()

        student.fee = fee  # Link the created Fee instance to the Student_tabel instance
        # student.save()

        return student