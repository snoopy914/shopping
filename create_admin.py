#!/usr/bin/env python
import os
import sys
import django
import getpass
from django.core.exceptions import ValidationError

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

def create_superuser_interactive():
    """대화형 슈퍼유저 생성"""
    print("=" * 50)
    print("🔧 Django 슈퍼유저 생성 도구")
    print("=" * 50)
    
    while True:
        username = input("사용자명을 입력하세요 (기본값: admin): ").strip()
        if not username:
            username = 'admin'
        
        # 사용자명 중복 체크
        if User.objects.filter(username=username).exists():
            print(f"❌ '{username}' 사용자명이 이미 존재합니다.")
            choice = input("다른 사용자명을 사용하시겠습니까? (y/n): ").lower()
            if choice == 'y':
                continue
            else:
                print("기존 사용자 정보:")
                user = User.objects.get(username=username)
                print(f"   - 사용자명: {user.username}")
                print(f"   - 이메일: {user.email}")
                print(f"   - 가입일: {user.date_joined}")
                return
        break
    
    # 이메일 입력
    email = input("이메일을 입력하세요 (기본값: admin@example.com): ").strip()
    if not email:
        email = 'admin@example.com'
    
    # 비밀번호 입력
    while True:
        print("\n비밀번호를 입력하세요:")
        password = getpass.getpass("비밀번호: ")
        password_confirm = getpass.getpass("비밀번호 확인: ")
        
        if password != password_confirm:
            print("❌ 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
            continue
        
        try:
            validate_password(password)
            break
        except ValidationError as e:
            print("❌ 비밀번호가 너무 간단합니다:")
            for error in e.messages:
                print(f"   - {error}")
            print()
    
    # 추가 정보 입력
    first_name = input("이름 (선택사항): ").strip()
    last_name = input("성 (선택사항): ").strip()
    
    # 확인
    print("\n" + "=" * 50)
    print("입력된 정보:")
    print(f"   사용자명: {username}")
    print(f"   이메일: {email}")
    print(f"   이름: {first_name or '(없음)'}")
    print(f"   성: {last_name or '(없음)'}")
    print("=" * 50)
    
    confirm = input("이 정보로 슈퍼유저를 생성하시겠습니까? (y/n): ").lower()
    if confirm != 'y':
        print("❌ 취소되었습니다.")
        return
    
    try:
        # 슈퍼유저 생성
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        print("\n✅ 슈퍼유저가 성공적으로 생성되었습니다!")
        print(f"   사용자명: {username}")
        print(f"   이메일: {email}")
        print("\n🌐 관리자 페이지 접속:")
        print("   http://localhost:8000/admin")
        print("   또는")
        print("   http://your-server-ip/admin")
        
    except Exception as e:
        print(f"❌ 슈퍼유저 생성 중 오류가 발생했습니다: {e}")

def create_default_admin():
    """기본 관리자 계정 생성 (빠른 설정용)"""
    username = 'admin'
    email = 'admin@nomadcoders.co'
    password = 'admin123!'
    
    if User.objects.filter(username=username).exists():
        print(f"❌ '{username}' 계정이 이미 존재합니다.")
        return
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print("✅ 기본 관리자 계정이 생성되었습니다!")
    print(f"   사용자명: {username}")
    print(f"   비밀번호: {password}")
    print("   ⚠️  보안을 위해 비밀번호를 변경해주세요!")

def list_users():
    """기존 사용자 목록 표시"""
    users = User.objects.all()
    if not users.exists():
        print("❌ 등록된 사용자가 없습니다.")
        return
    
    print("👥 등록된 사용자 목록:")
    for user in users:
        status = "슈퍼유저" if user.is_superuser else "일반사용자"
        print(f"   - {user.username} ({user.email}) - {status}")

def main():
    """메인 메뉴"""
    while True:
        print("\n" + "=" * 50)
        print("🔧 Django 사용자 관리 도구")
        print("=" * 50)
        print("1. 대화형 슈퍼유저 생성")
        print("2. 기본 관리자 계정 생성 (빠른 설정)")
        print("3. 기존 사용자 목록 보기")
        print("4. 종료")
        print("=" * 50)
        
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == '1':
            create_superuser_interactive()
        elif choice == '2':
            create_default_admin()
        elif choice == '3':
            list_users()
        elif choice == '4':
            print("👋 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        sys.exit(1) 