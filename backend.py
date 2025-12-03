# Backend logic for 알바·단기계약 리스크 하이라이터

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage
from PIL import Image
import pypdf
import io
import base64

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


def chat_with_contract(user_question, contract_context):
    """
    사용자의 질문을 받아서 계약서 내용과 법률 지식을 바탕으로 답변하는 채팅 함수

    Args:
        user_question (str): 사용자의 질문
        contract_context (str): 분석한 계약서 원문 텍스트

    Returns:
        str: Gemini가 생성한 답변
    """
    print(f"\n채팅 질문: {user_question}")

    # 1. search_db를 호출해서 관련 법률 지식 가져오기
    print("관련 법률 지식 검색 중...")
    legal_knowledge = search_db(user_question)

    # 2. ChatGoogleGenerativeAI 초기화
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=google_api_key,
        temperature=0.7
    )

    # 3. 프롬프트 템플릿 작성 (계약서 내용 + 법률 지식)
    prompt = f"""당신은 사회초년생을 위한 친절한 법률 멘토 '하이라이터'입니다.
사용자가 자신의 계약서에 대해 추가 질문을 했습니다.
아래의 [계약서 내용]과 [법률 지식]을 바탕으로 사용자의 질문에 명쾌하게 답해주세요.

[답변 가이드라인]
1. 계약서 내용을 구체적으로 인용하며 설명해주세요
2. 관련 법률 근거를 함께 제시해주세요
3. 실용적이고 실행 가능한 조언을 해주세요
4. 친근하고 이해하기 쉬운 말투로 작성해주세요

[계약서 내용]
{contract_context[:3000]}

[법률 지식]
{legal_knowledge}

[사용자 질문]
{user_question}
"""

    # 4. Gemini로 답변 생성
    print("Gemini가 답변을 생성 중...")
    response = llm.invoke(prompt)

    return response.content


def generate_suggested_questions(contract_text):
    """
    계약서 텍스트를 분석하여 사용자가 물어볼 만한 질문 3개를 생성하는 함수

    Args:
        contract_text (str): 계약서 원문 텍스트

    Returns:
        list: 추천 질문 3개의 리스트
    """
    print("\n추천 질문 생성 중...")

    # Google API Key 확인
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    # ChatGoogleGenerativeAI 초기화
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=google_api_key,
        temperature=0.7
    )

    # 추천 질문 생성 프롬프트
    prompt = f"""당신은 사회초년생을 위한 법률 멘토입니다.
아래 계약서를 보고, 사용자가 추가로 물어볼 만한 구체적인 질문 3개를 생성해주세요.

[계약서 내용]
{contract_text[:2000]}

[요구사항]
- 계약서 내용을 기반으로 구체적이고 실용적인 질문을 만들어주세요
- 최저임금, 근로시간, 수당, 계약 조건 등 실제로 중요한 사항에 대한 질문이어야 합니다
- 질문은 자연스러운 구어체로 작성해주세요
- 반드시 정확히 3개의 질문만 생성해주세요
- 각 질문은 한 줄로 작성해주세요

출력 형식 (반드시 이 형식을 지켜주세요):
1. 첫 번째 질문
2. 두 번째 질문
3. 세 번째 질문"""

    # LLM 호출
    response = llm.invoke(prompt)
    generated_text = response.content

    # 생성된 텍스트에서 질문 추출
    questions = []
    for line in generated_text.split('\n'):
        line = line.strip()
        # "1.", "2.", "3." 형식의 줄 찾기
        if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
            # 번호 제거하고 질문만 추출
            question = line[2:].strip()
            if question:
                questions.append(question)

    # 정확히 3개가 아니면 기본 질문 사용
    if len(questions) != 3:
        print(f"Warning: LLM이 {len(questions)}개의 질문을 생성했습니다. 기본 질문을 사용합니다.")
        questions = [
            "최저임금 계산이 맞나요?",
            "주휴수당은 어떻게 되나요?",
            "수습기간 조항이 적법한가요?"
        ]

    print(f"생성된 추천 질문: {questions}")
    return questions


def analyze_contract(file_obj):
    """
    계약서 파일(이미지 또는 PDF)을 분석하는 함수

    Args:
        file_obj: Streamlit의 st.file_uploader가 반환하는 파일 객체

    Returns:
        dict: 다음 키를 포함하는 딕셔너리
            - "analysis": 계약서 분석 결과 (워닝사인+스크립트+법적근거)
            - "contract_text": 추출된 계약서 원문 텍스트
            - "suggested_questions": LLM이 생성한 추천 질문 리스트 (3개)
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

        # PIL로 이미지 로드
        image = Image.open(file_obj)

        # 이미지를 바이트로 변환
        buffered = io.BytesIO()
        image.save(buffered, format=image.format or "PNG")
        image_bytes = buffered.getvalue()

        # Base64로 인코딩
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # ChatGoogleGenerativeAI로 Vision 모델 초기화
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=google_api_key,
            temperature=0.2
        )

        # 이미지에서 텍스트 추출 프롬프트
        text_prompt = """이 이미지는 계약서입니다.
이미지에 있는 모든 텍스트를 정확하게 추출해주세요.
계약 내용, 조항, 날짜, 서명란 등 모든 텍스트를 빠짐없이 추출해주세요."""

        # HumanMessage로 이미지와 텍스트 함께 전달
        message = HumanMessage(
            content=[
                {"type": "text", "text": text_prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:image/{image.format or 'png'};base64,{image_base64}"
                }
            ]
        )

        # LLM 호출
        response = llm.invoke([message])
        extracted_text = response.content
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
        return {
            "analysis": f"지원하지 않는 파일 형식입니다: {file_type}\n지원 형식: 이미지(JPG, PNG), PDF",
            "contract_text": "",
            "suggested_questions": []
        }

    # 4. 추출된 텍스트가 없으면 오류 반환
    if not extracted_text.strip():
        return {
            "analysis": "텍스트를 추출할 수 없습니다. 파일이 비어있거나 읽을 수 없습니다.",
            "contract_text": "",
            "suggested_questions": []
        }

    # 5. get_answer() 함수로 계약서 분석
    print("\n계약서 내용을 분석 중...")
    analysis_query = f"""다음은 계약서의 내용입니다. 이 계약서를 분석해서 사회초년생이 주의해야 할 위험 요소를 찾아주세요.

[계약서 내용]
{extracted_text}

위 계약서에서 문제가 될 수 있는 부분을 찾아서 분석해주세요."""

    analysis_result = get_answer(analysis_query)

    # 6. 추천 질문 생성
    suggested_questions = generate_suggested_questions(extracted_text)

    # 7. Dictionary 형태로 결과 반환
    return {
        "analysis": analysis_result,
        "contract_text": extracted_text,
        "suggested_questions": suggested_questions
    }
