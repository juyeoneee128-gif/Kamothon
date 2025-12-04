from __future__ import annotations

import os
import json
import logging
from typing import Optional, List

from pydantic import BaseModel

# Vector DB imports (for chat_with_contract RAG system)
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_chroma import Chroma
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    VECTOR_DB_AVAILABLE = False
    logging.warning(f"Vector DB dependencies not available: {e}. Chat functionality will be limited.")

DEMO_MODE = False

CLEANING_RULES = """
**[작업 1: 텍스트 추출 및 정제 (Text Cleaning)] - 중요!**
계약서 이미지에서 텍스트를 추출할 때, 다음 '줄바꿈 처리 규칙'을 엄격하게 적용하여 문장을 자연스럽게 만드세요.

1. **문장 연결 (Line Merge):**
   - 문장이 문법적으로 끝나지 않았는데 줄바꿈 문자(\\n)가 있는 경우, 이를 삭제하고 **공백(띄어쓰기)으로 대체**하여 앞뒤 문장을 연결하세요.
   - 예시: "근로자는 갑의 지시에\\n따라야 한다" -> "근로자는 갑의 지시에 따라야 한다"

2. **구조 유지 (Structure Keep):**
   - 문단이 바뀌거나, 조항이 구분되는 경우(예: 제1조, 1., 가. 등)에는 줄바꿈을 유지하세요.
   - 표나 리스트 형태의 데이터는 구조가 깨지지 않도록 줄바꿈을 보존하세요.
"""

# [백엔드 삽입용] 6대 법령 강행규정 위반 탐지 데이터셋
# 이 리스트는 AI가 분석할 때 '정답지'로 참고합니다.
MANDATORY_RISK_CLAUSES = [
    # 1. 근로기준법 제20조 (위약금 예정 금지) - 절대 무효
    {
        "clause_id": "mandatory_labor_01",
        "category": "🚨 근로기준법 위반",
        "risk_pattern": "퇴사 시 위약금, 손해배상액을 미리 금액으로 정해둠",
        "legal_reference": "근로기준법 제20조 (위약 예정 금지)",
        "explanation": "근로자가 갑자기 그만둔다고 해서 미리 정해진 벌금(위약금)을 내게 하는 건 불법입니다. 실제 발생한 손해만 청구할 수 있습니다.",
        "script": "근로기준법 제20조에 의거, 근로계약 불이행에 대한 위약금 예정 약정은 무효입니다. 해당 조항 삭제를 요청합니다."
    },

    # 2. 근로기준법 제56조 (연장/야간/휴일근로 가산수당) - 50% 가산 필수
    {
        "clause_id": "mandatory_labor_02",
        "category": "🚨 근로기준법 위반",
        "risk_pattern": "연장근로, 야간근로, 휴일근로에 대한 가산수당(50%)이 없거나 통상임금만 지급",
        "legal_reference": "근로기준법 제56조 (연장·야간 및 휴일 근로)",
        "explanation": "야근, 밤 10시 이후 근무, 주말 근무를 할 때는 시급의 1.5배(50% 가산)를 받아야 합니다. 평일 시급만 주는 건 불법입니다.",
        "script": "근로기준법 제56조에 따라 연장·야간·휴일근로 시 통상임금의 50%를 가산하여 지급해야 합니다. 가산수당 지급을 요청합니다."
    },

    # 3. 최저임금법 (최저임금 미달) - 형사처벌 대상
    {
        "clause_id": "mandatory_wage_01",
        "category": "🚨 최저임금법 위반",
        "risk_pattern": "시급 환산 시 법정 최저임금(2025년 10,030원)보다 낮음",
        "legal_reference": "최저임금법 제6조 (최저임금의 효력)",
        "explanation": "2025년 최저시급은 10,030원입니다. 월급을 근무시간으로 나눴을 때 이보다 낮으면 형사처벌 대상입니다.",
        "script": "계약서상 급여를 시급으로 환산하면 최저임금법에 미달합니다. 2025년 최저시급 10,030원 기준으로 재계산하여 계약서 수정을 요청합니다."
    },

    # 4. 근로기준법 제54조 (휴게시간 미부여) - 의무 위반
    {
        "clause_id": "mandatory_labor_03",
        "category": "🚨 근로기준법 위반",
        "risk_pattern": "4시간 근무 시 30분, 8시간 근무 시 1시간의 휴게시간을 보장하지 않음",
        "legal_reference": "근로기준법 제54조 (휴게)",
        "explanation": "4시간 일하면 30분, 8시간 일하면 1시간 쉬는 시간을 의무적으로 줘야 합니다. '알아서 쉬라'는 식은 불법입니다.",
        "script": "근로기준법 제54조에 따라 근로시간이 4시간인 경우 30분 이상, 8시간인 경우 1시간 이상의 휴게시간을 근로시간 도중에 부여해야 합니다."
    },

    # 5. 근로자퇴직급여보장법 (퇴직금 미지급) - 1년 이상 근무 시 필수
    {
        "clause_id": "mandatory_retirement_01",
        "category": "🚨 근로자퇴직급여보장법 위반",
        "risk_pattern": "퇴직금 없음, 퇴직금은 월급에 포함, 퇴직금 지급 안 함 등의 문구",
        "legal_reference": "근로자퇴직급여보장법 제8조 (퇴직금제도의 설정)",
        "explanation": "1년 이상, 주 15시간 이상 일하면 반드시 퇴직금을 받아야 합니다. '월급에 포함'이라는 말은 위법입니다.",
        "script": "근로자퇴직급여보장법 제8조에 따라 계속근로기간 1년에 대하여 30일분 이상의 평균임금을 퇴직금으로 지급해야 합니다. 퇴직금 조항 추가를 요청합니다."
    },

    # 6. 하도급법 (부당한 특약 금지) - 갑질 방지
    {
        "clause_id": "mandatory_subcontract_01",
        "category": "🚨 하도급법 위반",
        "risk_pattern": "무한 수정, 횟수 제한 없이 수정, 갑이 만족할 때까지 무상 수정 등의 문구",
        "legal_reference": "하도급거래 공정화에 관한 법률 제3조의4 (부당한 특약 금지)",
        "explanation": "돈은 정해져 있는데 일은 끝없이 시키는 건 불법입니다. '무상 수정 2회' 처럼 횟수를 딱 정해야 합니다.",
        "script": "무제한 수정 요구는 하도급법상 부당한 특약에 해당할 소지가 큽니다. 통상적인 기준인 '무상 수정 2회, 이후 유상 진행'으로 수정을 요청합니다."
    }
]

