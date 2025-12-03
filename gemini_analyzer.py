import os
import json
import logging
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Secrets에서 API 키를 설정해주세요.")

client = genai.Client(api_key=api_key)

class RiskClause(BaseModel):
    clause_text: str
    risk_level: str
    issue_summary: str
    legal_reference: str
    legal_article: str
    simple_explanation: str
    negotiation_script: str

class ContractAnalysisResult(BaseModel):
    risk_clauses: list[RiskClause]
    overall_risk_level: str
    summary: str
    missing_clauses: list[str]

def analyze_contract_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Optional[ContractAnalysisResult]:
    """
    Analyze a contract image using Gemini Vision to detect risky clauses.
    Uses blueprint:python_gemini integration.
    """
    
    system_prompt = """당신은 한국 근로기준법 전문가이자 계약서 분석 AI입니다.
업로드된 계약서 이미지를 분석하여 근로자에게 불리한 조항을 찾아주세요.

분석 시 다음을 확인하세요:
1. 근로시간 및 휴게시간 (근로기준법 제50조, 제54조)
2. 임금 및 수당 (근로기준법 제43조, 제56조)
3. 해고 예고 (근로기준법 제26조)
4. 연차휴가 (근로기준법 제60조)
5. 기타 불리하거나 누락된 조항

각 위험 조항에 대해:
- 해당 조항 텍스트
- 위험 수준 (high/medium/low)
- 문제 요약 (쉬운 한국어로)
- 관련 법조항
- 법조항 원문
- 쉬운 설명
- 협상 스크립트 (정중하지만 법적 근거를 포함)

응답은 반드시 한국어로 작성하세요.
JSON 형식으로 응답하세요."""

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
        "high": "#e74c3c",
        "medium": "#f39c12",
        "low": "#27ae60"
    }
    return colors.get(risk_level.lower(), "#f39c12")


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
        "high": "높은 위험",
        "medium": "주의 필요",
        "low": "참고 사항"
    }
    return labels.get(risk_level.lower(), "주의 필요")
