import os
import json
import logging
from typing import Optional, List

from pydantic import BaseModel

DEMO_MODE = True

class RiskClause(BaseModel):
    clause_id: str
    original_text: str
    risk_level: str
    issue_summary: str
    legal_reference: str
    legal_article: str
    simple_explanation: str
    negotiation_script: str

class ContractAnalysisResult(BaseModel):
    extracted_text: str
    risk_clauses: list[RiskClause]
    overall_risk_level: str
    summary: str
    missing_clauses: list[str]


def get_demo_result() -> ContractAnalysisResult:
    """Return demo analysis result for testing without API calls."""
    
    demo_extracted_text = """근로계약서

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

    demo_risk_clauses = [
        RiskClause(
            clause_id="risk_1",
            original_text="09:00 ~ 21:00 (휴게시간 별도 협의)",
            risk_level="high",
            issue_summary="12시간 근무에 휴게시간이 명시되지 않음",
            legal_reference="근로기준법 제54조",
            legal_article="사용자는 근로시간이 4시간인 경우에는 30분 이상, 8시간인 경우에는 1시간 이상의 휴게시간을 근로시간 도중에 주어야 한다.",
            simple_explanation="12시간 근무라면 최소 1시간 30분의 휴게시간이 법으로 보장되어야 해요. '별도 협의'라는 표현은 휴게시간을 안 줄 수도 있다는 뜻이에요.",
            negotiation_script="휴게시간이 '별도 협의'로 되어 있는데, 근로기준법 제54조에 따르면 8시간 초과 근무 시 1시간 이상의 휴게시간이 보장되어야 합니다. 계약서에 구체적인 휴게시간을 명시해 주실 수 있을까요?"
        ),
        RiskClause(
            clause_id="risk_2",
            original_text="회사는 업무상 필요에 따라 근로자를 즉시 해고할 수 있다.",
            risk_level="high",
            issue_summary="즉시 해고 조항 - 해고 예고 의무 위반",
            legal_reference="근로기준법 제26조",
            legal_article="사용자는 근로자를 해고하려면 적어도 30일 전에 예고를 하여야 하고, 30일 전에 예고를 하지 아니하였을 때에는 30일분 이상의 통상임금을 지급하여야 한다.",
            simple_explanation="회사가 마음대로 바로 해고할 수 있다는 조항이에요. 법적으로는 30일 전에 미리 알려주거나, 30일치 월급을 줘야 해요.",
            negotiation_script="해고 조항이 '즉시 해고'로 되어 있는데, 근로기준법 제26조에 따르면 해고 시 30일 전 예고 또는 30일분 통상임금 지급이 필요합니다. 이 부분을 법에 맞게 수정해 주실 수 있을까요?"
        ),
        RiskClause(
            clause_id="risk_3",
            original_text="근로자는 업무상 발생한 손해에 대해 전액 배상해야 한다.",
            risk_level="medium",
            issue_summary="과도한 손해배상 조항",
            legal_reference="민법 제398조, 근로기준법 제20조",
            legal_article="근로기준법 제20조: 사용자는 근로계약 불이행에 대한 위약금 또는 손해배상액을 예정하는 계약을 체결하지 못한다.",
            simple_explanation="일하다 생긴 손해를 전부 물어내라는 조항이에요. 고의나 중대한 과실이 아니면 이렇게 전액을 물릴 수 없어요.",
            negotiation_script="손해배상 조항에서 '전액 배상'으로 되어 있는데, 근로기준법상 손해배상액 예정은 금지되어 있고, 실제 손해는 고의나 중과실인 경우에만 청구가 가능합니다. 이 부분 조정이 가능할까요?"
        ),
        RiskClause(
            clause_id="risk_4",
            original_text="주 1일 (사업장 사정에 따라 변경 가능)",
            risk_level="medium",
            issue_summary="휴일이 사업장 사정에 따라 변경될 수 있음",
            legal_reference="근로기준법 제55조",
            legal_article="사용자는 근로자에게 1주에 평균 1회 이상의 유급휴일을 보장하여야 한다.",
            simple_explanation="주휴일이 보장은 되지만, '사정에 따라 변경'이라는 표현이 모호해요. 쉬는 날이 불규칙해질 수 있어요.",
            negotiation_script="휴일 조항에 '사업장 사정에 따라 변경 가능'으로 되어 있는데, 주휴일은 근로기준법 제55조에 따라 확실히 보장되어야 합니다. 휴일 변경 시 최소 며칠 전에 통보해 주신다는 내용을 추가해 주실 수 있을까요?"
        ),
        RiskClause(
            clause_id="risk_5",
            original_text="퇴직 후 1년간 동종업계 취업을 금지한다.",
            risk_level="low",
            issue_summary="경업금지 조항 - 직업선택의 자유 제한",
            legal_reference="헌법 제15조",
            legal_article="모든 국민은 직업선택의 자유를 가진다.",
            simple_explanation="퇴직 후 비슷한 업종에 취업하지 못하게 하는 조항이에요. 아르바이트 수준에서는 보통 효력이 없지만, 알아두면 좋아요.",
            negotiation_script="경업금지 조항이 있는데, 제가 하는 업무 수준에서 이 조항이 꼭 필요한지 여쭤봐도 될까요? 직업선택의 자유와 관련해서 조금 부담이 됩니다."
        )
    ]
    
    demo_missing_clauses = [
        "연차휴가에 대한 규정이 없습니다 (근로기준법 제60조)",
        "연장근로수당에 대한 규정이 없습니다 (근로기준법 제56조)",
        "4대 보험 가입 여부가 명시되지 않았습니다"
    ]
    
    return ContractAnalysisResult(
        extracted_text=demo_extracted_text,
        risk_clauses=demo_risk_clauses,
        overall_risk_level="high",
        summary="총 5개의 위험 조항이 발견되었습니다. 특히 휴게시간과 해고 관련 조항을 꼭 확인하세요!",
        missing_clauses=demo_missing_clauses
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
    
    system_prompt = """당신은 한국 근로기준법 전문가이자 계약서 분석 AI입니다.

