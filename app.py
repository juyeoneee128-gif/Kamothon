import streamlit as st
from PIL import Image
import io
import os

st.set_page_config(
    page_title="계약서 리스크 하이라이터",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    .upload-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    .result-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff8e6;
        border-left: 4px solid #f5a623;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #fdecea;
        border-left: 4px solid #e74c3c;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e8f4fd;
        border-left: 4px solid #2196f3;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .script-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .step-header {
        color: #1a1a2e;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .friendly-text {
        color: #555;
        font-size: 1rem;
        line-height: 1.6;
    }
    .reassurance-text {
        color: #2e7d32;
        font-size: 0.95rem;
        font-style: italic;
    }
    .error-text {
        color: #c62828;
        font-size: 0.95rem;
    }
    .summary-box {
        background-color: #f5f5f5;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧾 계약서 리스크 하이라이터")
st.markdown("##### 복잡한 계약서, 위험 조항은 우리가 찾아드립니다")
st.markdown("---")

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analysis_error' not in st.session_state:
    st.session_state.analysis_error = None

def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    return mime_types.get(ext, 'image/jpeg')

def get_risk_box_class(risk_level: str) -> str:
    """Return CSS class based on risk level."""
    if risk_level.lower() == 'high':
        return 'danger-box'
    return 'warning-box'

def get_risk_emoji(risk_level: str) -> str:
    """Return emoji based on risk level."""
    emojis = {
        'high': '🚨',
        'medium': '⚠️',
        'low': '💡'
    }
    return emojis.get(risk_level.lower(), '⚠️')

def get_risk_label(risk_level: str) -> str:
    """Return Korean label based on risk level."""
    labels = {
        'high': '높은 위험',
        'medium': '주의 필요',
        'low': '참고 사항'
    }
    return labels.get(risk_level.lower(), '주의 필요')

col_upload, col_spacer, col_result = st.columns([1, 0.1, 1.2])

with col_upload:
    st.markdown('<p class="step-header">1️⃣ 계약서 업로드</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="friendly-text">
    📤 계약서 사진을 업로드해주세요.<br>
    <small style="color: #888;">지원 형식: PNG, JPG, JPEG</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "계약서 이미지 선택",
        type=['png', 'jpg', 'jpeg'],
        help="계약서 사진을 드래그하거나 클릭해서 업로드하세요",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file
        image = Image.open(uploaded_file)
        st.image(image, caption="📋 업로드된 계약서", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <p class="reassurance-text">
        🔒 업로드된 이미지는 분석 후 저장되지 않습니다.
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔍 계약서 분석하기", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 꼼꼼히 분석하고 있어요..."):
                try:
                    from gemini_analyzer import analyze_contract_image
                    
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    mime_type = get_mime_type(uploaded_file.name)
                    
                    result = analyze_contract_image(image_bytes, mime_type)
                    
                    if result:
                        st.session_state.analysis_result = result
                        st.session_state.analysis_complete = True
                        st.session_state.analysis_error = None
                    else:
                        st.session_state.analysis_error = "분석 결과를 받지 못했습니다. 다시 시도해주세요."
                        
                except Exception as e:
                    st.session_state.analysis_error = str(e)
                    st.session_state.analysis_complete = False
                    
            st.rerun()

with col_result:
    st.markdown('<p class="step-header">2️⃣ 분석 결과</p>', unsafe_allow_html=True)
    
    if st.session_state.analysis_error:
        st.markdown(f"""
        <div class="danger-box">
            <p class="error-text">
            ❌ 분석 중 오류가 발생했습니다.<br>
            {st.session_state.analysis_error}<br><br>
            다시 시도해주세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 다시 시도하기", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.analysis_error = None
            st.session_state.analysis_result = None
            st.rerun()
    
    elif not st.session_state.analysis_complete:
        st.markdown("""
        <div class="info-box">
            <p class="friendly-text">
            👈 왼쪽에서 계약서를 업로드하고 분석 버튼을 눌러주세요.<br><br>
            <strong>분석 시 확인하는 항목:</strong><br>
            ✅ 근로시간 및 휴게시간<br>
            ✅ 임금 및 수당 조건<br>
            ✅ 해고 및 계약해지 조건<br>
            ✅ 기타 불리한 조항
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state.analysis_result
        
        st.markdown("""
        <div class="reassurance-text" style="margin-bottom: 1rem;">
        ✅ 분석이 완료되었습니다. 아래 내용을 확인해주세요.
        </div>
        """, unsafe_allow_html=True)
        
        if result.summary:
            st.markdown(f"""
            <div class="summary-box">
                <strong>📋 요약</strong><br>
                <span class="friendly-text">{result.summary}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if result.missing_clauses and len(result.missing_clauses) > 0:
            st.markdown("### 📝 누락된 조항")
            missing_items = "".join([f"<li>{clause}</li>" for clause in result.missing_clauses])
            st.markdown(f"""
            <div class="warning-box">
                <span class="friendly-text">
                다음 조항들이 계약서에 없거나 불명확해요:
                <ul style="margin-top: 0.5rem;">{missing_items}</ul>
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        if result.risk_clauses and len(result.risk_clauses) > 0:
            st.markdown("### 🚨 주의가 필요한 조항")
            
            for clause in result.risk_clauses:
                box_class = get_risk_box_class(clause.risk_level)
                emoji = get_risk_emoji(clause.risk_level)
                label = get_risk_label(clause.risk_level)
                
                st.markdown(f"""
                <div class="{box_class}">
                    <strong>{emoji} {label}: {clause.issue_summary}</strong><br>
                    <span class="friendly-text">
                    {clause.simple_explanation}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 📚 왜 문제가 될까요?")
            
            for clause in result.risk_clauses:
                if clause.legal_reference and clause.legal_article:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>{clause.legal_reference}</strong><br>
                        <span class="friendly-text">
                        "{clause.legal_article}"<br><br>
                        👉 <strong>쉽게 말하면:</strong> {clause.simple_explanation}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 🗣️ 이렇게 요청해보세요")
            
            for clause in result.risk_clauses:
                if clause.negotiation_script:
                    st.markdown(f"""
                    <div class="script-box">
                        <strong>{clause.issue_summary} 관련 요청:</strong><br>
                        <span class="friendly-text">
                        "{clause.negotiation_script}"
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="script-box">
                <strong>✨ 특별한 위험 조항이 발견되지 않았어요!</strong><br>
                <span class="friendly-text">
                계약서가 대체로 적정해 보입니다. 그래도 서명 전에 모든 내용을 꼼꼼히 읽어보세요.
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="reassurance-text">
        💪 걱정하지 마세요! 법에 근거한 정당한 요청이에요.<br>
        위의 문구를 그대로 사용하셔도 됩니다.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔄 다른 계약서 분석하기", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.uploaded_image = None
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
🛡️ 계약서 리스크 하이라이터 | 당신의 권리를 지켜드립니다<br>
<small>* 본 서비스는 법률 자문을 대체하지 않습니다. 중요한 결정은 전문가와 상담하세요.</small>
</div>
""", unsafe_allow_html=True)
