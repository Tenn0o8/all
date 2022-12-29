from attr import field
from rest_framework import serializers
from .models import User, item, location

# using modelserializer to turn json file received from postman to django model
class UserSerializer(serializers.ModelSerializer):
  class Meta: 
    model = User
    fields = ['id','name','email','password']
    # to not return password in json file output( res.data)
    extra_kwargs = {
      'password':{'write_only':True}
    }
    depth = 1
    
  # to hash the password in db, set_password is provided by django
  def create(self, validated_data):
    password = validated_data.pop('password',None)
    instance = self.Meta.model(**validated_data)
    if password is not None:
      instance.set_password(password)
    instance.save()
    return instance

class ItemRegisterSerializer(serializers.ModelSerializer):
  class Meta: 
    model = item
    fields = ['name','IMEI','owner']
    # depth = 1

class LocationSerializer(serializers.ModelSerializer):
  class Meta: 
    model = location
    fields = ['lat','lng','original_item']

    