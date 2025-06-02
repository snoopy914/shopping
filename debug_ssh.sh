#!/bin/bash

# 🔧 SSH 연결 디버깅 스크립트
echo "🔧 SSH 연결 문제를 진단합니다..."

# 설정값
PEM_KEY="/Volumes/T7/060_tool/550_shopping/my-key.pem"
EC2_IP="3.90.0.216"

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

echo "================================================="
echo "🔍 SSH 연결 진단 도구"
echo "================================================="
echo "EC2 IP: $EC2_IP"
echo "키페어: $PEM_KEY"
echo "================================================="

# 1. 키페어 파일 확인
print_status "1. 키페어 파일을 확인합니다..."
if [ -f "$PEM_KEY" ]; then
    print_success "키페어 파일 존재함"
    ls -la "$PEM_KEY"
    
    # 권한 확인
    perms=$(ls -la "$PEM_KEY" | cut -d' ' -f1)
    if [[ "$perms" == *"400"* ]] || [[ "$perms" == "-r--------"* ]]; then
        print_success "키페어 권한 올바름 ($perms)"
    else
        print_warning "키페어 권한 수정 중..."
        chmod 400 "$PEM_KEY"
    fi
else
    print_error "키페어 파일을 찾을 수 없습니다!"
    exit 1
fi

# 2. 네트워크 연결 테스트
print_status "2. 네트워크 연결을 테스트합니다..."
if ping -c 1 "$EC2_IP" > /dev/null 2>&1; then
    print_success "PING 성공 - 네트워크 연결 정상"
else
    print_warning "PING 실패 - 네트워크 또는 보안 그룹 문제일 수 있음"
fi

# 3. SSH 포트 테스트
print_status "3. SSH 포트(22)를 테스트합니다..."
if nc -z -w5 "$EC2_IP" 22 2>/dev/null; then
    print_success "포트 22 열려있음"
else
    print_error "포트 22 닫혀있음 - 보안 그룹 확인 필요!"
    echo ""
    print_warning "AWS 콘솔에서 보안 그룹을 확인하세요:"
    echo "   1. EC2 → 보안 그룹"
    echo "   2. SSH (포트 22) 규칙 확인"
    echo "   3. 소스: 0.0.0.0/0 또는 내 IP"
fi

# 4. 상세 SSH 연결 테스트
print_status "4. 상세 SSH 연결을 테스트합니다..."
echo ""
print_warning "다음 명령어를 수동으로 실행해보세요:"
echo ""
echo "ssh -v -i \"$PEM_KEY\" ec2-user@$EC2_IP"
echo ""
print_warning "또는 호스트 키 검증 없이:"
echo ""
echo "ssh -o StrictHostKeyChecking=no -i \"$PEM_KEY\" ec2-user@$EC2_IP"
echo ""

# 5. 대안 연결 방법
print_status "5. 대안 연결 방법들..."
echo ""
echo "💡 EC2 Connect 사용:"
echo "   AWS 콘솔 → EC2 → 인스턴스 선택 → 연결 → EC2 Instance Connect"
echo ""
echo "💡 Session Manager 사용:"
echo "   AWS 콘솔 → EC2 → 인스턴스 선택 → 연결 → Session Manager"
echo ""

# 6. 문제 해결 체크리스트
echo "================================================="
echo "📋 문제 해결 체크리스트"
echo "================================================="
echo "✅ EC2 인스턴스 상태: running"
echo "✅ 보안 그룹 SSH 포트 22 열림"
echo "✅ 보안 그룹 HTTP 포트 80 열림"
echo "✅ 키페어 이름이 인스턴스와 일치"
echo "✅ 키페어 파일 권한 400"
echo "✅ 네트워크 연결 가능"
echo "================================================="

# 자동 재시도 옵션
echo ""
read -p "SSH 연결을 다시 시도하시겠습니까? (y/n): " retry

if [[ "$retry" == "y" || "$retry" == "Y" ]]; then
    print_status "SSH 연결을 재시도합니다..."
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i "$PEM_KEY" ec2-user@$EC2_IP
fi 