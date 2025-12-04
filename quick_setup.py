#!/usr/bin/env python3
"""
빠른 .env 설정
이 파일의 YOUR_API_KEY_HERE를 실제 키로 교체한 후 실행하세요.
"""

# ⬇️ 여기에 발급받은 API 키를 입력하세요
API_KEY = "YOUR_API_KEY_HERE"

# =====================================
# 아래 코드는 수정하지 마세요
# =====================================

if API_KEY == "YOUR_API_KEY_HERE":
    print("❌ 오류: 위의 API_KEY 변수에 실제 API 키를 입력하세요!")
    print("   파일을 열어서 'YOUR_API_KEY_HERE'를 교체한 후 다시 실행하세요.")
    exit(1)

if len(API_KEY) < 20:
    print("❌ 오류: API 키가 너무 짧습니다.")
    exit(1)

# .env 파일 생성
with open('.env', 'w') as f:
    f.write(f"GOOGLE_API_KEY={API_KEY}\n")
    f.write(f"GEMINI_API_KEY={API_KEY}\n")

print("✅ .env 파일이 생성되었습니다!")
print(f"   키 길이: {len(API_KEY)} 문자")
print(f"   시작: {API_KEY[:10]}...")

# 검증
from dotenv import load_dotenv
import os
load_dotenv('.env')
if os.getenv('GEMINI_API_KEY') == API_KEY:
    print("\n✅ 검증 완료! API 키가 정상적으로 설정되었습니다.")
else:
    print("\n⚠️ 검증 실패")
