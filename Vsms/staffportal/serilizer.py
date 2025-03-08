from rest_framework import serializers
from.models import Staff_tabel,User,Staff_depatments,Admin_tabel
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)  # Hash the password
            user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # Handle password securely
        instance.save()
        return instance
    
class staffSerializer(serializers.ModelSerializer):
  userrole = UserSerializer()
  class Meta:
        model=Staff_tabel
        fields=['userrole','mobile','Gender','Image','address','desgination']

  def validate(self,data):
    if data['mobile']<999999999 or data['mobile']>9999999999:
        raise serializers.ValidationError({'error':'mobile number must be 10 digits'})
  
    return data
  def validate(self, data):
        if 'mobile_no' in data:
            mobile_no = data['mobile_no']
            # Check if a Student_tabel with the given mobile number already exists
            if Staff_tabel.objects.filter(mobile_no=mobile_no).exists():
                raise serializers.ValidationError({"mobile_no": "Student with this mobile number is already registered."})
        return data
  def create(self, validated_data):
        user_data = validated_data.pop('userrole')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        staff = Staff_tabel.objects.create(userrole=user, **validated_data)
        return staff

class staffSerializers(serializers.ModelSerializer):
  userrole = UserSerializer()
  class Meta:
        model=Staff_tabel
        fields='__all__'

class Staffdepartmentserilizer(serializers.ModelSerializer):
    class Meta:
        model=Staff_depatments
        fields="__all__"

class Staffdepartmentpostserilizer(serializers.ModelSerializer):
    class Meta:
        model=Staff_depatments
        fields=['Departmentname']

class Forgetpasswordserilizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['password']
        
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance





class staffupdateSerializers(serializers.ModelSerializer):
    # Flatten the user-related fields directly in the StaffSerializer
    username = serializers.CharField(source='userrole.username')
    email = serializers.EmailField(source='userrole.email')
    
    
    class Meta:
        model = Staff_tabel
        fields = [ 'username', 'email', 'mobile', 'address', 'Gender', 'Image', 'desgination']

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
        
        # Update staff instance fields
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.address = validated_data.get('address', instance.address)
        instance.Gender = validated_data.get('Gender', instance.Gender)
        instance.Image = validated_data.get('Image', instance.Image)
        instance.desgination = validated_data.get('desgination', instance.desgination)
        instance.save()
        return instance
    

class AdminSerializer(serializers.ModelSerializer):
    userrole = UserSerializer()

    class Meta:
        model = Admin_tabel
        fields = ['userrole']

    def create(self, validated_data):
        user_data = validated_data.pop('userrole')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        admin = Admin_tabel.objects.create(userrole=user, **validated_data)
        return admin