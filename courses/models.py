from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """강의 카테고리"""
    name = models.CharField(max_length=100, verbose_name="카테고리명")
    slug = models.SlugField(unique=True, verbose_name="슬러그")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"
        
    def __str__(self):
        return self.name


class Technology(models.Model):
    """기술 스택"""
    name = models.CharField(max_length=50, verbose_name="기술명")
    color = models.CharField(max_length=7, default="#000000", verbose_name="색상")
    
    class Meta:
        verbose_name = "기술"
        verbose_name_plural = "기술"
        
    def __str__(self):
        return self.name


class Course(models.Model):
    """강의"""
    LEVEL_CHOICES = [
        ('beginner', '초급'),
        ('intermediate', '중급'),
        ('advanced', '고급'),
    ]
    
    PRICE_CHOICES = [
        ('free', '무료'),
        ('paid', '유료'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="강의명")
    description = models.TextField(verbose_name="강의 설명")
    thumbnail = models.ImageField(upload_to='course_thumbnails/', verbose_name="썸네일", blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="난이도")
    price_type = models.CharField(max_length=10, choices=PRICE_CHOICES, verbose_name="가격 유형")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="가격")
    
    # 태그들
    is_bestseller = models.BooleanField(default=False, verbose_name="베스트셀러")
    is_updated = models.BooleanField(default=False, verbose_name="최신 업데이트")
    is_discount = models.BooleanField(default=False, verbose_name="할인")
    
    # 관계
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="카테고리")
    technologies = models.ManyToManyField(Technology, verbose_name="기술 스택")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="강사")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "강의"
        verbose_name_plural = "강의"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    @property
    def get_level_display_korean(self):
        level_dict = dict(self.LEVEL_CHOICES)
        return level_dict.get(self.level, self.level)
    
    @property
    def get_price_display_korean(self):
        price_dict = dict(self.PRICE_CHOICES)
        return price_dict.get(self.price_type, self.price_type)


class Chapter(models.Model):
    """강의 챕터"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name="강의")
    title = models.CharField(max_length=200, verbose_name="챕터명")
    description = models.TextField(blank=True, verbose_name="챕터 설명")
    order = models.PositiveIntegerField(verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "챕터"
        verbose_name_plural = "챕터"
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        
    def __str__(self):
        return f"#{self.order} {self.title}"


class Lesson(models.Model):
    """강의 레슨"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', verbose_name="챕터")
    title = models.CharField(max_length=200, verbose_name="레슨명")
    description = models.TextField(blank=True, verbose_name="레슨 설명")
    duration = models.CharField(max_length=20, blank=True, verbose_name="재생시간")  # "05:37" 형태
    order = models.PositiveIntegerField(verbose_name="순서")
    is_preview = models.BooleanField(default=False, verbose_name="미리보기 가능")
    video_url = models.URLField(blank=True, verbose_name="비디오 URL")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "레슨"
        verbose_name_plural = "레슨"
        ordering = ['chapter', 'order']
        unique_together = ['chapter', 'order']
        
    def __str__(self):
        return f"#{self.chapter.order}.{self.order} {self.title}"


class Review(models.Model):
    """강의 리뷰"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name="강의")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="평점")
    comment = models.TextField(verbose_name="리뷰 내용")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰"
        unique_together = ['course', 'user']
        
    def __str__(self):
        return f"{self.course.title} - {self.user.username} ({self.rating}점)" 