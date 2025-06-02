from django.db import models
from django.contrib.auth.models import User
import re


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
    """강의 - 단순화된 버전"""
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
    
    # 유튜브 영상 관련 필드 (단순화)
    youtube_url = models.URLField(blank=True, verbose_name="유튜브 URL", help_text="유튜브 영상 URL을 입력하세요")
    youtube_video_id = models.CharField(max_length=20, blank=True, verbose_name="유튜브 비디오 ID")
    duration = models.CharField(max_length=20, blank=True, verbose_name="재생시간")
    
    # 태그들
    is_bestseller = models.BooleanField(default=False, verbose_name="베스트셀러")
    is_updated = models.BooleanField(default=False, verbose_name="최신 업데이트")
    is_discount = models.BooleanField(default=False, verbose_name="할인")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="할인가격")
    
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
    
    @property
    def final_price(self):
        """할인이 적용된 최종 가격"""
        if self.is_discount and self.discount_price:
            return self.discount_price
        return self.price
    
    def save(self, *args, **kwargs):
        # 유튜브 URL에서 비디오 ID 추출
        if self.youtube_url and not self.youtube_video_id:
            self.youtube_video_id = self.extract_youtube_id(self.youtube_url)
        
        super().save(*args, **kwargs)
    
    def extract_youtube_id(self, url):
        """유튜브 URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''
    
    @property
    def youtube_embed_url(self):
        """유튜브 임베드 URL"""
        if self.youtube_video_id:
            return f"https://www.youtube.com/embed/{self.youtube_video_id}"
        return ""


class Payment(models.Model):
    """결제 정보"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', '결제 대기'),
        ('success', '결제 완료'),
        ('failed', '결제 실패'),
        ('cancelled', '결제 취소'),
        ('refunded', '환불 완료'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="강의")
    
    # Toss Payments 관련 필드
    payment_key = models.CharField(max_length=200, unique=True, verbose_name="결제 키")
    order_id = models.CharField(max_length=100, unique=True, verbose_name="주문 ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="결제 금액")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="결제 상태")
    
    # 결제 상세 정보
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="결제 수단")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="승인 시간")
    failed_reason = models.TextField(blank=True, verbose_name="실패 사유")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.course.title} - {self.user.username} ({self.status})"


class Purchase(models.Model):
    """구매 완료된 강의"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="강의")
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, verbose_name="결제 정보")
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="구매일시")
    
    class Meta:
        verbose_name = "구매"
        verbose_name_plural = "구매"
        unique_together = ['user', 'course']
        ordering = ['-purchased_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


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
    
    # 유튜브 영상 관련 필드
    youtube_url = models.URLField(blank=True, verbose_name="유튜브 URL", help_text="유튜브 영상 URL을 입력하세요")
    youtube_video_id = models.CharField(max_length=20, blank=True, verbose_name="유튜브 비디오 ID")
    video_description = models.TextField(blank=True, verbose_name="영상 설명", help_text="이 영상에서 다루는 내용을 자세히 설명해주세요")
    
    duration = models.CharField(max_length=20, blank=True, verbose_name="재생시간")
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
    
    def save(self, *args, **kwargs):
        # 유튜브 URL에서 비디오 ID 추출
        if self.youtube_url and not self.youtube_video_id:
            self.youtube_video_id = self.extract_youtube_id(self.youtube_url)
        
        super().save(*args, **kwargs)
    
    def extract_youtube_id(self, url):
        """유튜브 URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''
    
    @property
    def youtube_embed_url(self):
        """유튜브 임베드 URL"""
        if self.youtube_video_id:
            return f"https://www.youtube.com/embed/{self.youtube_video_id}"
        return ""


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


class Note(models.Model):
    """레슨 노트"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="레슨")
    content = models.TextField(verbose_name="노트 내용")
    timestamp = models.CharField(max_length=20, blank=True, verbose_name="영상 시간", help_text="예: 05:30")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "노트"
        verbose_name_plural = "노트"
        ordering = ['-updated_at']
        
    def __str__(self):
        timestamp_text = f" ({self.timestamp})" if self.timestamp else ""
        return f"{self.lesson.title} - {self.user.username}{timestamp_text}" 