# Backend logic for 알바·단기계약 리스크 하이라이터

import os
from google import genai


def chat_with_contract(user_question: str, contract_context: str) -> str:
    """
    계약서 내용을 기반으로 사용자의 추가 질문에 답변합니다.
    
    Args:
        user_question: 사용자의 질문
        contract_context: 분석된 계약서 원문 텍스트
    
    Returns:
        AI의 답변 문자열
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "API 키가 설정되지 않았습니다. 관리자에게 문의해주세요."
    
    client = genai.Client(api_key=api_key)
    
    system_prompt = """당신은 한국 노동법 전문가이자 친절한 상담사입니다. 
사용자가 업로드한 계약서를 분석한 결과를 바탕으로 추가 질문에 답변해주세요.

다음 원칙을 따라주세요:
1. 쉬운 말로 설명해주세요 (법률 용어는 괄호로 풀이)
2. 근로기준법 등 관련 법률을 인용할 때는 조항 번호를 명시해주세요
3. 사용자가 걱정하는 부분에 대해 공감해주세요
4. 실질적으로 도움이 되는 조언을 해주세요
5. 답변은 간결하게 3-5문장으로 해주세요
6. 법적 조언이 아닌 정보 제공임을 명시해주세요"""

    prompt = f"""[계약서 원문]
{contract_context}

[사용자 질문]
{user_question}

위 계약서 내용을 참고하여 사용자의 질문에 친절하게 답변해주세요."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-06-05",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=500
            )
        )
        
        if response.text:
            return response.text
        else:
            return "죄송해요, 답변을 생성하지 못했어요. 다시 질문해주세요!"
            
    except Exception as e:
        return f"오류가 발생했어요: {str(e)}"
