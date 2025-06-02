#!/bin/bash

# 🚀 Git 기반 EC2 자동 배포 스크립트
echo "🚀 Git을 통한 EC2 배포를 시작합니다..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# EC2 정보 입력받기
read -p "EC2 퍼블릭 IP를 입력하세요: " EC2_IP
read -p "PEM 키 파일 경로를 입력하세요 (예: ~/my-key.pem): " PEM_KEY
read -p "Git 저장소 URL을 입력하세요: " GIT_REPO

print_status "EC2 IP: $EC2_IP"
print_status "PEM 키: $PEM_KEY"
print_status "Git 저장소: $GIT_REPO"

# 1. 로컬 코드를 Git에 푸시
print_status "로컬 변경사항을 Git에 푸시합니다..."
git add .
git commit -m "배포 준비: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 2. EC2에 SSH로 연결하여 배포 실행
print_status "EC2에 연결하여 배포를 진행합니다..."

ssh -i "$PEM_KEY" ec2-user@$EC2_IP << EOF
    # 색상 정의
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    
    echo -e "\${BLUE}[EC2]${NC} 배포 프로세스를 시작합니다..."
    
    # 프로젝트 디렉토리로 이동 또는 클론
    if [ -d "shopping" ]; then
        echo -e "\${BLUE}[EC2]${NC} 기존 프로젝트를 업데이트합니다..."
        cd shopping
        git pull origin main
    else
        echo -e "\${BLUE}[EC2]${NC} 프로젝트를 새로 클론합니다..."
        git clone $GIT_REPO shopping
        cd shopping
    fi
    
    # 가상환경 활성화 (있다면)
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 의존성 설치
    if [ -f "requirements.txt" ]; then
        echo -e "\${BLUE}[EC2]${NC} Python 패키지를 설치합니다..."
        pip install -r requirements.txt
    fi
    
    # Django 설정
    if [ -f "manage.py" ]; then
        echo -e "\${BLUE}[EC2]${NC} Django 설정을 진행합니다..."
        python manage.py collectstatic --noinput
        python manage.py migrate
    fi
    
    # 서비스 재시작 (Gunicorn이 설치되어 있다면)
    if systemctl is-active --quiet gunicorn; then
        echo -e "\${BLUE}[EC2]${NC} Gunicorn을 재시작합니다..."
        sudo systemctl restart gunicorn
    fi
    
    # Nginx 재시작 (설치되어 있다면)
    if systemctl is-active --quiet nginx; then
        echo -e "\${BLUE}[EC2]${NC} Nginx를 재시작합니다..."
        sudo systemctl restart nginx
    fi
    
    echo -e "\${GREEN}[EC2]${NC} 배포가 완료되었습니다! 🎉"
EOF

print_success "배포가 완료되었습니다!"
print_success "웹사이트 확인: http://$EC2_IP"
print_warning "최초 배포라면 deploy_setup.sh를 먼저 실행하세요!" 