from django.contrib import admin
from .models import Category, Technology, Course, Chapter, Lesson, Review, Payment, Purchase, Note
# Payment, Purchase는 일시적으로 제거

# 기존 admin 클래스들만 유지
# PaymentAdmin, PurchaseAdmin은 나중에 추가

from django.utils.html import format_html
from django.db import models


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_course_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_per_page = 20
    
    def get_course_count(self, obj):
        count = obj.course_set.count()
        if count > 0:
            return format_html(
                '<a href="{}?category__id__exact={}">{} 개</a>',
                '/admin/courses/course/',
                obj.id,
                count
            )
        return '0 개'
    get_course_count.short_description = '강의 수'


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'get_course_count', 'color_preview']
    list_display_links = ['name']
    search_fields = ['name']
    list_filter = ['color']
    ordering = ['name']
    
    # 전체 선택 삭제 활성화
    actions = ['delete_selected', 'duplicate_technologies']
    
    # 한 페이지당 항목 수
    list_per_page = 20
    
    # 색상 미리보기 함수
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = '색상 미리보기'
    
    # 해당 기술을 사용하는 강의 수
    def get_course_count(self, obj):
        count = obj.course_set.count()
        if count > 0:
            return format_html(
                '<a href="{}?technologies__id__exact={}">{} 개 강의</a>',
                '/admin/courses/course/',
                obj.id,
                count
            )
        return '0 개 강의'
    get_course_count.short_description = '사용 강의 수'
    get_course_count.admin_order_field = 'course_count'
    
    # 강의 수를 기준으로 정렬 가능하도록 queryset 수정
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            course_count=models.Count('course')
        )
        return queryset
    
    # 일괄 삭제 시 확인 메시지 커스터마이징
    def delete_selected(self, request, queryset):
        # 삭제 전 사용 중인 강의가 있는지 확인
        used_technologies = []
        safe_to_delete = []
        
        for tech in queryset:
            course_count = tech.course_set.count()
            if course_count > 0:
                used_technologies.append(f"{tech.name} ({course_count}개 강의에서 사용 중)")
            else:
                safe_to_delete.append(tech)
        
        if used_technologies:
            self.message_user(
                request,
                f"다음 기술들은 강의에서 사용 중이므로 삭제할 수 없습니다: {', '.join(used_technologies)}",
                level='ERROR'
            )
            # 안전하게 삭제 가능한 기술들만 삭제
            if safe_to_delete:
                count = len(safe_to_delete)
                for tech in safe_to_delete:
                    tech.delete()
                self.message_user(
                    request,
                    f"{count}개의 미사용 기술이 삭제되었습니다.",
                    level='SUCCESS'
                )
            return
        
        # 모든 기술이 안전하게 삭제 가능한 경우
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{count}개의 기술이 삭제되었습니다.",
            level='SUCCESS'
        )
    
    delete_selected.short_description = "선택된 기술들을 삭제"
    
    # 기술 복제 액션 추가
    def duplicate_technologies(self, request, queryset):
        duplicated_count = 0
        for tech in queryset:
            Technology.objects.create(
                name=f"{tech.name} (복사본)",
                color=tech.color
            )
            duplicated_count += 1
        
        self.message_user(
            request,
            f"{duplicated_count}개의 기술이 복제되었습니다.",
            level='SUCCESS'
        )
    
    duplicate_technologies.short_description = "선택된 기술들을 복제"


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['order', 'title', 'youtube_url', 'duration', 'is_preview']
    readonly_fields = ['youtube_video_id']


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ['order', 'title']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['course', 'order', 'title', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'order', 'title', 'duration', 'youtube_video_id', 'is_preview', 'created_at']
    list_filter = ['is_preview', 'chapter__course', 'created_at']
    search_fields = ['title', 'description', 'video_description', 'chapter__title', 'chapter__course__title']
    fields = [
        'chapter', 'order', 'title', 'description', 
        'youtube_url', 'youtube_video_id', 'video_description',
        'duration', 'is_preview', 'video_url'
    ]
    readonly_fields = ['youtube_video_id']
    ordering = ['chapter__course', 'chapter__order', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'price_type', 'get_final_price', 'category', 'instructor', 'get_sales_count', 'is_bestseller', 'created_at']
    list_filter = ['level', 'price_type', 'category', 'is_bestseller', 'is_updated', 'is_discount']
    search_fields = ['title', 'description']
    filter_horizontal = ['technologies']
    readonly_fields = ['created_at', 'updated_at', 'youtube_video_id']
    inlines = [ChapterInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'thumbnail', 'category', 'instructor')
        }),
        ('강의 설정', {
            'fields': ('level', 'price_type', 'price', 'discount_price', 'technologies')
        }),
        ('유튜브 영상', {
            'fields': ('youtube_url', 'youtube_video_id', 'duration'),
            'description': 'youtube_video_id는 URL에서 자동으로 추출됩니다.'
        }),
        ('태그', {
            'fields': ('is_bestseller', 'is_updated', 'is_discount')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_final_price(self, obj):
        price = obj.final_price
        if obj.is_discount and obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #666;">₩{}</span><br>'
                '<span style="color: #d73527; font-weight: bold;">₩{}</span>',
                obj.price,
                price
            )
        return f'₩{price:,.0f}' if price > 0 else '무료'
    get_final_price.short_description = '최종 가격'
    
    def get_sales_count(self, obj):
        count = obj.purchase_set.count()
        if count > 0:
            return format_html(
                '<a href="{}?course__id__exact={}">{} 명</a>',
                '/admin/courses/purchase/',
                obj.id,
                count
            )
        return '0 명'
    get_sales_count.short_description = '구매자 수'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'get_course_title', 'get_user_name', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'payment_key', 'user__username', 'course__title']
    readonly_fields = ['payment_key', 'order_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'course', 'amount', 'status')
        }),
        ('결제 정보', {
            'fields': ('payment_key', 'order_id', 'payment_method', 'approved_at')
        }),
        ('실패 정보', {
            'fields': ('failed_reason',),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_course_title(self, obj):
        return obj.course.title
    get_course_title.short_description = '강의명'
    
    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_description = '사용자'
    
    actions = ['mark_as_success', 'mark_as_failed']
    
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated}개의 결제가 성공으로 변경되었습니다.')
    mark_as_success.short_description = '선택된 결제를 성공으로 변경'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated}개의 결제가 실패로 변경되었습니다.')
    mark_as_failed.short_description = '선택된 결제를 실패로 변경'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'get_course_title', 'get_payment_amount', 'get_payment_method', 'purchased_at']
    list_filter = ['purchased_at', 'payment__payment_method', 'course__category']
    search_fields = ['user__username', 'course__title', 'payment__order_id']
    readonly_fields = ['purchased_at']
    
    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_description = '구매자'
    
    def get_course_title(self, obj):
        return obj.course.title
    get_course_title.short_description = '강의명'
    
    def get_payment_amount(self, obj):
        if obj.payment.amount == 0:
            return '무료'
        return f'₩{obj.payment.amount:,.0f}'
    get_payment_amount.short_description = '결제금액'
    
    def get_payment_method(self, obj):
        if obj.payment.payment_method == 'free':
            return '무료 등록'
        return obj.payment.payment_method or '미확인'
    get_payment_method.short_description = '결제수단'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'user__username', 'comment']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'user', 'timestamp', 'get_content_preview', 'created_at']
    list_filter = ['created_at', 'lesson__chapter__course']
    search_fields = ['content', 'user__username', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = '노트 미리보기' 