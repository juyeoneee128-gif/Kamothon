import streamlit as st
from PIL import Image
import io
import os

st.set_page_config(
    page_title="계약서 리스크 하이라이터",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main {
        background-color: #F6FAFB;
    }
    .stApp {
        background: linear-gradient(180deg, #F6FAFB 0%, #E8F6F7 100%);
    }
    
    .brand-header {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 151, 167, 0.2);
        position: relative;
        overflow: hidden;
    }
    .brand-header::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .brand-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .brand-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        font-weight: 400;
    }
    .brand-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 151, 167, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 188, 212, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 151, 167, 0.12);
    }
    
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        border-radius: 50%;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 151, 167, 0.3);
    }
    .step-header {
        display: flex;
        align-items: center;
        color: #0097A7;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
    }
    
    .friendly-text {
        color: #555;
        font-size: 1rem;
        line-height: 1.7;
    }
    .small-hint {
        color: #0097A7;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .reassurance-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, rgba(0, 151, 167, 0.1) 0%, rgba(0, 188, 212, 0.1) 100%);
        color: #0097A7;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.5rem 0;
        border: 1px solid rgba(0, 151, 167, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border-left: 4px solid #FFA726;
        padding: 1.25rem 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(255, 167, 38, 0.15);
    }
    .danger-box {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid #EF5350;
        padding: 1.25rem 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(239, 83, 80, 0.15);
    }
    .info-box {
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
        border-left: 4px solid #00BCD4;
        padding: 1.25rem 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0, 188, 212, 0.15);
    }
    .script-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #66BB6A;
        padding: 1.25rem 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(102, 187, 106, 0.15);
    }
    .success-box {
        background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);
        border-left: 4px solid #0097A7;
        padding: 1.25rem 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0, 151, 167, 0.15);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #ffffff 0%, #F6FAFB 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 2px solid rgba(0, 151, 167, 0.15);
        box-shadow: 0 4px 16px rgba(0, 151, 167, 0.08);
    }
    
    .flow-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(0, 151, 167, 0.05);
        border-radius: 12px;
    }
    .flow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #0097A7;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .flow-step-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    .flow-arrow {
        color: #00BCD4;
        font-size: 1.2rem;
    }
    
    .checklist-item {
        display: flex;
        align-items: flex-start;
        padding: 0.5rem 0;
        color: #555;
    }
    .checklist-icon {
        color: #0097A7;
        margin-right: 0.75rem;
        font-size: 1.1rem;
    }
    
    .section-title {
        color: #0097A7;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .privacy-note {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(0, 151, 167, 0.08);
        color: #0097A7;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    
    .footer-section {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 2rem;
        text-align: center;
        color: white;
    }
    .footer-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .footer-benefits {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    .footer-benefit {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
    }
    .footer-disclaimer {
        font-size: 0.8rem;
        opacity: 0.85;
        margin-top: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(0, 151, 167, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 151, 167, 0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stFileUploader {
        border: 2px dashed rgba(0, 151, 167, 0.3);
        border-radius: 16px;
        padding: 1rem;
        background: rgba(0, 151, 167, 0.02);
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #0097A7;
        background: rgba(0, 151, 167, 0.05);
    }
    
    .result-placeholder {
        text-align: center;
        padding: 3rem 2rem;
        color: #888;
    }
    .result-placeholder-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .error-text {
        color: #c62828;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div class="brand-title">🛡️ 계약서 리스크 하이라이터</div>
    <div class="brand-subtitle">복잡한 계약서도 걱정 마세요! AI가 위험한 부분을 찾아드려요</div>
    <div class="brand-badge">✨ 청년 근로자를 위한 든든한 계약서 분석 서비스</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="flow-indicator">
    <div class="flow-step">
        <span class="flow-step-icon">📤</span>
        <span>계약서 업로드</span>
    </div>
    <span class="flow-arrow">→</span>
    <div class="flow-step">
        <span class="flow-step-icon">🤖</span>
        <span>AI 분석</span>
    </div>
    <span class="flow-arrow">→</span>
    <div class="flow-step">
        <span class="flow-step-icon">💬</span>
        <span>협상 스크립트</span>
    </div>
</div>
""", unsafe_allow_html=True)

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analysis_error' not in st.session_state:
    st.session_state.analysis_error = None

def get_mime_type(filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    return mime_types.get(ext, 'image/jpeg')

def get_risk_box_class(risk_level: str) -> str:
    if risk_level.lower() == 'high':
        return 'danger-box'
    return 'warning-box'

def get_risk_emoji(risk_level: str) -> str:
    emojis = {
        'high': '🚨',
        'medium': '⚠️',
        'low': '💡'
    }
    return emojis.get(risk_level.lower(), '⚠️')

def get_risk_label(risk_level: str) -> str:
    labels = {
        'high': '꼭 확인하세요!',
        'medium': '조심하면 좋아요',
        'low': '참고해주세요'
    }
    return labels.get(risk_level.lower(), '조심하면 좋아요')

col_upload, col_spacer, col_result = st.columns([1, 0.08, 1.2])

with col_upload:
    st.markdown("""
    <div class="card">
        <div class="step-header">
            <span class="step-badge">1</span>
            계약서를 올려주세요
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p class="friendly-text" style="margin-bottom: 1rem;">
    📸 계약서 사진이나 스캔본을 올려주시면<br>
    AI가 꼼꼼하게 살펴볼게요!
    </p>
    <p class="small-hint">PNG, JPG, JPEG 형식 지원</p>
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
        st.image(image, caption="📋 업로드된 계약서 미리보기", use_container_width=True)
        
        st.markdown("""
        <div class="privacy-note">
            🔒 안심하세요! 이미지는 분석 후 바로 삭제됩니다
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔍 계약서 분석하기", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 꼼꼼히 읽고 있어요... 잠시만 기다려주세요! 📖"):
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
                        st.session_state.analysis_error = "분석 결과를 받지 못했어요. 다시 시도해주세요!"
                        
                except Exception as e:
                    st.session_state.analysis_error = str(e)
                    st.session_state.analysis_complete = False
                    
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_result:
    st.markdown("""
    <div class="card">
        <div class="step-header">
            <span class="step-badge">2</span>
            걱정마세요! 확인해볼게요
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.analysis_error:
        st.markdown(f"""
        <div class="danger-box">
            <p class="error-text">
            😥 앗, 문제가 생겼어요!<br>
            {st.session_state.analysis_error}<br><br>
            다시 한번 시도해볼까요?
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
        <div class="result-placeholder">
            <div class="result-placeholder-icon">📋</div>
            <p class="friendly-text">
            왼쪽에서 계약서를 올려주시면<br>
            여기에 분석 결과가 나타나요!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <p class="friendly-text">
            <strong>🔍 AI가 확인해드리는 것들:</strong>
            </p>
            <div class="checklist-item">
                <span class="checklist-icon">✓</span>
                <span>근로시간 및 휴게시간이 적절한지</span>
            </div>
            <div class="checklist-item">
                <span class="checklist-icon">✓</span>
                <span>임금과 수당이 법에 맞는지</span>
            </div>
            <div class="checklist-item">
                <span class="checklist-icon">✓</span>
                <span>불합리한 해고 조건은 없는지</span>
            </div>
            <div class="checklist-item">
                <span class="checklist-icon">✓</span>
                <span>꼭 있어야 할 조항이 빠지진 않았는지</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state.analysis_result
        
        st.markdown("""
        <div class="success-box">
            <strong>✅ 걱정마세요! 분석을 완료했어요</strong><br>
            <span class="friendly-text">아래 내용을 차근차근 확인해보세요 👇</span>
        </div>
        """, unsafe_allow_html=True)
        
        if result.summary:
            st.markdown(f"""
            <div class="summary-card">
                <strong style="color: #0097A7;">📝 한눈에 보기</strong><br><br>
                <span class="friendly-text">{result.summary}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if result.missing_clauses and len(result.missing_clauses) > 0:
            st.markdown("""
            <div class="section-title">
                📋 이런 내용이 없거나 불분명해요
            </div>
            """, unsafe_allow_html=True)
            
            missing_items = "".join([f'<div class="checklist-item"><span class="checklist-icon">❓</span><span>{clause}</span></div>' for clause in result.missing_clauses])
            st.markdown(f"""
            <div class="warning-box">
                <span class="friendly-text">
                계약서에서 다음 내용을 찾기 어려웠어요.<br>
                사장님께 확인해보시는 게 좋을 것 같아요!
                </span>
                <div style="margin-top: 1rem;">
                {missing_items}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if result.risk_clauses and len(result.risk_clauses) > 0:
            st.markdown("""
            <div class="section-title">
                🚨 조심하면 좋을 부분이에요
            </div>
            """, unsafe_allow_html=True)
            
            for clause in result.risk_clauses:
                box_class = get_risk_box_class(clause.risk_level)
                emoji = get_risk_emoji(clause.risk_level)
                label = get_risk_label(clause.risk_level)
                
                st.markdown(f"""
                <div class="{box_class}">
                    <strong>{emoji} {label}</strong><br>
                    <span class="friendly-text" style="font-weight: 500; color: #333;">
                    {clause.issue_summary}
                    </span><br><br>
                    <span class="friendly-text">
                    {clause.simple_explanation}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="section-title">
                📚 왜 조심해야 할까요?
            </div>
            """, unsafe_allow_html=True)
            
            for clause in result.risk_clauses:
                if clause.legal_reference and clause.legal_article:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong style="color: #0097A7;">{clause.legal_reference}</strong><br><br>
                        <span class="friendly-text" style="font-style: italic;">
                        "{clause.legal_article}"
                        </span><br><br>
                        <span class="friendly-text">
                        👉 <strong>쉽게 말하면:</strong> {clause.simple_explanation}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="step-header" style="margin-top: 2rem;">
                <span class="step-badge">3</span>
                이렇게 말씀해보세요
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="reassurance-badge">
                💪 법에 근거한 정당한 요청이에요. 당당하게 말씀하세요!
            </div>
            """, unsafe_allow_html=True)
            
            for clause in result.risk_clauses:
                if clause.negotiation_script:
                    st.markdown(f"""
                    <div class="script-box">
                        <strong style="color: #2E7D32;">📢 {clause.issue_summary} 관련</strong><br><br>
                        <span class="friendly-text" style="font-size: 1.05rem;">
                        "{clause.negotiation_script}"
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="script-box">
                <strong style="color: #2E7D32;">🎉 좋은 소식이에요!</strong><br><br>
                <span class="friendly-text">
                특별히 위험해 보이는 조항은 발견되지 않았어요.<br>
                그래도 서명하시기 전에 모든 내용을 꼼꼼히 읽어보시는 걸 추천해요!
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔄 다른 계약서 분석하기", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.uploaded_image = None
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer-section">
    <div class="footer-title">🛡️ 내 권리를 지켜주는 든든한 서비스</div>
    <div class="footer-benefits">
        <div class="footer-benefit">
            <span>✨</span>
            <span>무료로 이용 가능</span>
        </div>
        <div class="footer-benefit">
            <span>🔒</span>
            <span>개인정보 안전</span>
        </div>
        <div class="footer-benefit">
            <span>⚡</span>
            <span>30초 만에 분석</span>
        </div>
        <div class="footer-benefit">
            <span>📚</span>
            <span>근로기준법 기반</span>
        </div>
    </div>
    <div class="footer-disclaimer">
    * 본 서비스는 참고용이며, 법률 자문을 대체하지 않습니다. 중요한 결정은 전문가와 상담하세요.
    </div>
</div>
""", unsafe_allow_html=True)
