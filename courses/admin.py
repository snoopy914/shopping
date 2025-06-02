from django.contrib import admin
from .models import Category, Technology, Course, Chapter, Lesson, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['order', 'title', 'duration', 'is_preview']


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
    list_display = ['chapter', 'order', 'title', 'duration', 'is_preview', 'created_at']
    list_filter = ['is_preview', 'chapter__course', 'created_at']
    search_fields = ['title', 'chapter__title', 'chapter__course__title']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'price_type', 'price', 'category', 'instructor', 'is_bestseller', 'is_updated', 'created_at']
    list_filter = ['level', 'price_type', 'category', 'is_bestseller', 'is_updated', 'is_discount']
    search_fields = ['title', 'description']
    filter_horizontal = ['technologies']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChapterInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'thumbnail', 'category', 'instructor')
        }),
        ('강의 설정', {
            'fields': ('level', 'price_type', 'price', 'technologies')
        }),
        ('태그', {
            'fields': ('is_bestseller', 'is_updated', 'is_discount')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'user__username', 'comment']
    readonly_fields = ['created_at'] 