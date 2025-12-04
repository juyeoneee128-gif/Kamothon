# 🤖 계약서 위험 탐지기 (Contract Risk Highlighter)

아르바이트생, 프리랜서 등 사회초년생이 근로 계약 시 겪는 정보 비대칭 문제를 해결하기 위한 AI 기반 계약서 검토 서비스이다. 사용자가 업로드한 계약서 이미지 또는 PDF를 분석하여 핵심 위험 조항 위반 여부를 정밀 탐지하고, 비전문가도 이해하기 쉬운 언어로 법률 정보와 협상 가이드를 제공한다.

---

## ✨ 핵심 기능

### 📊 주요 강행규정 정밀 진단
근로기준법, 저작권법, 최저임금법, 하도급거래 공정화에 관한 법률, 약관의 규제에 관한 법률 등 5대 주요 법령을 기준으로 사전 구축된 15가지 핵심 위험 데이터셋(위약금 예정, 포괄임금제 악용, 저작권 일방 양도 등)과 계약서를 대조한다. 문구의 미묘한 차이로 인해 AI가 놓칠 수 있는 위법 조항을 방지하기 위해, 법적으로 무효인 위반 사항을 별도 데이터셋과 교차 검증하여 '위험(Risk)' 등급을 산출한다.

### 📝 맞춤형 법률 가이드 및 대응 스크립트
난해한 법률 용어를 사회초년생이 이해하기 쉬운 구어체('해요체')로 변환하여 출력한다. 위험 조항이 탐지될 경우, 사용자가 고용주에게 직접 수정 요청을 할 수 있도록 법적 근거가 포함된 협상용 커뮤니케이션 스크립트를 생성한다.

### 🛡️ PII 자동 마스킹 및 텍스트 정제
OCR 과정에서 발생하는 줄바꿈 깨짐 현상을 교정하여 문맥을 복원하는 전처리 파이프라인을 내장했다. 또한, 계약서 내의 성명, 주민등록번호, 주소 등 개인식별정보(PII)를 시스템 프롬프트 단계에서 식별하여 `[이름]`, `[전화번호]`와 같은 플레이스홀더로 치환함으로써 데이터 보안을 유지한다.


---

## 🤖 AI 기술 활용

### Dual Track Hybrid Architecture (하이브리드 분석 엔진)
단일 LLM의 환각(Hallucination) 현상을 방지하고 분석의 정확도를 높이기 위해 두 가지 분석 트랙을 결합한 아키텍처를 구축했다.
- **Track 1 (Rule-based Filtering):** 코드 내에 하드코딩된 `MANDATORY_RISK_CLAUSES` 데이터셋(15개 항목)을 기준으로 강행규정 위반 여부를 1차 필터링한다.
- **Track 2 (RAG Retrieval):** `ChromaDB`에 벡터화되어 저장된 법령(근로기준법, 저작권법 등) 및 표준근로계약서 PDF 청크를 검색하여, 탐지된 위험 조항에 대한 구체적인 법적 근거(조항 원문)를 매핑한다.

### Text Cleaning Pipeline (줄바꿈 보정)
PDF 문서 파싱 시 발생하는 불규칙한 줄바꿈(`\n`) 문제를 해결하기 위해 LLM 기반의 정제 로직을 적용했다.
- `CLEANING_RULES` 상수를 정의하여 "문장이 문법적으로 끝나지 않은 경우 공백으로 연결"하고, "조항 번호나 표 구조는 유지"하도록 처리했다.
- 이를 통해 원문 복원율을 높여 분석 모델이 문맥을 정확하게 파악하도록 구현했다.

### CoT (Chain of Thought) Prompt Engineering
AI가 직관적으로 결론을 내리는 것을 방지하기 위해 4단계 사고 과정을 시스템 프롬프트에 강제했다.
1. **Fact Checking:** 계약서 내 조항의 존재 여부 및 수치(임금, 시간) 확인
2. **Law Matching:** 15대 주요 강행규정 및 RAG 검색 결과와 대조
3. **Judgment:** 위법 여부 판정 (Warning/Critical 구분)
4. **Generation:** 사용자 친화적 설명 및 대응 스크립트 작성
이 과정을 통해 논리적 정합성이 확보된 결과만을 JSON 포맷으로 출력한다.

