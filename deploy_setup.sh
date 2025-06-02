#!/bin/bash

# 🚀 Django + Nginx 배포 자동화 스크립트
echo "🚀 Django + Nginx 배포 설정을 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 루트 권한 확인
if [[ $EUID -eq 0 ]]; then
   print_error "이 스크립트를 루트 권한으로 실행하지 마세요."
   exit 1
fi

# 프로젝트 경로 설정
PROJECT_NAME="shopping"
PROJECT_PATH="/var/www/$PROJECT_NAME"
CURRENT_DIR=$(pwd)

print_status "프로젝트 경로: $PROJECT_PATH"
print_status "현재 디렉토리: $CURRENT_DIR"

# 1. 시스템 업데이트
print_status "시스템 패키지를 업데이트합니다..."
sudo apt update && sudo apt upgrade -y

# 2. 필요한 패키지 설치
print_status "필요한 패키지를 설치합니다..."
sudo apt install -y python3-pip python3-venv nginx git curl

# 3. 프로젝트 디렉토리 생성 및 권한 설정
print_status "프로젝트 디렉토리를 설정합니다..."
sudo mkdir -p $PROJECT_PATH
sudo chown $USER:$USER $PROJECT_PATH

# 4. 프로젝트 파일 복사
print_status "프로젝트 파일을 복사합니다..."
cp -r $CURRENT_DIR/* $PROJECT_PATH/
cd $PROJECT_PATH

# 5. 가상환경 생성 및 활성화
print_status "Python 가상환경을 생성합니다..."
python3 -m venv venv
source venv/bin/activate

# 6. Python 패키지 설치
print_status "Python 패키지를 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 7. Django 설정
print_status "Django 설정을 진행합니다..."
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# 8. Gunicorn 설정
print_status "Gunicorn 서비스를 설정합니다..."

# Gunicorn socket 파일
sudo tee /etc/systemd/system/gunicorn.socket > /dev/null <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# Gunicorn service 파일
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_PATH
ExecStart=$PROJECT_PATH/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Gunicorn 서비스 시작
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# 9. Nginx 설정
print_status "Nginx를 설정합니다..."

# Nginx 설정 파일 생성
sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 75M;

    location /static/ {
        alias $PROJECT_PATH/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias $PROJECT_PATH/media/;
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

    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

# 사이트 활성화
sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 권한 설정
sudo chown -R www-data:www-data $PROJECT_PATH/staticfiles/
sudo chown -R www-data:www-data $PROJECT_PATH/media/
sudo chmod -R 755 $PROJECT_PATH/staticfiles/
sudo chmod -R 755 $PROJECT_PATH/media/

# Nginx 설정 테스트 및 재시작
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    print_success "Nginx 설정이 완료되었습니다."
else
    print_error "Nginx 설정에 오류가 있습니다."
    exit 1
fi

# 10. 방화벽 설정
print_status "방화벽을 설정합니다..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

# 11. 서비스 상태 확인
print_status "서비스 상태를 확인합니다..."
sudo systemctl status gunicorn.socket --no-pager
sudo systemctl status nginx --no-pager

# 12. 완료 메시지
print_success "배포 설정이 완료되었습니다!"
echo ""
echo "🌐 웹사이트 접속 정보:"
echo "   - HTTP: http://$(curl -s ifconfig.me)"
echo "   - 관리자 페이지: http://$(curl -s ifconfig.me)/admin"
echo ""
echo "📁 프로젝트 경로: $PROJECT_PATH"
echo ""
echo "🔧 유용한 명령어:"
echo "   - Gunicorn 재시작: sudo systemctl restart gunicorn"
echo "   - Nginx 재시작: sudo systemctl restart nginx"
echo "   - 로그 확인: sudo tail -f /var/log/nginx/access.log"
echo "   - 에러 로그: sudo tail -f /var/log/nginx/error.log"
echo ""
print_warning "보안을 위해 Django의 DEBUG를 False로 설정하고 SECRET_KEY를 변경하세요!" 