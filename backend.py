# Backend logic for 알바·단기계약 리스크 하이라이터

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()


def build_vector_db():
    """
    PDF 파일들을 로드하고 벡터 DB(ChromaDB)를 구축하는 함수
    """
    print("벡터 DB 구축을 시작합니다...")

    # 1. DirectoryLoader로 data/ 폴더의 모든 .pdf 파일을 로드
    print("1. PDF 파일 로딩 중...")
    loader = DirectoryLoader(
        path="./data",
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    print(f"   - 총 {len(documents)}개의 페이지를 로드했습니다.")

    # 2. RecursiveCharacterTextSplitter 사용
    print("2. 문서를 청크로 분할 중...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   - 총 {len(chunks)}개의 청크로 분할했습니다.")

    # 3. GoogleGenerativeAIEmbeddings 사용
    print("3. 임베딩 모델 초기화 중...")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=google_api_key
    )

    # 4. Chroma를 사용하여 로컬 경로('./chroma_db')에 저장
    print("4. ChromaDB에 저장 중...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    # 5. 완료 메시지 출력
    print(f"\n총 {len(chunks)}개의 문서 조각(Chunks)이 DB에 저장되었습니다!")

    return vectorstore
