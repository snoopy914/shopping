#!/usr/bin/env python
"""
실제 노마드 코더스 JavaScript 강의 구조를 참조하여 
상세한 챕터와 레슨 데이터를 생성하는 스크립트

참고: https://nomadcoders.co/javascript-for-beginners/lobby
"""

import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, Chapter, Lesson, Category, Technology


def create_javascript_course_content():
    """JavaScript 강의의 상세 내용을 생성합니다."""
    
    print("🔍 JavaScript 강의를 찾고 있습니다...")
    
    # JavaScript 강의 찾기
    try:
        js_course = Course.objects.get(title__icontains="바닐라 JS")
        print(f"✅ 강의를 찾았습니다: {js_course.title}")
    except Course.DoesNotExist:
        print("❌ JavaScript 강의를 찾을 수 없습니다. 먼저 샘플 데이터를 생성해주세요.")
        return
    
    # 기존 챕터 삭제 (재생성)
    js_course.chapters.all().delete()
    print("🗑️  기존 챕터 데이터를 삭제했습니다.")
    
    # 실제 노마드 코더스 JavaScript 강의 구조
    chapters_data = [
        {
            'title': 'Introduction',
            'description': '강의 소개, 요구사항, JavaScript를 배우는 이유',
            'lessons': [
                {'title': '❤️ 무료 강의 ❤️', 'duration': '', 'is_preview': True},
                {'title': 'Welcome', 'duration': '01:54', 'is_preview': True},
                {'title': 'What Are We Building', 'duration': '02:13', 'is_preview': True},
                {'title': 'Requirements', 'duration': '02:00', 'is_preview': True},
                {'title': 'Software Requirements', 'duration': '02:42', 'is_preview': True},
                {'title': 'Why JS', 'duration': '07:39', 'is_preview': True},
                {'title': 'Why JS II', 'duration': '06:30', 'is_preview': True},
                {'title': 'Online IDE', 'duration': '03:30', 'is_preview': True},
            ]
        },
        {
            'title': 'Welcome to Javascript',
            'description': 'JavaScript 기초 문법과 개념들',
            'lessons': [
                {'title': 'Your First JS Project', 'duration': '11:11', 'is_preview': True},
                {'title': 'Basic Data Types', 'duration': '04:32', 'is_preview': False},
                {'title': 'Variables', 'duration': '10:39', 'is_preview': False},
                {'title': 'const and let', 'duration': '09:45', 'is_preview': False},
                {'title': 'Booleans', 'duration': '07:22', 'is_preview': False},
                {'title': 'Arrays', 'duration': '13:53', 'is_preview': False},
                {'title': 'Objects', 'duration': '13:05', 'is_preview': False},
                {'title': 'Functions part One', 'duration': '08:44', 'is_preview': False},
                {'title': 'Functions part Two', 'duration': '12:45', 'is_preview': False},
                {'title': 'Recap', 'duration': '10:04', 'is_preview': False},
                {'title': 'Recap II', 'duration': '12:52', 'is_preview': False},
                {'title': 'Returns', 'duration': '15:43', 'is_preview': False},
                {'title': 'Recap', 'duration': '06:37', 'is_preview': False},
                {'title': 'Conditionals', 'duration': '11:35', 'is_preview': False},
                {'title': 'Conditionals part Two', 'duration': '09:02', 'is_preview': False},
                {'title': 'Conditionals part Three', 'duration': '13:49', 'is_preview': False},
                {'title': 'Recap', 'duration': '07:34', 'is_preview': False},
            ]
        },
        {
            'title': 'Javascript on the Browser',
            'description': 'DOM 조작과 이벤트 처리',
            'lessons': [
                {'title': 'The Document Object', 'duration': '08:14', 'is_preview': False},
                {'title': 'HTML in Javascript', 'duration': '10:31', 'is_preview': False},
                {'title': 'Searching For Elements', 'duration': '12:23', 'is_preview': False},
                {'title': 'Events', 'duration': '12:38', 'is_preview': False},
                {'title': 'Events part Two', 'duration': '08:31', 'is_preview': False},
                {'title': 'More Events', 'duration': '09:48', 'is_preview': False},
                {'title': 'CSS in Javascript', 'duration': '06:51', 'is_preview': False},
                {'title': 'CSS in Javascript part Two', 'duration': '09:34', 'is_preview': False},
                {'title': 'CSS in Javascript part Three', 'duration': '07:57', 'is_preview': False},
            ]
        },
        {
            'title': 'Login',
            'description': '사용자 입력 처리와 로컬 스토리지 활용',
            'lessons': [
                {'title': 'Input Values', 'duration': '09:48', 'is_preview': False},
                {'title': 'Form Submission', 'duration': '08:38', 'is_preview': False},
                {'title': 'Events', 'duration': '10:56', 'is_preview': False},
                {'title': 'Events part Two', 'duration': '08:08', 'is_preview': True},
                {'title': 'Getting Username', 'duration': '11:12', 'is_preview': False},
                {'title': 'Saving Username', 'duration': '07:35', 'is_preview': False},
                {'title': 'Loading Username', 'duration': '10:07', 'is_preview': False},
                {'title': 'Super Recap', 'duration': '13:58', 'is_preview': False},
            ]
        },
        {
            'title': 'Clock',
            'description': '실시간 시계 구현하기',
            'lessons': [
                {'title': 'Intervals', 'duration': '05:37', 'is_preview': False},
                {'title': 'Timeouts and Dates', 'duration': '08:46', 'is_preview': False},
                {'title': 'PadStart', 'duration': '07:42', 'is_preview': False},
                {'title': 'Recap', 'duration': '04:44', 'is_preview': False},
            ]
        },
        {
            'title': 'Quotes and Background',
            'description': '랜덤 명언과 배경 이미지 기능',
            'lessons': [
                {'title': 'Quotes', 'duration': '10:14', 'is_preview': False},
                {'title': 'Background', 'duration': '08:45', 'is_preview': False},
                {'title': 'Recap', 'duration': '05:15', 'is_preview': False},
            ]
        },
        {
            'title': 'To Do List',
            'description': '할 일 목록 기능 구현',
            'lessons': [
                {'title': 'Setup', 'duration': '07:55', 'is_preview': False},
                {'title': 'Adding ToDos', 'duration': '07:00', 'is_preview': False},
                {'title': 'Deleting To Dos', 'duration': '09:54', 'is_preview': False},
                {'title': 'Saving To Dos', 'duration': '07:26', 'is_preview': False},
                {'title': 'Loading To Dos part One', 'duration': '11:19', 'is_preview': False},
                {'title': 'Loading To Dos part Two', 'duration': '08:28', 'is_preview': False},
                {'title': 'Deleting To Dos part One', 'duration': '10:23', 'is_preview': False},
                {'title': 'Deleting To Dos part Two', 'duration': '13:04', 'is_preview': False},
                {'title': 'Deleting To Dos part Three', 'duration': '05:32', 'is_preview': False},
            ]
        },
        {
            'title': 'Weather',
            'description': '날씨 API 연동하기',
            'lessons': [
                {'title': 'Geolocation', 'duration': '07:27', 'is_preview': False},
                {'title': 'Weather API', 'duration': '14:13', 'is_preview': False},
                {'title': 'Conclusions', 'duration': '02:52', 'is_preview': False},
            ]
        },
    ]
    
    print("📚 챕터와 레슨을 생성하고 있습니다...")
    
    # 챕터와 레슨 생성
    for chapter_order, chapter_data in enumerate(chapters_data, 1):
        chapter = Chapter.objects.create(
            course=js_course,
            title=chapter_data['title'],
            description=chapter_data['description'],
            order=chapter_order
        )
        
        print(f"   └─ #{chapter_order} {chapter.title} 생성")
        
        # 레슨 생성
        for lesson_order, lesson_data in enumerate(chapter_data['lessons'], 1):
            Lesson.objects.create(
                chapter=chapter,
                title=lesson_data['title'],
                duration=lesson_data['duration'],
                order=lesson_order,
                is_preview=lesson_data['is_preview']
            )
        
        print(f"      └─ {len(chapter_data['lessons'])}개 레슨 생성")
    
    print("\n✅ JavaScript 강의 구조가 성공적으로 생성되었습니다!")
    print(f"🎯 총 {len(chapters_data)}개 챕터, {sum(len(ch['lessons']) for ch in chapters_data)}개 레슨")
    print("\n📖 다음으로 확인해보세요:")
    print("   🌐 강의 상세 페이지: http://127.0.0.1:8000/course/1/")
    print("   🔧 관리자 페이지: http://127.0.0.1:8000/admin/courses/course/")


if __name__ == '__main__':
    try:
        create_javascript_course_content()
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc() 