#!/bin/bash

# 노마드 코더스 클론 앱 실행 스크립트
# macOS/Linux용 Django 개발 서버 실행 스크립트

echo "🚀 노마드 코더스 클론 앱을 시작합니다..."
echo "=================================="

# 현재 디렉토리 확인
if [ ! -f "manage.py" ]; then
    echo "❌ 오류: manage.py 파일을 찾을 수 없습니다."
    echo "   프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# 가상환경 디렉토리 확인
if [ ! -d "venv" ]; then
    echo "❌ 오류: 가상환경(venv)을 찾을 수 없습니다."
    echo "   다음 명령어로 가상환경을 생성해주세요:"
    echo "   python3 -m venv venv"
    exit 1
fi

# 가상환경 활성화
echo "📦 가상환경을 활성화합니다..."
source venv/bin/activate

# 패키지 설치 확인
if [ ! -f "venv/lib/python*/site-packages/django" ]; then
    echo "📥 필요한 패키지를 설치합니다..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 패키지 설치에 실패했습니다."
        exit 1
    fi
fi

# 데이터베이스 마이그레이션 확인
if [ ! -f "db.sqlite3" ]; then
    echo "🗄️  데이터베이스를 설정합니다..."
    python manage.py makemigrations
    python manage.py migrate
    
    echo "👤 관리자 계정을 생성합니다..."
    python create_admin.py
    
    echo "📚 샘플 데이터를 생성합니다..."
    python create_sample_data.py
fi

# 서버 포트 확인 (기본값: 8000)
PORT=${1:-8000}

# Django 개발 서버 실행
echo "🌟 Django 개발 서버를 시작합니다..."
echo "   URL: http://127.0.0.1:$PORT"
echo "   관리자 페이지: http://127.0.0.1:$PORT/admin"
echo "   사용자명: admin"
echo "   비밀번호: admin123!"
echo ""
echo "💡 서버를 종료하려면 Ctrl+C를 누르세요."
echo "=================================="

python manage.py runserver 0.0.0.0:$PORT 