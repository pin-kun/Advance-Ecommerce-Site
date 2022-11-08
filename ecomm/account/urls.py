from django.urls import path
from account.views import *

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('activate/<uidb64>/<token>', ActivateAccountView.as_view(), name='activate'),
]