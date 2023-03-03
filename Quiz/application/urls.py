from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import QuizCreateAPIView,QuizListAPIView, UserProfileAPIView, RegisterAPIView,QuizTakingAPIView,QuizResultAPIView,QuizAnalyticsAPIView
from .views import AdminUpdateView,AdminCreateView,AdminUserListAPIView



urlpatterns = [

    path('quizanalytics/',QuizAnalyticsAPIView.as_view(), name='quizanalytics'),
    path('quizresult/',QuizResultAPIView.as_view(), name='quizresult'),
    path('quiztaking/<int:quiz_id>',QuizTakingAPIView.as_view(), name='quiztaking'),
    path('listquiz/',QuizListAPIView.as_view(), name='quizlist-view'),
    path('createquiz/',QuizCreateAPIView.as_view(),name='createquiz'),
    path('userprofile/',UserProfileAPIView.as_view(),name='user-profile'),
    path('register/', RegisterAPIView.as_view(), name='register'),



    path('adminuserupdate/<int:id>', AdminUpdateView.as_view(), name='adminupdate'),
    path('adminusercreate/', AdminCreateView.as_view(), name='admincreate'),
    path('adminlistusers/',AdminUserListAPIView.as_view(),name='adminuserview'),
    








]