class AnalysisItem(BaseModel):
    category: str
    original_text: str
    explanation: str
    script: str

class ContractAnalysisResult(BaseModel):
    extracted_text: str
    risk_clauses: list[AnalysisItem]
    summary: str


def get_demo_result() -> ContractAnalysisResult:
    """Return demo analysis result for testing without API calls."""

    demo_contract_text = """근로계약서

1. 근로계약기간: 2024년 1월 1일 ~ 2024년 12월 31일

2. 근무장소: 서울시 강남구 테헤란로 123, ABC 주식회사

3. 업무내용: 매장 판매 및 고객 응대

4. 근로시간: 09:00 ~ 21:00 (휴게시간 별도 협의)

5. 임금
   - 시급: 9,860원
   - 임금지급일: 익월 15일
   - 지급방법: 계좌이체

6. 휴일: 주 1일 (사업장 사정에 따라 변경 가능)

7. 해고: 회사는 업무상 필요에 따라 근로자를 즉시 해고할 수 있다.

8. 기타사항
   - 근로자는 업무상 발생한 손해에 대해 전액 배상해야 한다.
   - 퇴직 후 1년간 동종업계 취업을 금지한다.

본인은 위 근로조건을 확인하고 이에 동의합니다.

2024년 1월 1일
근로자: _____________ (서명)
사용자: ABC 주식회사 대표 홍길동 (인)"""

    demo_analysis = [
        AnalysisItem(
            category="🚨 휴게시간 미명시",
            original_text="09:00 ~ 21:00 (휴게시간 별도 협의)",
            explanation="12시간 근무라면 최소 1시간 30분의 휴게시간이 법으로 보장되어야 해요. '별도 협의'라는 표현은 휴게시간을 안 줄 수도 있다는 뜻이에요. 근로기준법 제54조에 따르면 8시간 일할 때 1시간 이상 쉬어야 하는데, 이게 계약서에 명확하게 안 적혀 있어서 문제가 될 수 있어요.",
            script="휴게시간이 '별도 협의'로 되어 있는데, 근로기준법 제54조에 따르면 8시간 초과 근무 시 1시간 이상의 휴게시간이 보장되어야 합니다. 계약서에 구체적인 휴게시간을 명시해 주실 수 있을까요?"
        ),
        AnalysisItem(
            category="🚨 즉시 해고 조항",
            original_text="회사는 업무상 필요에 따라 근로자를 즉시 해고할 수 있다.",
            explanation="회사가 마음대로 바로 해고할 수 있다는 조항이에요. 법적으로는 30일 전에 미리 알려주거나, 30일치 월급을 줘야 해요. 근로기준법 제26조에서 해고 예고 의무를 정하고 있는데, 이 계약서는 그걸 완전히 무시하고 있어요.",
            script="해고 조항이 '즉시 해고'로 되어 있는데, 근로기준법 제26조에 따르면 해고 시 30일 전 예고 또는 30일분 통상임금 지급이 필요합니다. 이 부분을 법에 맞게 수정해 주실 수 있을까요?"
        ),
        AnalysisItem(
            category="⚠️ 과도한 손해배상 조항",
            original_text="근로자는 업무상 발생한 손해에 대해 전액 배상해야 한다.",
            explanation="일하다 생긴 손해를 전부 물어내라는 조항이에요. 고의나 중대한 과실이 아니면 이렇게 전액을 물릴 수 없어요. 근로기준법 제20조에서는 손해배상액을 미리 정하는 걸 금지하고 있거든요. 실수로 접시 깨뜨렸다고 월급에서 다 떼이면 안 되잖아요?",
            script="손해배상 조항에서 '전액 배상'으로 되어 있는데, 근로기준법상 손해배상액 예정은 금지되어 있고, 실제 손해는 고의나 중과실인 경우에만 청구가 가능합니다. 이 부분 조정이 가능할까요?"
        ),
        AnalysisItem(
            category="⚠️ 불명확한 휴일 조항",
            original_text="주 1일 (사업장 사정에 따라 변경 가능)",
            explanation="주휴일이 보장은 되지만, '사정에 따라 변경'이라는 표현이 모호해요. 쉬는 날이 불규칙해질 수 있어요. 근로기준법 제55조는 주 1회 유급휴일을 보장하는데, 언제 쉬는지도 모르고 일해야 한다면 스케줄 관리가 너무 힘들겠죠?",
            script="휴일 조항에 '사업장 사정에 따라 변경 가능'으로 되어 있는데, 주휴일은 근로기준법 제55조에 따라 확실히 보장되어야 합니다. 휴일 변경 시 최소 며칠 전에 통보해 주신다는 내용을 추가해 주실 수 있을까요?"
        ),
        AnalysisItem(
            category="💡 경업금지 조항",
            original_text="퇴직 후 1년간 동종업계 취업을 금지한다.",
            explanation="퇴직 후 비슷한 업종에 취업하지 못하게 하는 조항이에요. 아르바이트 수준에서는 보통 효력이 없지만, 알아두면 좋아요. 헌법 제15조에서 보장하는 직업선택의 자유와 충돌할 수 있거든요. 카페 알바 하다가 다른 카페로 못 가게 한다는 건 좀 억지죠?",
            script="경업금지 조항이 있는데, 제가 하는 업무 수준에서 이 조항이 꼭 필요한지 여쭤봐도 될까요? 직업선택의 자유와 관련해서 조금 부담이 됩니다."
        )
    ]

    return ContractAnalysisResult(
        extracted_text=demo_contract_text,
        risk_clauses=demo_analysis,
        summary="총 5개의 위험 조항이 발견됐어요. 특히 🚨 표시된 휴게시간과 해고 관련 조항은 꼭 짚고 넘어가야 해요! 나머지도 하나씩 체크해서 손해보지 말자고요 💪"
    )