**작업 1: 텍스트 추출 (OCR)**
계약서 이미지에서 모든 텍스트를 정확히 추출하세요. 
원본 형식(줄바꿈, 번호 등)을 최대한 유지하세요.

**작업 2: 위험 조항 분석**
추출된 텍스트에서 근로자에게 불리한 조항을 찾으세요.

분석 시 확인 사항:
1. 근로시간 및 휴게시간 (근로기준법 제50조, 제54조)
2. 임금 및 수당 (근로기준법 제43조, 제56조)
3. 해고 예고 (근로기준법 제26조)
4. 연차휴가 (근로기준법 제60조)
5. 기타 불리하거나 누락된 조항

**중요: 각 위험 조항의 original_text는 반드시 extracted_text에 포함된 정확한 문장이어야 합니다.**
이 텍스트는 하이라이트 표시에 사용됩니다.

각 위험 조항에 대해:
- clause_id: 고유 ID (예: "risk_1", "risk_2")
- original_text: 계약서에서 발견된 정확한 문장 (하이라이트용)
- risk_level: "high", "medium", "low"
- issue_summary: 문제 요약 (쉬운 한국어)
- legal_reference: 관련 법조항 (예: "근로기준법 제54조")
- legal_article: 법조항 원문
- simple_explanation: 쉬운 설명
- negotiation_script: 협상 스크립트 (정중하지만 법적 근거 포함)

