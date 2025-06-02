from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from decimal import Decimal
from django.conf import settings
from datetime import datetime

from .models import Course, Category, Technology, Payment, Purchase, Chapter, Lesson, Note

# requests 라이브러리를 조건부로 임포트
try:
    import requests
except ImportError:
    requests = None


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
    
    # 사용자가 이미 구매했는지 확인
    is_purchased = False
    if request.user.is_authenticated:
        is_purchased = Purchase.objects.filter(user=request.user, course=course).exists()
    
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
        'is_purchased': is_purchased,
        'toss_client_key': getattr(settings, 'TOSS_PAYMENTS_CLIENT_KEY', ''),
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def initiate_payment(request, course_id):
    """결제 시작"""
    if request.method != 'POST':
        return redirect('courses:course_detail', course_id=course_id)
    
    course = get_object_or_404(Course, id=course_id)
    
    # 이미 구매한 강의인지 확인
    if Purchase.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, '이미 구매한 강의입니다.')
        return redirect('courses:course_detail', course_id=course_id)
    
    # 무료 강의 처리
    if course.price_type == 'free':
        # 무료 강의는 바로 구매 완료 처리
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            payment_key=f'free_{uuid.uuid4().hex[:20]}',
            order_id=f'order_{uuid.uuid4().hex[:10]}',
            amount=Decimal('0'),
            status='success',
            payment_method='free'
        )
        
        Purchase.objects.create(
            user=request.user,
            course=course,
            payment=payment
        )
        
        messages.success(request, f'무료 강의 "{course.title}"를 수강할 수 있습니다!')
        return redirect('courses:my_courses')
    
    # 유료 강의 결제 준비
    order_id = f'order_{uuid.uuid4().hex[:10]}'
    amount = int(course.final_price)
    
    # 결제 정보 임시 저장
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        payment_key='',  # Toss에서 받아올 예정
        order_id=order_id,
        amount=course.final_price,
        status='pending'
    )
    
    context = {
        'course': course,
        'payment': payment,
        'amount': amount,
        'order_id': order_id,
        'toss_client_key': getattr(settings, 'TOSS_PAYMENTS_CLIENT_KEY', ''),
        'success_url': getattr(settings, 'PAYMENT_SUCCESS_URL', ''),
        'fail_url': getattr(settings, 'PAYMENT_FAIL_URL', ''),
    }
    
    return render(request, 'courses/payment.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def payment_success(request):
    """결제 성공 처리"""
    try:
        data = json.loads(request.body)
        payment_key = data.get('paymentKey')
        order_id = data.get('orderId')
        amount = data.get('amount')
        
        # 결제 정보 조회
        payment = get_object_or_404(Payment, order_id=order_id)
        
        # requests가 없으면 간단하게 성공 처리
        if not requests:
            payment.payment_key = payment_key
            payment.status = 'success'
            payment.payment_method = 'card'
            payment.approved_at = datetime.now()
            payment.save()
            
            # 구매 완료 처리
            Purchase.objects.create(
                user=payment.user,
                course=payment.course,
                payment=payment
            )
            
            return JsonResponse({
                'success': True,
                'message': '결제가 완료되었습니다.',
                'redirect_url': '/courses/my-courses/'
            })
        
        # Toss Payments API 결제 승인
        url = f"{getattr(settings, 'TOSS_PAYMENTS_API_URL', '')}confirm"
        headers = {
            'Authorization': f'Basic {getattr(settings, "TOSS_PAYMENTS_SECRET_KEY", "")}',
            'Content-Type': 'application/json'
        }
        confirm_data = {
            'paymentKey': payment_key,
            'orderId': order_id,
            'amount': amount
        }
        
        response = requests.post(url, json=confirm_data, headers=headers)
        
        if response.status_code == 200:
            # 결제 성공
            confirm_result = response.json()
            
            payment.payment_key = payment_key
            payment.status = 'success'
            payment.payment_method = confirm_result.get('method', '')
            payment.approved_at = datetime.now()
            payment.save()
            
            # 구매 완료 처리
            Purchase.objects.create(
                user=payment.user,
                course=payment.course,
                payment=payment
            )
            
            return JsonResponse({
                'success': True,
                'message': '결제가 완료되었습니다.',
                'redirect_url': '/courses/my-courses/'
            })
        else:
            # 결제 실패
            error_data = response.json()
            payment.status = 'failed'
            payment.failed_reason = error_data.get('message', '결제 승인 실패')
            payment.save()
            
            return JsonResponse({
                'success': False,
                'message': '결제 승인에 실패했습니다.',
                'error': error_data.get('message', '')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '결제 처리 중 오류가 발생했습니다.',
            'error': str(e)
        })


def payment_fail(request):
    """결제 실패 처리"""
    code = request.GET.get('code', '')
    message = request.GET.get('message', '결제에 실패했습니다.')
    order_id = request.GET.get('orderId', '')
    
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'failed'
            payment.failed_reason = f"[{code}] {message}"
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    context = {
        'error_code': code,
        'error_message': message,
        'order_id': order_id,
    }
    
    return render(request, 'courses/payment_fail.html', context)


@login_required
def my_courses(request):
    """내 강의 목록"""
    purchases = Purchase.objects.filter(user=request.user).select_related('course', 'payment')
    
    # 각 강의의 챕터와 레슨 정보 추가
    courses_data = []
    for purchase in purchases:
        course = purchase.course
        chapters = course.chapters.all().prefetch_related('lessons')
        total_lessons = sum(chapter.lessons.count() for chapter in chapters)
        
        courses_data.append({
            'purchase': purchase,
            'course': course,
            'chapters': chapters,
            'total_lessons': total_lessons,
        })
    
    context = {
        'courses_data': courses_data,
    }
    
    return render(request, 'courses/my_courses.html', context)


@login_required
def edit_course(request, course_id):
    """강의 편집 페이지"""
    course = get_object_or_404(Course, id=course_id)
    
    # 강사 또는 관리자만 편집 가능
    if request.user != course.instructor and not request.user.is_staff:
        messages.error(request, '강의를 편집할 권한이 없습니다.')
        return redirect('courses:course_detail', course_id=course_id)
    
    if request.method == 'POST':
        # 기본 정보 업데이트
        course.title = request.POST.get('title', course.title)
        course.description = request.POST.get('description', course.description)
        course.duration = request.POST.get('duration', course.duration)
        
        # 유튜브 URL 업데이트
        youtube_url = request.POST.get('youtube_url', '').strip()
        if youtube_url != course.youtube_url:
            course.youtube_url = youtube_url
            course.youtube_video_id = course.extract_youtube_id(youtube_url) if youtube_url else ''
        
        course.save()
        messages.success(request, '강의가 성공적으로 업데이트되었습니다.')
        return redirect('courses:edit_course', course_id=course_id)
    
    context = {
        'course': course,
    }
    return render(request, 'courses/edit_course.html', context)


@login_required
def youtube_embed_manager(request):
    """유튜브 임베드 관리 페이지"""
    if not request.user.is_staff:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('courses:course_list')
    
    courses = Course.objects.all().select_related('instructor', 'category')
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        youtube_url = request.POST.get('youtube_url', '').strip()
        duration = request.POST.get('duration', '').strip()
        
        try:
            course = Course.objects.get(id=course_id)
            course.youtube_url = youtube_url
            course.duration = duration
            if youtube_url:
                course.youtube_video_id = course.extract_youtube_id(youtube_url)
            else:
                course.youtube_video_id = ''
            course.save()
            
            messages.success(request, f'"{course.title}" 강의의 유튜브 정보가 업데이트되었습니다.')
        except Course.DoesNotExist:
            messages.error(request, '강의를 찾을 수 없습니다.')
    
    context = {
        'courses': courses,
    }
    return render(request, 'courses/youtube_embed_manager.html', context)


@csrf_exempt
def youtube_preview(request):
    """유튜브 미리보기 AJAX 엔드포인트"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            youtube_url = data.get('youtube_url', '')
            
            if youtube_url:
                # 임시 Course 객체 생성하여 ID 추출
                temp_course = Course()
                video_id = temp_course.extract_youtube_id(youtube_url)
                
                if video_id:
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                    return JsonResponse({
                        'success': True,
                        'video_id': video_id,
                        'embed_url': embed_url,
                        'youtube_url': youtube_url
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '유효하지 않은 유튜브 URL입니다.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'URL이 입력되지 않았습니다.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 허용됩니다.'})


@login_required
def lesson_detail(request, lesson_id):
    """레슨 상세 페이지"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.chapter.course
    
    # 강의를 구매했는지 또는 미리보기 가능한지 확인
    has_access = False
    if request.user.is_staff or request.user == course.instructor:
        has_access = True
    elif Purchase.objects.filter(user=request.user, course=course).exists():
        has_access = True
    elif lesson.is_preview:
        has_access = True
    
    # 사용자의 노트들 가져오기 (접근 권한이 있을 때만)
    notes = []
    if has_access:
        notes = Note.objects.filter(user=request.user, lesson=lesson).order_by('timestamp', '-created_at')
    
    context = {
        'lesson': lesson,
        'course': course,
        'chapter': lesson.chapter,
        'has_access': has_access,
        'notes': notes,
    }
    
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def edit_lesson(request, lesson_id):
    """레슨 편집 페이지"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.chapter.course
    
    # 강사 또는 관리자만 편집 가능
    if request.user != course.instructor and not request.user.is_staff:
        messages.error(request, '레슨을 편집할 권한이 없습니다.')
        return redirect('courses:lesson_detail', lesson_id=lesson_id)
    
    if request.method == 'POST':
        # 기본 정보 업데이트
        lesson.title = request.POST.get('title', lesson.title)
        lesson.description = request.POST.get('description', lesson.description)
        lesson.video_description = request.POST.get('video_description', lesson.video_description)
        lesson.duration = request.POST.get('duration', lesson.duration)
        lesson.is_preview = bool(request.POST.get('is_preview'))
        
        # 유튜브 URL 업데이트
        youtube_url = request.POST.get('youtube_url', '').strip()
        if youtube_url != lesson.youtube_url:
            lesson.youtube_url = youtube_url
            lesson.youtube_video_id = lesson.extract_youtube_id(youtube_url) if youtube_url else ''
        
        lesson.save()
        messages.success(request, '레슨이 성공적으로 업데이트되었습니다.')
        return redirect('courses:edit_lesson', lesson_id=lesson_id)
    
    context = {
        'lesson': lesson,
        'course': course,
        'chapter': lesson.chapter,
    }
    return render(request, 'courses/edit_lesson.html', context)


@login_required
def lesson_manager(request, course_id):
    """강의의 모든 레슨 관리 페이지"""
    course = get_object_or_404(Course, id=course_id)
    
    # 강사 또는 관리자만 접근 가능
    if request.user != course.instructor and not request.user.is_staff:
        messages.error(request, '레슨을 관리할 권한이 없습니다.')
        return redirect('courses:course_detail', course_id=course_id)
    
    chapters = course.chapters.all().prefetch_related('lessons')
    
    context = {
        'course': course,
        'chapters': chapters,
    }
    return render(request, 'courses/lesson_manager.html', context)


@login_required
@csrf_exempt
def save_note(request, lesson_id):
    """노트 저장 (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.chapter.course
    
    # 접근 권한 확인
    has_access = False
    if request.user.is_staff or request.user == course.instructor:
        has_access = True
    elif Purchase.objects.filter(user=request.user, course=course).exists():
        has_access = True
    elif lesson.is_preview:
        has_access = True
    
    if not has_access:
        return JsonResponse({'success': False, 'error': '접근 권한이 없습니다.'})
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        timestamp = data.get('timestamp', '').strip()
        note_id = data.get('note_id')
        
        if not content:
            return JsonResponse({'success': False, 'error': '노트 내용을 입력해주세요.'})
        
        if note_id:
            # 기존 노트 수정
            note = get_object_or_404(Note, id=note_id, user=request.user, lesson=lesson)
            note.content = content
            note.timestamp = timestamp
            note.save()
            action = '수정'
        else:
            # 새 노트 생성
            note = Note.objects.create(
                user=request.user,
                lesson=lesson,
                content=content,
                timestamp=timestamp
            )
            action = '저장'
        
        return JsonResponse({
            'success': True,
            'message': f'노트가 {action}되었습니다.',
            'note_id': note.id,
            'timestamp': note.timestamp,
            'content': note.content,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def delete_note(request, note_id):
    """노트 삭제 (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})
    
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    
    return JsonResponse({
        'success': True,
        'message': '노트가 삭제되었습니다.'
    }) 