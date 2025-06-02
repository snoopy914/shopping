from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from .models import Course, Category, Technology


def course_list(request):
    """강의 목록 페이지"""
    courses = Course.objects.all().select_related('category', 'instructor').prefetch_related('technologies')
    categories = Category.objects.all()
    technologies = Technology.objects.all()
    
    # 필터링
    level_filter = request.GET.get('level')
    price_filter = request.GET.get('price')
    category_filter = request.GET.get('category')
    tech_filter = request.GET.get('tech')
    search_query = request.GET.get('search')
    
    if level_filter:
        courses = courses.filter(level=level_filter)
    
    if price_filter:
        courses = courses.filter(price_type=price_filter)
    
    if category_filter:
        courses = courses.filter(category__slug=category_filter)
    
    if tech_filter:
        courses = courses.filter(technologies__name__icontains=tech_filter)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # 태그별 강의 분류
    bestseller_courses = courses.filter(is_bestseller=True)[:6]
    updated_courses = courses.filter(is_updated=True)[:6]
    free_courses = courses.filter(price_type='free')[:6]
    
    context = {
        'courses': courses,
        'categories': categories,
        'technologies': technologies,
        'bestseller_courses': bestseller_courses,
        'updated_courses': updated_courses,
        'free_courses': free_courses,
        'current_level': level_filter,
        'current_price': price_filter,
        'current_category': category_filter,
        'current_tech': tech_filter,
        'search_query': search_query,
    }
    
    return render(request, 'courses/course_list.html', context)


def course_detail(request, course_id):
    """강의 상세 페이지"""
    course = get_object_or_404(Course, id=course_id)
    reviews = course.reviews.all().select_related('user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # 챕터와 레슨 정보
    chapters = course.chapters.all().prefetch_related('lessons')
    
    # 총 레슨 수와 총 시간 계산
    total_lessons = sum(chapter.lessons.count() for chapter in chapters)
    
    # 미리보기 가능한 레슨들
    preview_lessons = []
    for chapter in chapters:
        preview_lessons.extend(chapter.lessons.filter(is_preview=True))
    
    # 관련 강의 (같은 카테고리)
    related_courses = Course.objects.filter(
        category=course.category
    ).exclude(id=course.id)[:4]
    
    context = {
        'course': course,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'chapters': chapters,
        'total_lessons': total_lessons,
        'preview_lessons': preview_lessons,
        'related_courses': related_courses,
    }
    
    return render(request, 'courses/course_detail.html', context) 