응답은 반드시 한국어로 작성하세요."""

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


def get_risk_color(risk_level: str) -> str:
    """Return background color based on risk level (Modern premium design)."""
    colors = {
        "high": "#FEF2F2",
        "medium": "#FFFBEB",
        "low": "#ECFDF5"
    }
    return colors.get(risk_level.lower(), "#FFFBEB")

def get_risk_border_color(risk_level: str) -> str:
    """Return border/accent color based on risk level (Modern premium design)."""
    colors = {
        "high": "#DC2626",
        "medium": "#F59E0B",
        "low": "#10B981"
    }
    return colors.get(risk_level.lower(), "#F59E0B")

def get_risk_emoji(risk_level: str) -> str:
    """Return emoji based on risk level."""
    emojis = {
        "high": "🚨",
        "medium": "⚠️",
        "low": "💡"
    }
    return emojis.get(risk_level.lower(), "⚠️")


def get_risk_label(risk_level: str) -> str:
    """Return Korean label based on risk level."""
    labels = {
        "high": "위험",
        "medium": "주의",
        "low": "참고"
    }
    return labels.get(risk_level.lower(), "주의")


def highlight_text_with_risks(extracted_text: str, risk_clauses: list[RiskClause]) -> str:
    """
    Apply inline highlights with hover tooltips and click-to-modal functionality.
    Uses pure CSS modal with checkbox hack (no JavaScript needed for Streamlit).
    Returns HTML with:
    - Highlighted risk text with colored background
    - Tooltip appearing on hover (like memo box)
    - Modal popup on click with full details (pure CSS)
    """
    import html
    
    safe_text = html.escape(extracted_text)
    highlighted = safe_text
    
    modal_data_list = []
    
    for idx, clause in enumerate(sorted(risk_clauses, key=lambda x: len(x.original_text), reverse=True), 1):
        safe_original = html.escape(clause.original_text)
        
        if safe_original and safe_original in highlighted:
            bg_color = get_risk_color(clause.risk_level)
            border_color = get_risk_border_color(clause.risk_level)
            emoji = get_risk_emoji(clause.risk_level)
            label = get_risk_label(clause.risk_level)
            
            safe_summary = html.escape(clause.issue_summary)
            safe_explanation = html.escape(clause.simple_explanation)
            safe_legal_ref = html.escape(clause.legal_reference)
            safe_legal_article = html.escape(clause.legal_article)
            safe_script = html.escape(clause.negotiation_script)
            
            modal_id = f"risk-modal-{idx}"
            checkbox_id = f"modal-toggle-{idx}"
            
            modal_data_list.append({
                "id": modal_id,
                "checkbox_id": checkbox_id,
                "emoji": emoji,
                "label": label,
                "summary": safe_summary,
                "original": safe_original,
                "explanation": safe_explanation,
                "legal_ref": safe_legal_ref,
                "legal_article": safe_legal_article,
                "script": safe_script,
                "risk_level": clause.risk_level,
                "border_color": border_color
            })
            
            highlight_html = f'''<span class="risk-highlight-wrapper"><label for="{checkbox_id}" class="risk-mark-label"><mark class="risk-mark" style="background: {bg_color}; border-bottom: 2px solid {border_color}; padding: 1px 2px; border-radius: 3px; cursor: pointer;">{safe_original}</mark></label><span class="risk-tooltip"><span class="tooltip-header"><span style="display:inline-block;width:8px;height:8px;background:{border_color};border-radius:50%;margin-right:6px;"></span>{label}</span><span class="tooltip-content">{safe_summary}</span><span class="tooltip-hint">클릭하여 상세 정보 확인</span></span></span>'''
            
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
                <span class="risk-badge {data['risk_level']}">{data['label']}</span>
            </div>
            <label for="{data['checkbox_id']}" class="modal-close">&times;</label>
        </div>
        <div class="modal-body">
            <div class="modal-section">
                <div class="modal-section-title">해당 조항</div>
                <div class="modal-section-content modal-original-text">"{data['original']}"</div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">문제점</div>
                <div class="modal-section-content">{data['explanation']}</div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">법적 근거</div>
                <div class="modal-section-content modal-legal-ref">
                    <strong>{data['legal_ref']}</strong><br><br>
                    {data['legal_article']}
                </div>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">협상 가이드</div>
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
                <span class="risk-badge {data['risk_level']}">{data['emoji']} {data['label']}</span>
                {data['summary']}
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
                <div class="modal-section-title">📚 법적 근거</div>
                <div class="modal-section-content modal-legal-ref">
                    <strong>{data['legal_ref']}</strong><br><br>
                    {data['legal_article']}
                </div>
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


def generate_annotation_cards(risk_clauses: list[RiskClause]) -> str:
    """
    Generate expandable annotation cards for each risk clause.
    These appear below the document as clickable cards.
    """
    import html
    
    if not risk_clauses:
        return ""
    
    cards_html = '<div class="annotation-cards">'
    
    for idx, clause in enumerate(risk_clauses, 1):
        bg_color = get_risk_color(clause.risk_level)
        border_color = get_risk_border_color(clause.risk_level)
        emoji = get_risk_emoji(clause.risk_level)
        label = get_risk_label(clause.risk_level)
        
        safe_original = html.escape(clause.original_text)
        safe_summary = html.escape(clause.issue_summary)
        safe_explanation = html.escape(clause.simple_explanation)
        safe_legal_ref = html.escape(clause.legal_reference)
        safe_legal_article = html.escape(clause.legal_article)
        safe_script = html.escape(clause.negotiation_script)
        
        cards_html += f'''
<details class="annotation-card" style="border-left: 4px solid {border_color};">
<summary class="annotation-summary" style="background: {bg_color};">
<span class="annotation-number" style="background: {border_color};">{idx}</span>
<span class="annotation-title">{emoji} {safe_summary}</span>
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
<div class="annotation-label">📚 법적 근거</div>
<div class="annotation-legal">
<strong>{safe_legal_ref}</strong><br>
{safe_legal_article}
</div>
</div>
<div class="annotation-section">
<div class="annotation-label">💬 이렇게 말해보세요</div>
<div class="annotation-script">"{safe_script}"</div>
</div>
</div>
</details>'''
    
    cards_html += '</div>'
    return cards_html
