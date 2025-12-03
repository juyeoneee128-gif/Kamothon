# Backend logic for 알바·단기계약 리스크 하이라이터

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from PIL import Image
import google.generativeai as genai
import pypdf
import io

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


def search_db(query):
    """
    질문을 받아서 벡터 DB에서 유사한 문서를 검색하는 함수

    Args:
        query (str): 검색할 질문

    Returns:
        str: 검색 결과를 정리한 문자열
    """
    print(f"질문: {query}")
    print("벡터 DB 검색 중...")

    # 1. GoogleGenerativeAIEmbeddings 초기화
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=google_api_key
    )

    # 2. Chroma 로드
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    # 3. 유사한 문서 3개 검색
    results = vectorstore.similarity_search(query, k=3)

    # 4. 결과 정리
    if not results:
        return "관련 문서를 찾을 수 없습니다."

    output = []
    for i, doc in enumerate(results, 1):
        output.append(f"\n=== 문서 {i} ===")
        output.append(f"내용: {doc.page_content[:200]}...")  # 처음 200자만 표시
        output.append(f"출처: {doc.metadata}")

    return "\n".join(output)


def get_answer(query):
    """
    사용자의 질문을 받아서 벡터 DB 검색 후 Gemini로 답변을 생성하는 함수

    Args:
        query (str): 사용자의 질문

    Returns:
        str: Gemini가 생성한 답변
    """
    print(f"\n질문: {query}")

    # 1. search_db를 호출해서 관련 문서 가져오기
    print("관련 문서 검색 중...")
    context = search_db(query)

    # 2. ChatGoogleGenerativeAI 초기화
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=google_api_key,
        temperature=0.7
    )

    # 3. 프롬프트 템플릿 작성
    prompt = f"""당신은 사회초년생을 위한 친절한 법률 멘토 '하이라이터'입니다.
아래의 [참고 문서]를 바탕으로 사용자의 질문에 명쾌하게 답해주세요.

[답변 필수 포함 항목]
1. 🚨 워닝 사인 (위법 여부 판단)
2. 💬 대처 스크립트 (사장님께 보낼 카톡 말투로)
3. ⚖️ 법적 근거 (참고 문서의 출처 활용)

[참고 문서]: {context}
[질문]: {query}
"""

    # 4. Gemini로 답변 생성
    print("Gemini가 답변을 생성 중...")
    response = llm.invoke(prompt)

    return response.content


def analyze_contract(file_obj):
    """
    계약서 파일(이미지 또는 PDF)을 분석하는 함수

    Args:
        file_obj: Streamlit의 st.file_uploader가 반환하는 파일 객체

    Returns:
        str: 계약서 분석 결과
    """
    print(f"\n계약서 분석 시작: {file_obj.name}")

    # 1. 파일 타입 확인
    file_type = file_obj.type
    print(f"파일 타입: {file_type}")

    extracted_text = ""

    # 2. 이미지 파일인 경우 (JPEG, PNG 등)
    if file_type.startswith("image/"):
        print("이미지 파일 감지 - Gemini Vision으로 텍스트 추출 중...")

        # Google API Key 확인
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

        # Gemini API 설정
        genai.configure(api_key=google_api_key)

        # PIL로 이미지 로드
        image = Image.open(file_obj)

        # Gemini 2.5 Pro Vision 모델 사용
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # 이미지에서 텍스트 추출 프롬프트
        prompt = """이 이미지는 계약서입니다.
이미지에 있는 모든 텍스트를 정확하게 추출해주세요.
계약 내용, 조항, 날짜, 서명란 등 모든 텍스트를 빠짐없이 추출해주세요."""

        # Gemini Vision API 호출
        response = model.generate_content([prompt, image])
        extracted_text = response.text
        print(f"추출된 텍스트 길이: {len(extracted_text)} 글자")

    # 3. PDF 파일인 경우
    elif file_type == "application/pdf":
        print("PDF 파일 감지 - pypdf로 텍스트 추출 중...")

        # 파일 객체를 바이트로 읽기
        pdf_bytes = file_obj.read()
        pdf_file = io.BytesIO(pdf_bytes)

        # pypdf로 PDF 읽기
        pdf_reader = pypdf.PdfReader(pdf_file)

        # 모든 페이지의 텍스트 추출
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            extracted_text += page_text + "\n"
            print(f"페이지 {page_num} 추출 완료")

        print(f"총 추출된 텍스트 길이: {len(extracted_text)} 글자")

    else:
        return f"지원하지 않는 파일 형식입니다: {file_type}\n지원 형식: 이미지(JPG, PNG), PDF"

    # 4. 추출된 텍스트가 없으면 오류 반환
    if not extracted_text.strip():
        return "텍스트를 추출할 수 없습니다. 파일이 비어있거나 읽을 수 없습니다."

    # 5. get_answer() 함수로 계약서 분석
    print("\n계약서 내용을 분석 중...")
    analysis_query = f"""다음은 계약서의 내용입니다. 이 계약서를 분석해서 사회초년생이 주의해야 할 위험 요소를 찾아주세요.

[계약서 내용]
{extracted_text}

위 계약서에서 문제가 될 수 있는 부분을 찾아서 분석해주세요."""

    analysis_result = get_answer(analysis_query)

    return analysis_result
