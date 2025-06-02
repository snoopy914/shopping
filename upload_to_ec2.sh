#!/bin/bash

# 📁 EC2 파일 업로드 스크립트
echo "📁 EC2로 파일을 업로드합니다..."

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

# 기본값 설정
EC2_USER="ec2-user"

# EC2 정보 입력
read -p "EC2 퍼블릭 IP를 입력하세요: " EC2_IP
read -p "PEM 키 파일 경로를 입력하세요: " PEM_KEY

# PEM 키 파일 권한 설정
chmod 400 "$PEM_KEY"

print_status "EC2 연결 테스트 중..."
if ssh -i "$PEM_KEY" -o ConnectTimeout=10 ec2-user@$EC2_IP "echo 'Connection successful'" 2>/dev/null; then
    print_success "EC2 연결 성공!"
else
    print_error "EC2 연결 실패! IP와 키 파일을 확인하세요."
    exit 1
fi

# 업로드할 파일/폴더 선택
echo ""
echo "업로드 옵션을 선택하세요:"
echo "1. 전체 프로젝트 폴더"
echo "2. 특정 파일들만"
echo "3. 커스텀 선택"
read -p "선택 (1-3): " choice

case $choice in
    1)
        print_status "전체 프로젝트 폴더를 업로드합니다..."
        
        # 제외할 파일들 설정
        excludes=(
            "--exclude=venv/"
            "--exclude=__pycache__/"
            "--exclude=*.pyc"
            "--exclude=.git/"
            "--exclude=.env"
            "--exclude=db.sqlite3"
            "--exclude=.DS_Store"
            "--exclude=node_modules/"
        )
        
        # rsync로 동기화 (더 효율적)
        rsync -avz -e "ssh -i $PEM_KEY" \
            "${excludes[@]}" \
            ./ ec2-user@$EC2_IP:~/shopping/
        
        print_success "프로젝트 폴더 업로드 완료!"
        ;;
        
    2)
        print_status "핵심 파일들만 업로드합니다..."
        
        # 필수 파일들
        files=(
            "manage.py"
            "requirements.txt"
            "deploy_setup.sh"
            "create_admin.py"
            "nginx_config.conf"
        )
        
        # 디렉토리들
        dirs=(
            "config/"
            "courses/"
            "templates/"
            "static/"
        )
        
        # EC2에 디렉토리 생성
        ssh -i "$PEM_KEY" ec2-user@$EC2_IP "mkdir -p ~/shopping"
        
        # 파일 업로드
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                print_status "업로드 중: $file"
                scp -i "$PEM_KEY" "$file" ec2-user@$EC2_IP:~/shopping/
            fi
        done
        
        # 디렉토리 업로드
        for dir in "${dirs[@]}"; do
            if [ -d "$dir" ]; then
                print_status "업로드 중: $dir"
                scp -i "$PEM_KEY" -r "$dir" ec2-user@$EC2_IP:~/shopping/
            fi
        done
        
        print_success "핵심 파일 업로드 완료!"
        ;;
        
    3)
        print_status "업로드할 파일/폴더를 입력하세요 (공백으로 구분):"
        read -p "파일/폴더 목록: " custom_files
        
        ssh -i "$PEM_KEY" ec2-user@$EC2_IP "mkdir -p ~/shopping"
        
        for item in $custom_files; do
            if [ -e "$item" ]; then
                print_status "업로드 중: $item"
                if [ -d "$item" ]; then
                    scp -i "$PEM_KEY" -r "$item" ec2-user@$EC2_IP:~/shopping/
                else
                    scp -i "$PEM_KEY" "$item" ec2-user@$EC2_IP:~/shopping/
                fi
            else
                print_warning "파일/폴더를 찾을 수 없습니다: $item"
            fi
        done
        
        print_success "커스텀 파일 업로드 완료!"
        ;;
        
    *)
        print_error "잘못된 선택입니다."
        exit 1
        ;;
esac

# 업로드된 파일 확인
print_status "업로드된 파일을 확인합니다..."
ssh -i "$PEM_KEY" ec2-user@$EC2_IP "ls -la ~/shopping/"

print_success "모든 파일 업로드가 완료되었습니다! 🎉"
print_warning "이제 EC2에서 deploy_setup.sh를 실행하세요:"
echo "ssh -i \"$PEM_KEY\" ec2-user@$EC2_IP"
echo "cd ~/shopping"
echo "chmod +x deploy_setup.sh"
echo "./deploy_setup.sh" 