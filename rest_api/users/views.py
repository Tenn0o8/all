from requests import delete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_api.settings import SECRET_KEY
from .serializers import UserSerializer, ItemRegisterSerializer
from .models import User, item, location
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from datetime import datetime, timedelta
from haversine import haversine, Unit


now = datetime.now()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # serializer.errors
        return Response(serializer.data)

# login user
# customize the ref and access token to have name and email key


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['email'] = user.email

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# remember to delete the access and ref token in frontend


class LogoutUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')

        refreshToken = request.data['refreshToken']
        try:
            refreshContent = jwt.decode(
                refreshToken, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        if refreshContent['token_type'] == 'refresh':
            try:
                token = RefreshToken(refreshToken)
                token.blacklist()
                # accessToken.blacklist()
                return Response({'messages': 'successfully logout'})
            except:
                return Response({'messages': 'cannot logout, try againt later'})
        else:
            return Response({'messages': 'cannot logout'})

# delete access or reftoken or not is still okay


class LogoutOnAllDevices(APIView):
    def post(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        # we'll blacklist all outstanding token
        tokens = OutstandingToken.objects.filter(user_id=userInfo['user_id'])
        for token in tokens:
            new_token = BlacklistedToken.objects.get_or_create(token=token)

        return Response("Logout on alldevices")


class getItemsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        owner = User.objects.get(id=userInfo['user_id'])
        items = owner.owner.all()
        content = [i.json() for i in items]
        # jsoncontent = json.dumps(content)
        return Response(content)


class getItemByID(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        owner = User.objects.get(id=userInfo['user_id'])
        item = owner.owner.get(id=id)
        location = item.item.order_by('-id')[:2]
        content = {
            'id': item.id,
            'name': item.name,
            'condition': item.condition,
            'IMEI': item.IMEI,
            'location': [i.json() for i in location]
        }

        return Response(content)


class registerItems(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        try:
            payload = {
                'name': request.data['name'],
                'IMEI': request.data['IMEI'],
                'owner': userInfo['user_id'],
            }
        except:
            return Response({
                'messages': 'Check your JSON again'
            })
        serializer = ItemRegisterSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class changeItems(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        try:
            payload = {
                'name': request.data['name'],
                'condition': request.data['condition'],
                'id': request.data['id'],
            }
        except:
            return Response({
                'messages': 'Check your JSON again'
            })
        owner = User.objects.get(id=userInfo['user_id'])
        item = owner.owner.get(id=payload['id'])
        if not item:
            return Response({
                'messages': 'You do not have access to this device'
            })
        #execute when change the dev condtion
        #......
        item.name = payload['name']
        item.condition = payload['condition']
        item.save()
        return Response({
            'messages': 'You have changed your device'
        })

    def delete(self, request):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        try:
            payload = {
                'id': request.data['id'],
            }
        except:
            return Response({
                'messages': 'Check your JSON again'
            })
        owner = User.objects.get(id=userInfo['user_id'])
        item = owner.owner.get(id=payload['id'])
        item.delete()
        return Response({
            'messages': 'You have deleted your device'
        })

class history(APIView):
    permission_classes = [IsAuthenticated]
    # id is the id of the device
    def get(self, request, id):
        accessToken = request.headers['Authorization']
        # remove the bearer
        tmp = accessToken.split()
        accessToken = " ".join(tmp[1:])
        try:
            userInfo = jwt.decode(accessToken, SECRET_KEY,
                                  algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated !')
        owner = User.objects.get(id=userInfo['user_id'])
        item = owner.owner.get(id=id)
        location_list = item.item.order_by('-id')[:200]
        compressed_list = []
        for i in location_list:
            if compressed_list == []:
                compressed_list.append(i.json())
            else:
                prev = compressed_list[-1]
                i_pos = (i.lat, i.lng)
                prev_pos = (prev['lat'], prev['lng'])
                # distance in meter, default is in kilometer
                distance = haversine(i_pos, prev_pos, unit=Unit.METERS)
                # the list is backward
                time_gap = (prev['timestamp']-i.timestamp)
                time_delta = timedelta(minutes=30)
                if (time_gap > time_delta):
                    compressed_list.append(i.json())
                elif (distance > 10 and time_gap> timedelta(minutes = 5)):
                    compressed_list.append(i.json())
        return Response(compressed_list)
