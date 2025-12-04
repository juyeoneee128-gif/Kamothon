#!/usr/bin/env python3
"""
.env 파일 설정 스크립트
API 키를 안전하게 입력할 수 있습니다.
"""

import getpass

print("=" * 60)
print("🔐 API 키 설정 스크립트")
print("=" * 60)
print("\n📝 Google AI Studio에서 발급받은 API 키를 입력하세요.")
print("   (입력하는 내용은 화면에 표시되지 않습니다)\n")

# API 키 입력 (화면에 표시 안 됨)
api_key = getpass.getpass("API Key: ").strip()

if len(api_key) < 20:
    print("\n❌ 오류: API 키가 너무 짧습니다. (최소 20자 이상)")
    print("   정상적인 Google API 키는 보통 39자 정도입니다.")
    exit(1)

if api_key == "YOUR_API_KEY_HERE":
    print("\n❌ 오류: 플레이스홀더를 그대로 입력하셨습니다.")
    print("   실제 API 키를 입력해주세요.")
    exit(1)

# .env 파일 생성
with open('.env', 'w') as f:
    f.write(f"GOOGLE_API_KEY={api_key}\n")
    f.write(f"GEMINI_API_KEY={api_key}\n")

print("\n✅ .env 파일이 성공적으로 생성되었습니다!")
print(f"   API 키 길이: {len(api_key)} 문자")
print(f"   시작 문자: {api_key[:7]}...")

# 검증
from dotenv import load_dotenv
import os

load_dotenv('.env')
test_key = os.getenv('GEMINI_API_KEY')

if test_key == api_key:
    print("\n✅ 검증 완료: API 키가 제대로 저장되었습니다!")
else:
    print("\n⚠️ 경고: 저장된 키와 입력한 키가 다릅니다.")

print("\n" + "=" * 60)
print("🎉 설정 완료!")
print("=" * 60)
