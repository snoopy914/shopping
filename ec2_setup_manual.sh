#!/bin/bash

# 🚀 EC2 Instance Connect용 수동 배포 스크립트
# AWS 웹 콘솔에서 이 스크립트를 복사해서 사용하세요

echo "🚀 EC2 Instance Connect용 Django 배포 스크립트"
echo "=============================================="

# 1. 시스템 업데이트
echo "1. 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 2. 필요한 패키지 설치
echo "2. 필요한 패키지 설치 중..."
sudo apt install -y python3-pip python3-venv nginx git curl

# 3. 프로젝트 디렉토리 생성
echo "3. 프로젝트 디렉토리 생성 중..."
mkdir -p ~/shopping
cd ~/shopping

# 4. 가상환경 생성
echo "4. Python 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

# 5. Django 및 필수 패키지 설치
echo "5. Django 패키지 설치 중..."
pip install --upgrade pip
pip install Django==4.2.7
pip install Pillow==10.4.0
pip install python-decouple==3.8
pip install gunicorn==21.2.0

# 6. Django 프로젝트 생성
echo "6. Django 프로젝트 구조 생성 중..."
django-admin startproject config .
python manage.py startapp courses

# 7. 기본 설정 파일 생성
echo "7. 기본 설정 파일들 생성 중..."

# settings.py 수정
cat > config/settings.py << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'courses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF

# 8. 기본 뷰 생성
mkdir -p templates
cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Django Shopping Mall</title>
    <style>
        body { font-family: Arial; margin: 50px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="success">🎉 Django + Nginx 배포 성공!</h1>
        <p>쇼핑몰 프로젝트가 성공적으로 배포되었습니다.</p>
        <a href="/admin/">관리자 페이지 →</a>
    </div>
</body>
</html>
EOF

# 9. URL 설정
cat > config/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
]
EOF

# 10. Django 설정 완료
echo "10. Django 초기 설정 완료 중..."
mkdir -p static media
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# 11. 슈퍼유저 생성 스크립트
cat > create_admin.py << 'EOF'
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123!')
    print("✅ 관리자 계정이 생성되었습니다!")
    print("   사용자명: admin")
    print("   비밀번호: admin123!")
else:
    print("❌ 관리자 계정이 이미 존재합니다.")
EOF

# 12. Gunicorn 설정
echo "12. Gunicorn 서비스 설정 중..."
sudo tee /etc/systemd/system/gunicorn.socket > /dev/null << 'EOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/shopping
ExecStart=/home/ubuntu/shopping/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# 13. Nginx 설정
echo "13. Nginx 설정 중..."
sudo tee /etc/nginx/sites-available/shopping > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 75M;

    location /static/ {
        alias /home/ubuntu/shopping/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /home/ubuntu/shopping/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location = /favicon.ico {
        access_log off;
        log_not_found off;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

sudo ln -sf /etc/nginx/sites-available/shopping /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 권한 설정
sudo chown -R www-data:www-data /home/ubuntu/shopping/staticfiles/
sudo chown -R www-data:www-data /home/ubuntu/shopping/media/
sudo chmod -R 755 /home/ubuntu/shopping/staticfiles/
sudo chmod -R 755 /home/ubuntu/shopping/media/

# Nginx 재시작
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# 방화벽 설정
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

echo ""
echo "🎉 배포 완료!"
echo "=============================================="
echo "웹사이트: http://3.90.0.216/"
echo "관리자: http://3.90.0.216/admin/"
echo ""
echo "관리자 계정 생성: python create_admin.py"
echo "==============================================" 