def analyze_contract_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Optional[ContractAnalysisResult]:
    """
    Analyze a contract image using Gemini Vision to:
    1. Extract full text from the contract (OCR)
    2. Identify risky clauses with exact text for highlighting
    """

    if DEMO_MODE:
        return get_demo_result()

    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # 강행규정 데이터셋을 문자열로 포맷팅
    mandatory_ref = "\n".join([
        f"{i+1}. {clause['legal_reference']} - {clause['risk_pattern']}"
        for i, clause in enumerate(MANDATORY_RISK_CLAUSES)
    ])

    system_prompt = f"""
당신은 사회초년생을 위한 '친절하고 꼼꼼한 AI 법률 멘토, 하이라이터 💡'입니다.
법을 잘 모르는 사용자도 쉽게 이해할 수 있도록, 전문 용어는 정확히 쓰되 설명은 **'해요체(~해요)'**로 부드럽게 풀어서 해주세요.

---
{CLEANING_RULES}

---

**[톤앤매너 (Tone & Manner) 가이드] - 중요!**
1. **말투:** 딱딱한 "~다", "~함" 대신 **"~해요", "~인데요", "~것 같아요"** 같은 부드러운 구어체를 사용하세요.
2. **공감:** 사용자의 불안한 마음을 먼저 다독여주세요. (예: "이 조항은 조금 위험해 보이네요 😢", "걱정 마세요, 법적으로 무효예요! 🛡️")
3. **가독성:** 줄글로 길게 쓰지 말고, 이모지(🚨, ✅, 💡, 🗣️)를 적극 활용해서 눈에 쏙 들어오게 작성하세요.

---

**🎯 [필독] 강행규정 절대 기준 데이터셋**
아래 6대 법령 강행규정을 '정답지'로 삼아 계약서를 분석해주세요.
이 항목들은 어떤 경우에도 위반되어서는 안 되는 **절대적 기준**이에요:

{mandatory_ref}

**[작업 2: 핵심 위험 조항 정밀 진단]**
정제된 텍스트를 바탕으로, 아래 '강행규정 위반 리스트'와 대조하여 불법/독소 조항을 찾아내주세요.

🚨 **[Critical Check List - 최우선 검증 항목]**
(코드 내 MANDATORY_RISK_CLAUSES 리스트를 참고하여, 이와 유사한 패턴이 보이면 즉시 '🚨' 경고를 띄워주세요)
반드시 아래 항목을 먼저 확인하고, 해당 사항이 있으면 **"high" 위험도**로 분류해주세요:

1. **최저임금 위반 ⚠️**
   - 계약서에 명시된 (월급 ÷ 총 근무시간)을 계산해주세요
   - 2024년 최저시급: 9,860원 / 2025년 최저시급: 10,030원
   - 계산 결과가 최저시급보다 낮으면 **명백한 법 위반**이에요

2. **수습기간 악용 ⚠️**
   - 계약 기간이 1년 미만인데 수습기간 급여 감액(예: 90% 지급)이 있는지 확인해주세요
   - 1년 미만 계약에서 수습기간 급여 감액은 **불법**이에요

3. **퇴직금 미지급 조항 ⚠️**
   - "퇴직금은 월급에 포함", "퇴직금 없음", "퇴직금 지급 안 함" 같은 문구가 있는지 확인해주세요
   - 이러한 조항은 근로자퇴직급여보장법 위반이에요

4. **위약금/손해배상 예정 ⚠️**
   - "지각 시 벌금 N원", "조기 퇴사 시 손해배상 N원", "위약금 청구" 등의 문구가 있는지 확인해주세요
   - 근로기준법 제20조(위약 예정의 금지)에 명백히 위반돼요

5. **부당 해고 조항 ⚠️**
   - "사장 재량으로 즉시 해고 가능", "통보 없이 해고", "정당한 사유 없이 해고 가능" 등의 문구 확인해주세요
   - 근로기준법 제23조(해고 등의 제한) 위반이에요

6. **독소 조항 탐지 (가스라이팅/불공정 조항) 🔥**
   - "을은 갑의 지시에 무조건 따른다" → 노예 계약 유형이에요, 근로자의 자율성을 침해해요
   - "민/형사상 이의를 제기하지 않는다" → 법적 권리 포기를 강요하는 무효 조항이에요
   - "휴게시간은 손님이 없을 때 알아서 쉰다" → 근로기준법 제54조(휴게시간 보장) 위반이에요
   - "수습 기간에는 4대 보험 가입 안 함" → 허위 사실이에요, 고용보험법 위반이에요
   - 위 문구나 유사한 뉘앙스 발견 시 **"⚠️ 가스라이팅/불공정 조항"**으로 즉시 경고해주세요

7. **하도급법 위반 (무한 수정 요구) ⚠️**
   - "횟수 제한 없이 무상 수정", "갑이 만족할 때까지 수정", "무제한 재작업" 등의 문구 확인해주세요
   - 하도급거래 공정화에 관한 법률 제3조의4(부당한 특약 금지) 위반이에요
   - 통상적으로 "무상 수정 2회, 이후 유상" 같은 명확한 기준이 필요해요

🎯 **[출력 스타일 가이드 - 반드시 준수]**
- ❌ 금지: "불법 소지가 있습니다", "문제가 될 수 있습니다" 같은 애매한 표현
- ✅ 필수: 위반 사항 발견 시 **"🚨 명백한 근로기준법 위반이에요!"** 같은 단호하면서도 친근한 표현 사용
- ✅ 비교 형식: 반드시 **[계약서 원문] vs [관련 법률/팩트]** 형태로 대조해서 설명
  예시:
  - 계약서: "월급 150만원 (주 40시간, 월 4주)"
  - 계산: 150만원 ÷ 160시간 = 9,375원/시간
  - 법률: 2025년 최저시급 10,030원
  - 결론: 🚨 명백한 최저임금법 위반이에요! (655원 부족해요)

분석 시 추가 확인 사항:
1. 근로시간 및 휴게시간 (근로기준법 제50조, 제54조)
2. 임금 및 수당 (근로기준법 제43조, 제56조)
3. 해고 예고 (근로기준법 제26조)
4. 연차휴가 (근로기준법 제60조)
5. 기타 불리하거나 누락된 조항

**🎨 [출력 형식 (JSON)]**
반드시 아래 JSON 포맷으로 출력해주세요:

{{
    "extracted_text": "줄바꿈이 교정된 계약서 원문",
    "risk_clauses": [
        {{
            "category": "🚨 위반 항목 제목 (예: 퇴직금 미지급 조항)",
            "original_text": "문제가 된 계약서 문구 (하이라이트용 - extracted_text에 포함된 정확한 문장)",
            "explanation": "이게 왜 문제인지 친구에게 설명하듯이 쉽고 친절하게 작성 (해요체 필수! 법적 근거도 자연스럽게 포함)",
            "script": "사장님께 보낼 정중하지만 단호한 요청 메시지 (그대로 복사해서 쓸 수 있게)"
        }}
    ],
    "summary": "전체적인 총평 (예: '전반적으로 괜찮지만, 3조는 꼭 짚고 넘어가야 해요! 꼼꼼히 챙겨서 손해보지 말자고요 💪')"
}}

**중요:**
- original_text는 반드시 extracted_text에 포함된 정확한 문장이어야 해요 (하이라이트 표시에 사용)
- category는 이모지를 포함한 간결한 제목으로 (🚨 위험, ⚠️ 주의, 💡 참고)
- explanation은 법적 근거를 포함하되 친구에게 설명하듯 자연스럽게 작성
- script는 실제로 사용할 수 있는 정중하고 명확한 요청 문구로
- summary는 공감과 응원이 담긴 친근한 총평으로

응답은 반드시 한국어로 작성하고, 모든 설명은 **해요체**로 친근하게 작성해주세요."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
                system_prompt + "\n\n위 계약서 이미지를 분석해주세요.",
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,  # 일관성 있는 법률 분석을 위해 창의성 제한
                response_mime_type="application/json",
                response_schema=ContractAnalysisResult,
            ),
        )

        raw_json = response.text
        logging.info(f"Gemini response: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            return ContractAnalysisResult(**data)
        else:
            return None

    except Exception as e:
        logging.error(f"Contract analysis failed: {e}")
        raise Exception(f"계약서 분석 중 오류가 발생했습니다: {e}")


def analyze_contract_images(image_data_list: list[tuple[bytes, str]]) -> Optional[ContractAnalysisResult]:
    """
    Analyze multiple contract images using Gemini Vision.
    Combines all pages into a single analysis.

    Args:
        image_data_list: List of (image_bytes, mime_type) tuples
    """

    if DEMO_MODE:
        return get_demo_result()

    if len(image_data_list) == 1:
        return analyze_contract_image(image_data_list[0][0], image_data_list[0][1])

    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # 강행규정 데이터셋을 문자열로 포맷팅
    mandatory_ref = "\n".join([
        f"{i+1}. {clause['legal_reference']} - {clause['risk_pattern']}"
        for i, clause in enumerate(MANDATORY_RISK_CLAUSES)
    ])

    system_prompt = f"""
