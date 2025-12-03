import os
import json
import logging
from typing import Optional, List

from google import genai
from google.genai import types
from pydantic import BaseModel

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Secrets에서 API 키를 설정해주세요.")

client = genai.Client(api_key=api_key)

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

def analyze_contract_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Optional[ContractAnalysisResult]:
    """
    Analyze a contract image using Gemini Vision to:
    1. Extract full text from the contract (OCR)
    2. Identify risky clauses with exact text for highlighting
    """
    
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
    """Return color code based on risk level."""
    colors = {
        "high": "#FFCDD2",
        "medium": "#FFE0B2",
        "low": "#C8E6C9"
    }
    return colors.get(risk_level.lower(), "#FFE0B2")

def get_risk_border_color(risk_level: str) -> str:
    """Return border color based on risk level."""
    colors = {
        "high": "#EF5350",
        "medium": "#FFA726",
        "low": "#66BB6A"
    }
    return colors.get(risk_level.lower(), "#FFA726")

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
    Apply inline highlights with hover tooltips to the extracted text.
    Returns HTML with highlighted risk sections and embedded tooltips.
    Uses CSS :has() selector for proper sibling-based toggle without nesting divs in spans.
    """
    import html
    
    safe_text = html.escape(extracted_text)
    highlighted = safe_text
    
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
            
            highlight_html = f'''<mark class="risk-mark" style="background: {bg_color}; border-bottom: 3px solid {border_color}; padding: 2px 4px; border-radius: 4px; cursor: help;" title="{emoji} {safe_summary} - 클릭하여 상세 보기">{safe_original}<sup style="background: {border_color}; color: white; padding: 1px 6px; border-radius: 8px; font-size: 0.7rem; margin-left: 3px; font-weight: 600;">{emoji}</sup></mark>'''
            
            highlighted = highlighted.replace(safe_original, highlight_html, 1)
    
    return highlighted


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
