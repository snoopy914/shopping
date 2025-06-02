from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('courses/', views.course_list, name='course_list_alt'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # 강의 편집
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    
    # 레슨 관련 URL
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('course/<int:course_id>/lessons/', views.lesson_manager, name='lesson_manager'),
    
    # 유튜브 임베드 관리
    path('youtube-manager/', views.youtube_embed_manager, name='youtube_embed_manager'),
    path('youtube-preview/', views.youtube_preview, name='youtube_preview'),
    
    # 결제 관련 URL
    path('payment/<int:course_id>/', views.initiate_payment, name='initiate_payment'),
    path('payments/success/', views.payment_success, name='payment_success'),
    path('payments/fail/', views.payment_fail, name='payment_fail'),
    path('my-courses/', views.my_courses, name='my_courses'),
    
    # 노트 관련 URL
    path('lesson/<int:lesson_id>/save-note/', views.save_note, name='save_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
] 