당신은 사회초년생을 위한 '친절하고 꼼꼼한 AI 법률 멘토, 하이라이터 💡'입니다.
법을 잘 모르는 사용자도 쉽게 이해할 수 있도록, 전문 용어는 정확히 쓰되 설명은 **'해요체(~해요)'**로 부드럽게 풀어서 해주세요.

---
{CLEANING_RULES}

---

**[톤앤매너 (Tone & Manner) 가이드] - 중요!**
1. **말투:** 딱딱한 "~다", "~함" 대신 **"~해요", "~인데요", "~것 같아요"** 같은 부드러운 구어체를 사용하세요.
2. **공감:** 사용자의 불안한 마음을 먼저 다독여주세요. (예: "이 조항은 조금 위험해 보이네요 😢", "걱정 마세요, 법적으로 무효예요! 🛡️")
3. **가독성:** 줄글로 길게 쓰지 말고, 이모지(🚨, ✅, 💡, 🗣️)를 적극 활용해서 눈에 쏙 들어오게 작성하세요.

---

**🎯 [필독] 강행규정 절대 기준 데이터셋**
아래 6대 법령 강행규정을 '정답지'로 삼아 계약서를 분석해주세요.
이 항목들은 어떤 경우에도 위반되어서는 안 되는 **절대적 기준**이에요:

{mandatory_ref}

