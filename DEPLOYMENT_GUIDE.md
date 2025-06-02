# 🚀 Django + Nginx 배포 가이드

## 📋 개요
이 가이드는 Django 프로젝트를 EC2에서 Nginx를 통해 외부 접속 가능하도록 배포하는 방법을 설명합니다.

## 🔧 개선된 기능

### 1. 향상된 관리자 생성 스크립트 (`create_admin.py`)
- 🎯 **대화형 인터페이스**: 단계별 가이드로 쉬운 관리자 생성
- 🔐 **보안 강화**: 비밀번호 검증 및 확인 절차
- 📋 **사용자 관리**: 기존 사용자 목록 확인 기능
- 🚀 **빠른 설정**: 기본 관리자 계정 자동 생성

### 2. Nginx 외부 접속 설정
- 🌍 **외부 접속**: 모든 IP에서 접근 가능
- ⚡ **성능 최적화**: 정적 파일 캐싱 및 압축
- 🔒 **보안 헤더**: XSS, CSRF 등 보안 설정
- 📊 **로깅**: 접근 및 에러 로그 관리

## 🚀 자동 배포 (권장)

### EC2에서 한 번에 설정하기
```bash
# 프로젝트 디렉토리에서 실행
chmod +x deploy_setup.sh
./deploy_setup.sh
```

## 📝 수동 배포 (단계별)

### 1. EC2 인스턴스 준비
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필요한 패키지 설치
sudo apt install -y python3-pip python3-venv nginx git
```

### 2. 프로젝트 설정
```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /var/www/shopping
sudo chown $USER:$USER /var/www/shopping

# 프로젝트 파일 복사
cp -r . /var/www/shopping/
cd /var/www/shopping

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. Django 설정
```bash
# 정적 파일 수집
python manage.py collectstatic --noinput

# 데이터베이스 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 관리자 계정 생성
python create_admin.py
```

### 4. Gunicorn 설정
```bash
# Gunicorn 소켓 파일 생성
sudo cp nginx_config.conf /etc/nginx/sites-available/shopping
sudo ln -s /etc/nginx/sites-available/shopping /etc/nginx/sites-enabled/

# 기본 사이트 비활성화
sudo rm /etc/nginx/sites-enabled/default

# Nginx 재시작
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 방화벽 설정
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable
```

## 🔧 관리자 생성 도구 사용법

### 대화형 생성
```bash
python create_admin.py
# 메뉴에서 "1. 대화형 슈퍼유저 생성" 선택
```

### 빠른 생성 (기본 계정)
```bash
python create_admin.py
# 메뉴에서 "2. 기본 관리자 계정 생성" 선택
# 사용자명: admin, 비밀번호: admin123!
```

### 사용자 목록 확인
```bash
python create_admin.py
# 메뉴에서 "3. 기존 사용자 목록 보기" 선택
```

## 🌐 접속 정보

### 웹사이트 접속
- **메인 페이지**: `http://your-ec2-ip/`
- **관리자 페이지**: `http://your-ec2-ip/admin/`

### EC2 퍼블릭 IP 확인
```bash
curl ifconfig.me
```

## 🔒 보안 설정 (운영 환경)

### 1. Django 설정 수정 (`config/settings.py`)
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-ec2-ip']
SECRET_KEY = 'your-new-secret-key'
```

### 2. SSL 인증서 설정 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🛠️ 유용한 명령어

### 서비스 관리
```bash
# Gunicorn 재시작
sudo systemctl restart gunicorn

# Nginx 재시작
sudo systemctl restart nginx

# 서비스 상태 확인
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### 로그 확인
```bash
# Nginx 접근 로그
sudo tail -f /var/log/nginx/access.log

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# Django 로그 (개발 서버)
python manage.py runserver
```

### 정적 파일 업데이트
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

## 🐛 문제 해결

### 502 Bad Gateway 오류
```bash
# Gunicorn 서비스 확인
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

# 소켓 파일 권한 확인
ls -la /run/gunicorn.sock
```

### 정적 파일이 로드되지 않음
```bash
# 정적 파일 경로 확인
ls -la /var/www/shopping/staticfiles/

# 권한 설정
sudo chown -R www-data:www-data /var/www/shopping/staticfiles/
sudo chmod -R 755 /var/www/shopping/staticfiles/
```

### 외부에서 접속이 안됨
```bash
# 방화벽 상태 확인
sudo ufw status

# EC2 보안 그룹에서 HTTP(80) 포트 열기
# AWS 콘솔에서 보안 그룹 설정 확인
```

## 📊 성능 최적화

### 1. Nginx 설정 최적화
- 정적 파일 캐싱 활성화
- Gzip 압축 사용
- 업로드 파일 크기 제한

### 2. Django 설정 최적화
- 데이터베이스 연결 풀링
- 캐시 시스템 도입 (Redis)
- 정적 파일 CDN 사용

## 🔄 업데이트 배포

### 새 버전 배포
```bash
cd /var/www/shopping
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
sudo systemctl restart gunicorn
```

---

📞 **도움이 필요하신가요?**
- 이슈가 발생하면 로그를 확인하세요
- 보안 그룹 설정을 확인하세요
- 방화벽 설정을 확인하세요 