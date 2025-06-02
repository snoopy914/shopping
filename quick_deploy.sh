#!/bin/bash

# 🚀 빠른 EC2 배포 스크립트 (키페어 경로 설정됨)
echo "🚀 빠른 EC2 배포를 시작합니다..."

# 키페어 경로 설정
PEM_KEY="/Volumes/T7/060_tool/550_shopping/my-key.pem"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 키페어 파일 확인
if [ ! -f "$PEM_KEY" ]; then
    print_error "키페어 파일을 찾을 수 없습니다: $PEM_KEY"
    exit 1
fi

print_success "키페어 파일 확인됨: $PEM_KEY"

# 키페어 권한 설정
print_status "키페어 파일 권한을 설정합니다..."
chmod 400 "$PEM_KEY"

# EC2 IP 입력받기
read -p "EC2 퍼블릭 IP를 입력하세요: " EC2_IP

if [ -z "$EC2_IP" ]; then
    print_error "EC2 IP를 입력해주세요."
    exit 1
fi

# EC2 연결 테스트
print_status "EC2 연결을 테스트합니다..."
if ssh -i "$PEM_KEY" -o ConnectTimeout=10 ec2-user@$EC2_IP "echo 'Connection successful'" 2>/dev/null; then
    print_success "EC2 연결 성공!"
else
    print_error "EC2 연결 실패! IP를 확인하세요."
    echo "테스트 명령어: ssh -i \"$PEM_KEY\" ec2-user@$EC2_IP"
    exit 1
fi

# 배포 방법 선택
echo ""
echo "배포 방법을 선택하세요:"
echo "1. Git 기반 배포 (권장)"
echo "2. 직접 파일 업로드"
echo "3. 수동 SCP 업로드"
read -p "선택 (1-3): " deploy_choice

case $deploy_choice in
    1)
        print_status "Git 기반 배포를 실행합니다..."
        read -p "Git 저장소 URL을 입력하세요: " GIT_REPO
        
        if [ -z "$GIT_REPO" ]; then
            print_error "Git 저장소 URL을 입력해주세요."
            exit 1
        fi
        
        # Git 배포 실행
        export EC2_IP PEM_KEY GIT_REPO
        ./deploy_git.sh
        ;;
        
    2)
        print_status "직접 파일 업로드를 실행합니다..."
        export EC2_IP PEM_KEY
        ./upload_to_ec2.sh
        ;;
        
    3)
        print_status "수동 SCP 업로드 명령어를 제공합니다..."
        echo ""
        echo "📁 전체 프로젝트 업로드:"
        echo "scp -i \"$PEM_KEY\" -r ./ ec2-user@$EC2_IP:~/shopping/"
        echo ""
        echo "🔧 개별 파일 업로드:"
        echo "scp -i \"$PEM_KEY\" manage.py requirements.txt deploy_setup.sh ec2-user@$EC2_IP:~/shopping/"
        echo ""
        echo "🖥️  EC2 접속:"
        echo "ssh -i \"$PEM_KEY\" ec2-user@$EC2_IP"
        echo ""
        echo "📋 배포 실행 (EC2에서):"
        echo "cd ~/shopping"
        echo "chmod +x deploy_setup.sh"
        echo "./deploy_setup.sh"
        ;;
        
    *)
        print_error "잘못된 선택입니다."
        exit 1
        ;;
esac

print_success "배포 스크립트 실행 완료!"
print_warning "배포 후 웹사이트 확인: http://$EC2_IP" 