**[작업 2: 핵심 위험 조항 정밀 진단]**
정제된 텍스트를 바탕으로, 아래 '강행규정 위반 리스트'와 대조하여 불법/독소 조항을 찾아내주세요.
(여러 장의 이미지가 제공된 경우, 모든 페이지를 통합하여 분석해주세요.)

🚨 **[Critical Check List - 최우선 검증 항목]**
(코드 내 MANDATORY_RISK_CLAUSES 리스트를 참고하여, 이와 유사한 패턴이 보이면 즉시 '🚨' 경고를 띄워주세요)
반드시 아래 항목을 먼저 확인하고, 해당 사항이 있으면 **"high" 위험도**로 분류해주세요:

1. **최저임금 위반 ⚠️**
   - 계약서에 명시된 (월급 ÷ 총 근무시간)을 계산해주세요
   - 2024년 최저시급: 9,860원 / 2025년 최저시급: 10,030원
   - 계산 결과가 최저시급보다 낮으면 **명백한 법 위반**이에요

2. **수습기간 악용 ⚠️**
   - 계약 기간이 1년 미만인데 수습기간 급여 감액(예: 90% 지급)이 있는지 확인해주세요
   - 1년 미만 계약에서 수습기간 급여 감액은 **불법**이에요

3. **퇴직금 미지급 조항 ⚠️**
   - "퇴직금은 월급에 포함", "퇴직금 없음", "퇴직금 지급 안 함" 같은 문구가 있는지 확인해주세요
   - 이러한 조항은 근로자퇴직급여보장법 위반이에요

4. **위약금/손해배상 예정 ⚠️**
   - "지각 시 벌금 N원", "조기 퇴사 시 손해배상 N원", "위약금 청구" 등의 문구가 있는지 확인해주세요
   - 근로기준법 제20조(위약 예정의 금지)에 명백히 위반돼요

5. **부당 해고 조항 ⚠️**
   - "사장 재량으로 즉시 해고 가능", "통보 없이 해고", "정당한 사유 없이 해고 가능" 등의 문구 확인해주세요
   - 근로기준법 제23조(해고 등의 제한) 위반이에요

6. **독소 조항 탐지 (가스라이팅/불공정 조항) 🔥**
   - "을은 갑의 지시에 무조건 따른다" → 노예 계약 유형이에요, 근로자의 자율성을 침해해요
   - "민/형사상 이의를 제기하지 않는다" → 법적 권리 포기를 강요하는 무효 조항이에요
   - "휴게시간은 손님이 없을 때 알아서 쉰다" → 근로기준법 제54조(휴게시간 보장) 위반이에요
   - "수습 기간에는 4대 보험 가입 안 함" → 허위 사실이에요, 고용보험법 위반이에요
   - 위 문구나 유사한 뉘앙스 발견 시 **"⚠️ 가스라이팅/불공정 조항"**으로 즉시 경고해주세요

7. **하도급법 위반 (무한 수정 요구) ⚠️**
   - "횟수 제한 없이 무상 수정", "갑이 만족할 때까지 수정", "무제한 재작업" 등의 문구 확인해주세요
   - 하도급거래 공정화에 관한 법률 제3조의4(부당한 특약 금지) 위반이에요
   - 통상적으로 "무상 수정 2회, 이후 유상" 같은 명확한 기준이 필요해요

🎯 **[출력 스타일 가이드 - 반드시 준수]**
- ❌ 금지: "불법 소지가 있습니다", "문제가 될 수 있습니다" 같은 애매한 표현
- ✅ 필수: 위반 사항 발견 시 **"🚨 명백한 근로기준법 위반이에요!"** 같은 단호하면서도 친근한 표현 사용
- ✅ 비교 형식: 반드시 **[계약서 원문] vs [관련 법률/팩트]** 형태로 대조해서 설명
  예시:
  - 계약서: "월급 150만원 (주 40시간, 월 4주)"
  - 계산: 150만원 ÷ 160시간 = 9,375원/시간
  - 법률: 2025년 최저시급 10,030원
  - 결론: 🚨 명백한 최저임금법 위반이에요! (655원 부족해요)

분석 시 추가 확인 사항:
1. 근로시간 및 휴게시간 (근로기준법 제50조, 제54조)
2. 임금 및 수당 (근로기준법 제43조, 제56조)
3. 해고 예고 (근로기준법 제26조)
4. 연차휴가 (근로기준법 제60조)
5. 기타 불리하거나 누락된 조항

**🎨 [출력 형식 (JSON)]**
반드시 아래 JSON 포맷으로 출력해주세요:

{{
    "extracted_text": "줄바꿈이 교정된 계약서 원문",
    "risk_clauses": [
        {{
            "category": "🚨 위반 항목 제목 (예: 퇴직금 미지급 조항)",
            "original_text": "문제가 된 계약서 문구 (하이라이트용 - extracted_text에 포함된 정확한 문장)",
            "explanation": "이게 왜 문제인지 친구에게 설명하듯이 쉽고 친절하게 작성 (해요체 필수! 법적 근거도 자연스럽게 포함)",
            "script": "사장님께 보낼 정중하지만 단호한 요청 메시지 (그대로 복사해서 쓸 수 있게)"
        }}
    ],
    "summary": "전체적인 총평 (예: '전반적으로 괜찮지만, 3조는 꼭 짚고 넘어가야 해요! 꼼꼼히 챙겨서 손해보지 말자고요 💪')"
}}

**중요:**
- original_text는 반드시 extracted_text에 포함된 정확한 문장이어야 해요 (하이라이트 표시에 사용)
- category는 이모지를 포함한 간결한 제목으로 (🚨 위험, ⚠️ 주의, 💡 참고)
- explanation은 법적 근거를 포함하되 친구에게 설명하듯 자연스럽게 작성
- script는 실제로 사용할 수 있는 정중하고 명확한 요청 문구로
- summary는 공감과 응원이 담긴 친근한 총평으로

