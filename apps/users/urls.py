from django.urls import path
from users import views


urlpatterns = [
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
]