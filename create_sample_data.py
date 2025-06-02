#!/usr/bin/env python
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import Category, Technology, Course, Review

# 강사 계정 생성
instructor, created = User.objects.get_or_create(
    username='nico',
    defaults={
        'first_name': '니꼬',
        'last_name': '쌤',
        'email': 'nico@nomadcoders.co'
    }
)

# 카테고리 생성
categories_data = [
    {'name': '풀스택', 'slug': 'fullstack'},
    {'name': '프론트엔드', 'slug': 'frontend'},
    {'name': '백엔드', 'slug': 'backend'},
    {'name': '모바일', 'slug': 'mobile'},
    {'name': 'AI/ML', 'slug': 'ai-ml'},
    {'name': '데이터', 'slug': 'data'},
]

for cat_data in categories_data:
    Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={'name': cat_data['name']}
    )

# 기술 스택 생성
technologies_data = [
    {'name': 'JavaScript', 'color': '#F7DF1E'},
    {'name': 'Python', 'color': '#3776AB'},
    {'name': 'React', 'color': '#61DAFB'},
    {'name': 'Django', 'color': '#092E20'},
    {'name': 'NextJS', 'color': '#000000'},
    {'name': 'Flutter', 'color': '#02569B'},
    {'name': 'React Native', 'color': '#61DAFB'},
    {'name': 'TypeScript', 'color': '#3178C6'},
    {'name': 'Node.js', 'color': '#339933'},
    {'name': 'HTML5', 'color': '#E34F26'},
    {'name': 'CSS3', 'color': '#1572B6'},
    {'name': 'TailwindCSS', 'color': '#06B6D4'},
    {'name': 'Firebase', 'color': '#FFCA28'},
    {'name': 'GraphQL', 'color': '#E10098'},
    {'name': 'Go', 'color': '#00ADD8'},
    {'name': 'Dart', 'color': '#0175C2'},
    {'name': 'Supabase', 'color': '#3ECF8E'},
    {'name': 'Prisma', 'color': '#2D3748'},
]

for tech_data in technologies_data:
    Technology.objects.get_or_create(
        name=tech_data['name'],
        defaults={'color': tech_data['color']}
    )