응답은 반드시 한국어로 작성하고, 모든 설명은 **해요체**로 친근하게 작성해주세요."""

    try:
        contents = []
        for idx, (image_bytes, mime_type) in enumerate(image_data_list):
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
            )

        contents.append(system_prompt + f"\n\n위 {len(image_data_list)}장의 계약서 이미지를 분석해주세요.")

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.0,  # 일관성 있는 법률 분석을 위해 창의성 제한
                response_mime_type="application/json",
                response_schema=ContractAnalysisResult,
            ),
        )

        raw_json = response.text
        logging.info(f"Gemini response: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            return ContractAnalysisResult(**data)
        else:
            return None

    except Exception as e:
        logging.error(f"Contract analysis failed: {e}")
        raise Exception(f"계약서 분석 중 오류가 발생했습니다: {e}")


def analyze_contract_files(file_data_list: list[tuple[bytes, str]]) -> Optional[ContractAnalysisResult]:
    """
    Analyze contract files (images or PDFs) using Gemini.
    PDFs are sent directly to Gemini without conversion.
    
    Args:
        file_data_list: List of (file_bytes, mime_type) tuples
                       mime_type can be 'image/jpeg', 'image/png', or 'application/pdf'
    """
    
    if DEMO_MODE:
        return get_demo_result()
    
    if len(file_data_list) == 1 and file_data_list[0][1] != 'application/pdf':
        return analyze_contract_image(file_data_list[0][0], file_data_list[0][1])
    
    from google import genai
    from google.genai import types
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    client = genai.Client(api_key=api_key)
    
    system_prompt = """당신은 한국 근로기준법 전문가이자 계약서 분석 AI입니다.

**작업 1: 텍스트 추출 (OCR)**
제공된 계약서 파일(이미지 또는 PDF)에서 텍스트를 정확히 추출하세요.
원본 형식(줄바꿈, 번호 등)을 최대한 유지하세요.

**작업 2: 위험 조항 분석**
추출된 텍스트에서 근로자에게 불리한 조항을 찾으세요.

분석 시 확인 사항:
1. 근로시간 및 휴게시간 (근로기준법 제50조, 제54조)
2. 임금 및 수당 (근로기준법 제43조, 제56조)
3. 해고 예고 (근로기준법 제26조)
4. 연차휴가 (근로기준법 제60조)
5. 기타 불리하거나 누락된 조항

**🎨 [출력 형식 (JSON)]**
반드시 아래 JSON 포맷으로 출력하세요:

{{
    "extracted_text": "줄바꿈이 교정된 계약서 원문",
    "risk_clauses": [
        {{
            "category": "🚨 위반 항목 제목 (예: 퇴직금 미지급 조항)",
            "original_text": "문제가 된 계약서 문구 (하이라이트용 - extracted_text에 포함된 정확한 문장)",
            "explanation": "이게 왜 문제인지 친구에게 설명하듯이 쉽고 친절하게 작성 (해요체 필수! 법적 근거도 자연스럽게 포함)",
            "script": "사장님께 보낼 정중하지만 단호한 요청 메시지 (그대로 복사해서 쓸 수 있게)"
        }}
    ],
    "summary": "전체적인 총평 (예: '전반적으로 괜찮지만, 3조는 꼭 짚고 넘어가야 해요! 꼼꼼히 챙겨서 손해보지 말자고요 💪')"
}}

**중요:**
- original_text는 반드시 extracted_text에 포함된 정확한 문장이어야 합니다 (하이라이트 표시에 사용)
- category는 이모지를 포함한 간결한 제목으로 (🚨 위험, ⚠️ 주의, 💡 참고)
- explanation은 법적 근거를 포함하되 친구에게 설명하듯 자연스럽게 작성
- script는 실제로 사용할 수 있는 정중하고 명확한 요청 문구로
- summary는 공감과 응원이 담긴 친근한 총평으로

