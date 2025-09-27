from django.urls import path
from . import views
from .views import MyTokenObtainPairView

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('signup1/', views.UserSignUpView.as_view(), name='signup'),
    path('signup2/', views.PersonSignUpView.as_view(), name='PersonSignUpView'),
    path('logout/', views.logout_view.as_view(),name='logout'),
    path('update_user_info/', views.update_user_info,name='update_user_info'),
    path('account/me/', views.current_user, name='current_user'),
    path('account/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('userinfo/', views.current_user,name='user_info'),
    # path('userinfo/update/', views.update_user,name='update_user'),
    # path('forgot_password/', views.forgot_password,name='forgot_password'),
    # path('reset_password/<str:token>', views.reset_password,name='reset_password'),
]