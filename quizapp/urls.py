from django.urls import path
from .views import *

#Create here your quizapp urls

app_name = 'quizapp'
urlpatterns= [
    path('',index,name='index'),

    path('adm/levels',LevelView.as_view(),name= 'level_list' ),
    path('adm/add-level',LevelCreateView.as_view(),name='level_add'),
    path('adm/levels/<int:pk>',LevelDetailView.as_view(),name= 'level_datail' ),

    path('adm/questions',QuestionView.as_view(),name='question_list'),
    path('adm/add-question',QuestionCreateView.as_view(),name='question_add'),
    path('adm/questions/<int:pk>',QuestionDetailView.as_view(),name='question_detail'),

    path('adm/user-level-progress',UserProgressAPI.as_view(),name='user_progress'),


    path('levels',ClientLevelListView.as_view(),name='client_level_list'),
    path('question/',ClientQuestionListView.as_view(),name='client_question_list'),
    path('user-progress/',ClientUserProgressView.as_view(),name='client_user_progress'),
    path('user-answers/', ClientUserAnswerView.as_view(), name='user-answer-list'),

    path('delete-user',DeleteUserAnswerView.as_view(),name='delete_user_answer'),

    
]