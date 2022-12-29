from django.urls import path
from .views import LogoutOnAllDevices, LogoutUser, MyTokenObtainPairView, RegisterView, changeItems, getItemsList, registerItems, getItemByID, history
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutUser.as_view()),
    path('logoutall/', LogoutOnAllDevices.as_view()),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('items/',getItemsList.as_view()),
    path('items/register/',registerItems.as_view()),
    path('items/change/',changeItems.as_view()),
    path('items/<str:id>/',getItemByID.as_view()),
    path('items/history/<str:id>/',history.as_view())
]

