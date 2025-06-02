# 노마드 코더스 클론 프로젝트

[nomadcoders.co/courses](https://nomadcoders.co/courses)와 유사한 구조의 온라인 강의 플랫폼입니다.

## 🚀 기능

- **강의 목록**: 다양한 프로그래밍 강의를 카테고리별로 분류
- **필터링**: 난이도, 가격, 기술 스택별 필터링
- **검색**: 강의명과 설명으로 검색 가능
- **강의 상세**: 강의 정보, 리뷰, 관련 강의 표시
- **관리자 패널**: Django Admin을 통한 강의 관리
- **반응형 디자인**: 모바일과 데스크톱 모두 지원

## 🛠 기술 스택

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **Database**: SQLite (개발용)
- **Icons**: Font Awesome 6.0
- **Image Processing**: Pillow

## 🚀 빠른 시작 (권장)

### 자동 실행 스크립트 사용

**macOS/Linux:**
```bash
./run_app.sh
```

**Windows:**
```cmd
run_app.bat
```

**다른 포트로 실행:**
```bash
./run_app.sh 8080    # macOS/Linux
run_app.bat 8080     # Windows
```

실행 스크립트가 자동으로 다음 작업을 수행합니다:
- 가상환경 활성화
- 필요한 패키지 설치 (첫 실행시)
- 데이터베이스 마이그레이션 (첫 실행시)
- 관리자 계정 생성 (첫 실행시)
- 샘플 데이터 생성 (첫 실행시)
- Django 개발 서버 실행

## 📦 수동 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd nomadcoder-clone
```

### 2. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 관리자 계정 생성
```bash
python create_admin.py
```

### 6. 샘플 데이터 생성
```bash
python create_sample_data.py
```

### 7. 개발 서버 실행
```bash
python manage.py runserver
```

웹 브라우저에서 `http://127.0.0.1:8000`으로 접속하세요.

## 👤 관리자 계정

- **사용자명**: admin
- **비밀번호**: admin123!
- **관리자 페널**: `http://127.0.0.1:8000/admin/`

## 📱 주요 페이지

- **홈페이지**: `/` - 모든 강의 목록
- **강의 상세**: `/course/<id>/` - 개별 강의 정보
- **관리자**: `/admin/` - Django 관리자 패널

## 🎨 디자인 특징

- **모던한 UI**: Bootstrap 5와 커스텀 CSS로 구현
- **카드 기반 레이아웃**: 강의를 카드 형태로 표시
- **호버 효과**: 마우스 오버시 카드 애니메이션
- **배지 시스템**: 난이도, 가격, 태그를 배지로 표시
- **그라디언트**: 히어로 섹션과 썸네일에 그라디언트 적용

## 📊 데이터 모델

### Category (카테고리)
- 풀스택, 프론트엔드, 백엔드, 모바일, AI/ML, 데이터

### Technology (기술 스택)
- JavaScript, Python, React, Django, NextJS, Flutter 등

### Course (강의)
- 제목, 설명, 썸네일, 난이도, 가격, 태그
- 카테고리, 기술 스택, 강사와 연결

### Review (리뷰)
- 강의별 사용자 리뷰 및 평점

## 📁 프로젝트 구조

```
nomadcoder-clone/
├── config/                 # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── courses/                # 강의 앱
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── ...
├── templates/              # HTML 템플릿
│   ├── base.html
│   └── courses/
├── static/                 # 정적 파일
├── media/                  # 업로드 파일
├── venv/                   # 가상환경
├── run_app.sh             # macOS/Linux 실행 스크립트
├── run_app.bat            # Windows 실행 스크립트
├── create_admin.py        # 관리자 계정 생성
├── create_sample_data.py  # 샘플 데이터 생성
├── requirements.txt       # 패키지 목록
└── README.md             # 프로젝트 설명
```

## 🔧 개발 환경

- **Python**: 3.8+
- **Django**: 4.2.7
- **macOS**: 완전 지원
- **Windows**: 완전 지원
- **브라우저**: Chrome, Firefox, Safari 지원

## 🐛 문제 해결

### 포트가 이미 사용 중인 경우
```bash
./run_app.sh 8080    # 다른 포트 사용
```

### 패키지 설치 오류
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 데이터베이스 리셋
```bash
rm db.sqlite3
python manage.py migrate
python create_admin.py
python create_sample_data.py
```

## 📝 라이센스

이 프로젝트는 교육 목적으로 만들어졌습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**노마드 코더스**와 유사한 학습 플랫폼을 Django로 구현한 프로젝트입니다. 🚀 