응답은 반드시 한국어로 작성하세요."""

    try:
        contents = []
        for idx, (file_bytes, mime_type) in enumerate(file_data_list):
            contents.append(
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type,
                )
            )
        
        file_count = len(file_data_list)
        contents.append(system_prompt + f"\n\n위 {file_count}개의 계약서 파일을 분석해주세요.")
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ContractAnalysisResult,
            ),
        )
        
        raw_json = response.text
        logging.info(f"Gemini response: {raw_json}")
        
        if raw_json:
            data = json.loads(raw_json)
            return ContractAnalysisResult(**data)
        else:
            return None
            
    except Exception as e:
        logging.error(f"Contract analysis failed: {e}")
        raise Exception(f"계약서 분석 중 오류가 발생했습니다: {e}")


def get_risk_color(category: str) -> str:
    """Return background color based on category emoji (Modern premium design)."""
    if "🚨" in category:
        return "#FEF2F2"
    elif "⚠️" in category:
        return "#FFFBEB"
    elif "💡" in category:
        return "#ECFDF5"
    return "#FFFBEB"

def get_risk_border_color(category: str) -> str:
    """Return border/accent color based on category emoji (Modern premium design)."""
    if "🚨" in category:
        return "#DC2626"
    elif "⚠️" in category:
        return "#F59E0B"
    elif "💡" in category:
        return "#10B981"
    return "#F59E0B"

def get_risk_emoji(category: str) -> str:
    """Extract emoji from category."""
    if "🚨" in category:
        return "🚨"
    elif "⚠️" in category:
        return "⚠️"
    elif "💡" in category:
        return "💡"
    return "⚠️"

def get_risk_label(category: str) -> str:
    """Extract Korean label from category."""
    # Extract text after emoji
    if "🚨" in category:
        return "위험"
    elif "⚠️" in category:
        return "주의"
    elif "💡" in category:
        return "참고"
    return "주의"


def highlight_text_with_risks(contract_text: str, analysis: list[AnalysisItem]) -> str:
    """
    Apply inline highlights with hover tooltips and click-to-modal functionality.
    Uses pure CSS modal with checkbox hack (no JavaScript needed for Streamlit).
    Returns HTML with:
    - Highlighted risk text with colored background
    - Tooltip appearing on hover (like memo box)
    - Modal popup on click with full details (pure CSS)
    """
    import html

    safe_text = html.escape(contract_text)
    highlighted = safe_text

    modal_data_list = []

    for idx, item in enumerate(sorted(analysis, key=lambda x: len(x.original_text), reverse=True), 1):
        safe_original = html.escape(item.original_text)

        if safe_original and safe_original in highlighted:
            bg_color = get_risk_color(item.category)
            border_color = get_risk_border_color(item.category)
            emoji = get_risk_emoji(item.category)
            label = get_risk_label(item.category)

            safe_category = html.escape(item.category)
            safe_explanation = html.escape(item.explanation)
            safe_script = html.escape(item.script)

            modal_id = f"risk-modal-{idx}"
            checkbox_id = f"modal-toggle-{idx}"

            modal_data_list.append({
                "id": modal_id,
                "checkbox_id": checkbox_id,
                "emoji": emoji,
                "label": label,
                "category": safe_category,
                "original": safe_original,
                "explanation": safe_explanation,
                "script": safe_script,
                "border_color": border_color
            })

            highlight_html = f'''<span class="risk-highlight-wrapper"><label for="{checkbox_id}" class="risk-mark-label"><mark class="risk-mark" style="background: {bg_color}; border-bottom: 2px solid {border_color}; padding: 1px 2px; border-radius: 3px; cursor: pointer;">{safe_original}</mark></label><span class="risk-tooltip"><span class="tooltip-header"><span style="display:inline-block;width:8px;height:8px;background:{border_color};border-radius:50%;margin-right:6px;"></span>{label}</span><span class="tooltip-content">{safe_category}</span><span class="tooltip-hint">클릭하여 상세 정보 확인</span></span></span>'''

            highlighted = highlighted.replace(safe_original, highlight_html, 1)

    return highlighted, modal_data_list


def generate_css_modals_html(modal_data_list: list) -> str:
    """Generate pure CSS modal HTML using checkbox hack."""
    modals = ""
    for data in modal_data_list:
        modals += f'''
<input type="checkbox" id="{data['checkbox_id']}" class="modal-toggle" />
<div class="css-modal-overlay">
    <label for="{data['checkbox_id']}" class="modal-overlay-bg"></label>
    <div class="modal-content">
        <div class="modal-header">
            <div class="modal-title">
                <span class="risk-badge">{data['emoji']} {data['label']}</span>
                <span class="risk-category">{data['category']}</span>
            </div>
            <label for="{data['checkbox_id']}" class="modal-close">&times;</label>
        </div>
        <div class="modal-body">
            <div class="modal-section">
                <div class="modal-section-title">📍 해당 조항</div>
                <div class="modal-section-content modal-original-text">"{data['original']}"</div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">💡 왜 문제가 될 수 있나요?</div>
                <div class="modal-section-content modal-issue-section">{data['explanation']}</div>
            </div>
            <div class="modal-section modal-script-section">
                <div class="modal-section-title">💬 이렇게 말해보세요</div>
                <div class="modal-section-content modal-script">"{data['script']}"</div>
            </div>
        </div>
    </div>
</div>'''
    return modals


def generate_modals_html(modal_data_list: list) -> str:
    """Generate modal HTML for each risk clause."""
    modals = ""
    for data in modal_data_list:
        modals += f'''
<div id="{data['id']}" class="modal-overlay" onclick="closeModalOnOverlay(event, '{data['id']}')">
    <div class="modal-content" onclick="event.stopPropagation()">
        <div class="modal-header">
            <div class="modal-title">
                <span class="risk-badge">{data['emoji']} {data['label']}</span>
                <span class="risk-category">{data['category']}</span>
            </div>
            <button class="modal-close" onclick="closeRiskModal('{data['id']}')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="modal-section">
                <div class="modal-section-title">📍 해당 조항</div>
                <div class="modal-section-content modal-original-text">"{data['original']}"</div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">💡 왜 문제가 될 수 있나요?</div>
                <div class="modal-section-content">{data['explanation']}</div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">💬 이렇게 말해보세요</div>
                <div class="modal-section-content modal-script">"{data['script']}"</div>
            </div>
        </div>
    </div>
</div>'''
    return modals


def generate_modal_script() -> str:
    """Generate JavaScript for modal open/close functionality.
    Note: This returns empty string as Streamlit strips inline scripts.
    The actual script needs to be injected via st.components.v1.html()
    """
    return ""


def get_modal_javascript() -> str:
    """Return the JavaScript code that needs to be injected via st.components.v1.html()"""
    return '''
<script>
window.openRiskModal = function(modalId) {
    const modal = window.parent.document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        window.parent.document.body.style.overflow = 'hidden';
    }
};

window.closeRiskModal = function(modalId) {
    const modal = window.parent.document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        window.parent.document.body.style.overflow = '';
    }
};

window.parent.document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = window.parent.document.querySelectorAll('.modal-overlay.active');
        modals.forEach(function(modal) {
            modal.classList.remove('active');
        });
        window.parent.document.body.style.overflow = '';
    }
});
</script>
'''


def generate_annotation_cards(analysis: list[AnalysisItem]) -> str:
    """
    Generate expandable annotation cards for each risk clause.
    These appear below the document as clickable cards.
    """
    import html

    if not analysis:
        return ""

    cards_html = '<div class="annotation-cards">'

    for idx, item in enumerate(analysis, 1):
        bg_color = get_risk_color(item.category)
        border_color = get_risk_border_color(item.category)
        emoji = get_risk_emoji(item.category)
        label = get_risk_label(item.category)

        safe_original = html.escape(item.original_text)
        safe_category = html.escape(item.category)
        safe_explanation = html.escape(item.explanation)
        safe_script = html.escape(item.script)

        cards_html += f'''
<details class="annotation-card" style="border-left: 4px solid {border_color};">
<summary class="annotation-summary" style="background: {bg_color};">
<span class="annotation-number" style="background: {border_color};">{idx}</span>
<span class="annotation-title">{safe_category}</span>
</summary>
<div class="annotation-detail">
<div class="annotation-quote">
<strong>📍 해당 문구:</strong><br>
"{safe_original}"
</div>
<div class="annotation-section">
<div class="annotation-label">💡 왜 문제가 될 수 있나요?</div>
<div class="annotation-content">{safe_explanation}</div>
</div>
<div class="annotation-section">
<div class="annotation-label">💬 이렇게 말해보세요</div>
<div class="annotation-script">"{safe_script}"</div>
</div>
</div>
</details>'''

    cards_html += '</div>'
    return cards_html


# ============================================================
# VECTOR DB FUNCTIONS (For chat_with_contract RAG system)
# ============================================================

def build_vector_db(data_folder: str = "./data", persist_directory: str = "./chroma_db") -> Optional[Chroma]:
    """
    Build ChromaDB vector database from PDF files in data folder.

    Args:
        data_folder: Path to folder containing PDF files
        persist_directory: Path to persist the vector database

    Returns:
        Chroma vectorstore instance or None if build fails
    """
    if not VECTOR_DB_AVAILABLE:
        logging.error("Vector DB dependencies not installed. Run: pip install langchain langchain-community langchain-google-genai langchain-chroma chromadb pypdf")
        return None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    print(f"📂 Scanning PDF files in {data_folder}...")

    # Get all PDF files
    pdf_files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]

    if not pdf_files:
        print(f"❌ No PDF files found in {data_folder}")
        return None

    print(f"✅ Found {len(pdf_files)} PDF files")

    # Load and split documents
    all_documents = []
    total_pages = 0

    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_folder, pdf_file)
        print(f"   📄 Loading {pdf_file}...")

        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            total_pages += len(documents)
            all_documents.extend(documents)
            print(f"      ✓ {len(documents)} pages loaded")
        except Exception as e:
            print(f"      ✗ Error loading {pdf_file}: {e}")
            continue

    if not all_documents:
        print("❌ No documents loaded")
        return None

    print(f"\n📊 Total: {len(pdf_files)} files, {total_pages} pages")
    print(f"🔪 Splitting documents into chunks...")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    splits = text_splitter.split_documents(all_documents)
    print(f"✅ Created {len(splits)} chunks")

    # Create embeddings and vector store
    print(f"🧮 Creating embeddings with Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

    print(f"💾 Building ChromaDB vector store at {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    print(f"✅ Vector DB built successfully!")
    print(f"   📊 Files: {len(pdf_files)} | Pages: {total_pages} | Chunks: {len(splits)}")

    return vectorstore


def get_vector_store(persist_directory: str = "./chroma_db") -> Optional[Chroma]:
    """
    Load existing ChromaDB vector store.

    Args:
        persist_directory: Path to persisted vector database

    Returns:
        Chroma vectorstore instance or None if not found
    """
    if not VECTOR_DB_AVAILABLE:
        logging.warning("Vector DB dependencies not available")
        return None

    if not os.path.exists(persist_directory):
        logging.warning(f"Vector DB not found at {persist_directory}. Run build_db.py first.")
        return None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    return vectorstore


def chat_with_contract(question: str, contract_text: str = "", use_rag: bool = True) -> dict:
    """
    RAG-based chat function for answering questions about labor law.

    Args:
        question: User's question
        contract_text: Optional contract text for context
        use_rag: Whether to use RAG (vector DB search) or direct answer

    Returns:
        dict with 'answer' and 'sources' keys
    """
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # Build context from RAG if enabled
    context_sources = []
    if use_rag and VECTOR_DB_AVAILABLE:
        vectorstore = get_vector_store()
        if vectorstore:
            # Search for relevant documents
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)  # Updated method name for newer langchain
            context_sources = [doc.page_content for doc in docs]

    # Build prompt
    system_prompt = """당신은 한국 근로기준법 전문가입니다.
사용자의 질문에 친절하고 정확하게 답변해주세요.

답변 시:
1. 관련 법조항을 명확히 인용하세요
2. 쉬운 말로 설명하세요
3. 실제 예시를 들어 설명하면 더 좋습니다

답변 형식:
📌 **핵심 답변**: (한 문장 요약)

⚖️ **법적 근거**:
(관련 법조항 인용)

🗣️ **쉬운 설명**:
(일반인이 이해하기 쉽게 풀어서 설명)
"""

    user_prompt = f"질문: {question}\n\n"

    if contract_text:
        user_prompt += f"계약서 내용:\n{contract_text}\n\n"

    if context_sources:
        user_prompt += "참고 자료:\n"
        for i, source in enumerate(context_sources, 1):
            user_prompt += f"\n[자료 {i}]\n{source}\n"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[system_prompt + "\n\n" + user_prompt],
            config=types.GenerateContentConfig(
                temperature=0.3,  # 법률 상담은 약간의 유연성 허용
            ),
        )

        answer = response.text

        return {
            "answer": answer,
            "sources": context_sources if use_rag else [],
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Chat failed: {e}")
        return {
            "answer": f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {e}",
            "sources": [],
            "status": "error"
        }
