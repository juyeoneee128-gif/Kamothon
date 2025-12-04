#!/usr/bin/env python3
"""
벡터 DB 리빌딩 스크립트

data/ 폴더의 모든 PDF 파일을 읽어서 ChromaDB 벡터 DB를 새로 구축합니다.
기존 chroma_db 폴더가 있다면 삭제하고 처음부터 다시 만듭니다.
"""

import os
import shutil
from backend import build_vector_db


def main():
    print("=" * 60)
    print("벡터 DB 리빌딩 시작")
    print("=" * 60)

    # 1. 기존 chroma_db 폴더가 있다면 삭제
    chroma_db_path = "./chroma_db"
    if os.path.exists(chroma_db_path):
        print(f"\n⚠️  기존 {chroma_db_path} 폴더를 삭제합니다...")
        shutil.rmtree(chroma_db_path)
        print(f"✅ 기존 DB 삭제 완료")
    else:
        print(f"\n💡 기존 DB가 없습니다. 새로 생성합니다.")

    # 2. data/ 폴더의 PDF 파일 목록 확인
    data_folder = "./data"
    if not os.path.exists(data_folder):
        print(f"❌ 오류: {data_folder} 폴더가 존재하지 않습니다.")
        return

    pdf_files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]
    print(f"\n📂 {data_folder} 폴더에서 {len(pdf_files)}개의 PDF 파일을 발견했습니다:")
    for i, pdf_file in enumerate(sorted(pdf_files), 1):
        file_path = os.path.join(data_folder, pdf_file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB 단위
        print(f"   {i}. {pdf_file} ({file_size:.2f} MB)")

    # 3. 벡터 DB 구축 (backend.py의 build_vector_db 함수 호출)
    print("\n" + "=" * 60)
    try:
        vectorstore = build_vector_db()
        print("=" * 60)
        print("\n🎉 벡터 DB 리빌딩 완료!")
        print(f"✅ 데이터베이스가 {chroma_db_path} 폴더에 저장되었습니다.")

        # 4. DB 상태 확인
        if os.path.exists(chroma_db_path):
            db_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(chroma_db_path)
                for filename in filenames
            ) / (1024 * 1024)  # MB 단위
            print(f"📊 DB 크기: {db_size:.2f} MB")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("DB 구축에 실패했습니다.")
        return

    print("\n" + "=" * 60)
    print("✅ 모든 작업이 완료되었습니다!")
    print("=" * 60)


if __name__ == "__main__":
    main()