# 강의 생성
courses_data = [
    {
        'title': '[풀스택] 유튜브 클론코딩',
        'description': '유튜브 백엔드 + 프런트엔드 + 배포\n\nPug, MongoDB, Express, Node.js를 사용하여 실제 유튜브와 같은 웹사이트를 만들어보세요. 사용자 인증, 비디오 업로드, 댓글 시스템까지 모든 기능을 구현합니다.',
        'level': 'beginner',
        'price_type': 'paid',
        'price': 89000,
        'category': 'fullstack',
        'technologies': ['JavaScript', 'Node.js', 'HTML5', 'CSS3'],
        'is_bestseller': True,
    },
    {
        'title': '코코아톡 클론코딩',
        'description': 'HTML, CSS, Github\n\n카카오톡 모바일 앱의 디자인을 HTML과 CSS만으로 완벽하게 재현해보세요. 반응형 웹 디자인과 CSS 애니메이션을 배울 수 있습니다.',
        'level': 'beginner',
        'price_type': 'paid',
        'price': 59000,
        'category': 'frontend',
        'technologies': ['HTML5', 'CSS3'],
        'is_bestseller': False,
    },
    {
        'title': '틱톡 클론코딩',
        'description': 'Flutter, Firebase, Dart\n\n실제 틱톡과 같은 모바일 앱을 Flutter로 만들어보세요. 비디오 업로드, 좋아요, 댓글, 팔로우 기능까지 모든 것을 구현합니다.',
        'level': 'intermediate',
        'price_type': 'paid',
        'price': 129000,
        'category': 'mobile',
        'technologies': ['Flutter', 'Firebase', 'Dart'],
        'is_updated': True,
    },
    {
        'title': '[풀스택] 캐럿마켓 클론코딩',
        'description': 'NextJS, Tailwind, Prisma, Supabase\n\n당근마켓과 같은 중고거래 플랫폼을 만들어보세요. 최신 기술 스택을 사용하여 현대적인 웹 애플리케이션을 개발합니다.',
        'level': 'intermediate',
        'price_type': 'paid',
        'price': 149000,
        'category': 'fullstack',
        'technologies': ['NextJS', 'TailwindCSS', 'Prisma', 'Supabase'],
        'is_updated': True,
        'is_bestseller': True,
    },
    {
        'title': 'SQL 마스터클래스',
        'description': 'SQLite, MySQL, PostgreSQL, MongoDB, Redis\n\n데이터베이스의 모든 것을 배워보세요. 관계형 데이터베이스부터 NoSQL까지 실무에서 사용하는 모든 데이터베이스를 다룹니다.',
        'level': 'beginner',
        'price_type': 'paid',
        'price': 99000,
        'category': 'data',
        'technologies': ['Python'],
        'is_updated': True,
    },
    {
        'title': '풀스택 GPT',
        'description': '랭체인으로 AI 웹 서비스 만들기\n\nChatGPT API를 활용하여 나만의 AI 웹 서비스를 만들어보세요. 최신 AI 기술을 웹 개발에 접목하는 방법을 배웁니다.',
        'level': 'beginner',
        'price_type': 'paid',
        'price': 119000,
        'category': 'ai-ml',
        'technologies': ['Python'],
        'is_updated': True,
        'is_bestseller': True,
    },
    {
        'title': 'Next.js 시작하기',
        'description': 'NextJS for Beginners\n\nReact의 프레임워크인 Next.js를 처음부터 배워보세요. 서버사이드 렌더링, 정적 사이트 생성 등 Next.js의 핵심 기능을 학습합니다.',
        'level': 'intermediate',
        'price_type': 'free',
        'price': 0,
        'category': 'frontend',
        'technologies': ['NextJS', 'React', 'TypeScript'],
        'is_updated': True,
    },
    {
        'title': '줌 클론코딩',
        'description': 'WebSockets, SocketIO, WebRTC\n\n실시간 화상회의 앱을 만들어보세요. WebRTC를 사용한 P2P 통신과 Socket.IO를 활용한 실시간 채팅을 구현합니다.',
        'level': 'beginner',
        'price_type': 'free',
        'price': 0,
        'category': 'fullstack',
        'technologies': ['JavaScript', 'Node.js'],
    },
    {
        'title': '트위터 클론코딩',
        'description': 'React Firebase for Beginners\n\nReact와 Firebase를 사용하여 트위터와 같은 소셜 미디어 앱을 만들어보세요. 실시간 데이터베이스와 사용자 인증을 배웁니다.',
        'level': 'intermediate',
        'price_type': 'free',
        'price': 0,
        'category': 'frontend',
        'technologies': ['React', 'Firebase'],
        'is_updated': True,
    },
    {
        'title': '바닐라 JS로 크롬 앱 만들기',
        'description': 'Javascript For Beginners\n\n순수 JavaScript만으로 크롬 확장 프로그램을 만들어보세요. JavaScript의 기초부터 실제 앱 개발까지 단계별로 학습합니다.',
        'level': 'beginner',
        'price_type': 'free',
        'price': 0,
        'category': 'frontend',
        'technologies': ['JavaScript', 'HTML5', 'CSS3'],
        'is_updated': True,
    },
]

for course_data in courses_data:
    category = Category.objects.get(slug=course_data['category'])
    
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults={
            'description': course_data['description'],
            'level': course_data['level'],
            'price_type': course_data['price_type'],
            'price': course_data['price'],
            'category': category,
            'instructor': instructor,
            'is_bestseller': course_data.get('is_bestseller', False),
            'is_updated': course_data.get('is_updated', False),
        }
    )
    
    if created:
        # 기술 스택 추가
        for tech_name in course_data['technologies']:
            try:
                tech = Technology.objects.get(name=tech_name)
                course.technologies.add(tech)
            except Technology.DoesNotExist:
                pass

print("샘플 데이터가 생성되었습니다!")
print(f"카테고리: {Category.objects.count()}개")
print(f"기술: {Technology.objects.count()}개")
print(f"강의: {Course.objects.count()}개") 