### Deterministic Output Optimization (일관성 보정)
동일한 계약서에 대해 분석할 때마다 결과가 달라지는 문제를 해결하기 위해 모델 파라미터를 최적화했다.
- **Temperature:** `0.0`으로 설정하여 창의성을 제한하고 결정론적(Deterministic) 답변을 유도했다.
- **Structured Output:** Pydantic 파서와 엄격한 JSON 스키마를 적용하여, 프론트엔드에서 예외 처리 없이 렌더링 가능한 규격화된 데이터를 반환한다.

---

## 🏗️ 아키텍처

```text
[User Upload (IMG/PDF)]
       │
       ▼
[Streamlit Frontend] ──(Replit)──┐
       │                         │
       ▼                         │
[Backend Server] (Python) <──────┘
       │
       ├──▶ [Preprocessing] 
       │    └─ Text Cleaning (Line Break Fix)
       │    └─ PII Masking
       │
       ├──▶ [Hybrid Analysis Engine]
       │    │
       │    ├── [Track 1: Rules] (15 Mandatory Clauses Dataset)
       │    │
       │    └── [Track 2: RAG] (ChromaDB Vector Store)
       │          └─ Source: Labor Law, Copyright Act PDF
       │
       ▼
[Gemini 2.5 Pro] (Vision & Reasoning)
       │
       ▼
[Structured Result (JSON)]

기술 스택
Frontend: Streamlit 1.51.0

Backend: Python 3.11, LangChain 0.3.0

Database: ChromaDB 0.5.5 (Local Vector Store)

AI Models: Google Gemini 2.5 Pro (Vision/Analysis)

Deploy: Replit (Combined Environment)

📂 프로젝트 구조
.
├── app.py                  # 메인 애플리케이션 및 UI 렌더링
├── backend.py              # 분석 로직 오케스트레이션
├── gemini_analyzer.py      # 프롬프트 관리 및 LLM 호출 엔진
├── build_db.py             # 법령 데이터 벡터화 스크립트
├── requirements.txt        # 라이브러리 의존성 명세
├── packages.txt            # Replit 시스템 패키지 설정
├── chroma_db/              # (자동 생성) 법령 데이터 벡터 저장소
├── .env                    # (로컬용) API Key 환경 변수
└── data/                   # RAG용 법률 데이터셋 (PDF)
    ├── labor_law.pdf       # 근로기준법
    ├── copyright_act.pdf   # 저작권법
    └── ... (총 15개 파일)
```

## 🚀 빠른 시작

### 1. 사전 준비
- Google Gemini API Key 발급
- Python 3.10 이상 설치


### 2. 설정 단계
```bash
# 저장소 클론
git clone [Repository URL]

# 필수 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
echo "GOOGLE_API_KEY=your_api_key" > .env

# 법률 데이터베이스 구축 (최초 1회)
python build_db.py


### 3. [배포 단계]
```bash
# 애플리케이션 실행
streamlit run app.py


🔐 보안
API Key 관리: .env 파일을 통해 관리하며 .gitignore를 통해 버전 관리 시스템에서 배제했다.

데이터 휘발성: 분석을 위해 업로드된 파일은 메모리 상에서 처리 후 즉시 삭제되며, 서버나 DB에 원본이 저장되지 않는다.

PII 비식별화: 출력되는 분석 결과 내의 모든 개인정보는 마스킹([이름], [서명] 등) 처리되어 클라이언트에 전달된다.

📝 기타 중요 정보
본 서비스는 법률 정보를 제공하는 AI 시스템으로, 변호사의 법률적 자문을 대체하지 않는다.

분석 결과는 업로드된 문서의 해상도 및 텍스트 인식률(OCR)에 따라 달라질 수 있다.

🤝 기여
현재 해커톤 프로젝트 진행 중으로 외부 기여를 받지 않는다.

📄 라이선스
MIT License

📞 지원
GitHub Issue를 통해 버그 리포트가 가능하다.

Made with ❤️ by Team 파피플
