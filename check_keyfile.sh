#!/bin/bash

echo "🔑 EC2 키페어 파일 확인 도구"
echo "================================"

# 가능한 키 파일 패턴들
patterns=(
    "2505121144"
    "2505121144.pem"
    "*.pem"
    "*key*"
    "*2505121144*"
)

echo "현재 디렉토리에서 키 파일을 찾고 있습니다..."
echo ""

for pattern in "${patterns[@]}"; do
    files=$(ls $pattern 2>/dev/null)
    if [ ! -z "$files" ]; then
        echo "✅ 발견된 파일: $pattern"
        for file in $files; do
            echo "   📁 파일: $file"
            echo "   📏 크기: $(ls -lh $file | awk '{print $5}')"
            echo "   🔐 권한: $(ls -l $file | awk '{print $1}')"
            
            # PEM 파일인지 확인
            if head -1 "$file" 2>/dev/null | grep -q "BEGIN.*PRIVATE KEY"; then
                echo "   ✅ 유효한 PEM 키 파일입니다!"
            elif file "$file" 2>/dev/null | grep -q "PEM"; then
                echo "   ✅ PEM 형식 파일입니다!"
            else
                echo "   ⚠️  PEM 파일이 아닐 수 있습니다."
            fi
            echo ""
        done
    fi
done

echo "권장 사항:"
echo "1. 키 파일이 발견되면: chmod 400 키파일명"
echo "2. 키 파일이 없다면: AWS 콘솔에서 새로 생성"
echo "3. 테스트: ssh -i 키파일명 ec2-user@EC2-IP" 