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
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 151, 167, 0.2);
    }
    .brand-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .brand-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
    }
    
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 151, 167, 0.08);
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 188, 212, 0.1);
    }
    
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        border-radius: 50%;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 0.6rem;
        box-shadow: 0 2px 8px rgba(0, 151, 167, 0.3);
    }
    .step-header {
        display: flex;
        align-items: center;
        color: #0097A7;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Document Viewer */
    .document-viewer {
        background: #ffffff;
        border: 1px solid rgba(0, 151, 167, 0.15);
        border-radius: 16px;
        padding: 2rem;
        font-size: 1rem;
        line-height: 2;
        white-space: pre-wrap;
        box-shadow: 0 4px 20px rgba(0, 151, 167, 0.08);
        max-width: 900px;
        margin: 0 auto 2rem auto;
    }
    
    /* Risk Mark (inline highlight) */
    .risk-mark {
        cursor: help;
        transition: all 0.2s ease;
    }
    .risk-mark:hover {
        filter: brightness(0.9);
        transform: scale(1.02);
    }
    
    /* Annotation Cards Container */
    .annotation-cards {
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Individual Annotation Card using details/summary */
    .annotation-card {
        background: #ffffff;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    
    .annotation-summary {
        padding: 1rem 1.25rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        transition: filter 0.2s;
        list-style: none;
    }
    .annotation-summary::-webkit-details-marker {
        display: none;
    }
    .annotation-summary:hover {
        filter: brightness(0.95);
    }
    
    .annotation-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        color: white;
        border-radius: 50%;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    
    .annotation-title {
        flex: 1;
        color: #333;
    }
    
    .annotation-detail {
        padding: 1.25rem;
        border-top: 1px solid rgba(0,0,0,0.08);
        background: #fafafa;
    }
    
    .annotation-quote {
        background: #FFF8E1;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #5D4037;
        border-left: 3px solid #FFA726;
    }
    
    .annotation-section {
        margin-bottom: 1rem;
    }
    .annotation-section:last-child {
        margin-bottom: 0;
    }
    
    .annotation-label {
        font-size: 0.85rem;
        color: #0097A7;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .annotation-content {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.6;
    }
    
    .annotation-legal {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #1565C0;
        border-left: 3px solid #42A5F5;
        line-height: 1.6;
    }
    
    .annotation-script {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.9rem;
        color: #2E7D32;
        border-left: 3px solid #66BB6A;
        line-height: 1.6;
    }
    
    /* Risk Legend */
    .risk-legend {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
        padding: 1rem;
        background: rgba(0, 151, 167, 0.05);
        border-radius: 12px;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: #555;
    }
    .legend-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }
    .legend-dot.high { background: #EF5350; }
    .legend-dot.medium { background: #FFA726; }
    .legend-dot.low { background: #66BB6A; }
    
    /* Missing Clauses Section */
    .missing-section {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #FFA726;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    .missing-title {
        font-weight: 600;
        color: #E65100;
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    .missing-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.4rem 0;
        color: #555;
        font-size: 0.9rem;
    }
    
    /* Summary Banner */
    .summary-banner {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Section Title */
    .section-title {
        color: #0097A7;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 2rem auto 1rem auto;
        max-width: 900px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 151, 167, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 151, 167, 0.4);
    }
    
    .privacy-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(0, 151, 167, 0.1);
        color: #0097A7;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    
    .friendly-text {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Style Streamlit file uploader as big dropzone */
    [data-testid="stFileUploader"] {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    [data-testid="stFileUploader"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploader"] section {
        background: #E8E8E8 !important;
        border: none !important;
        border-radius: 24px !important;
        min-height: 420px !important;
        padding: 2rem !important;
        transition: background 0.3s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        background: #DEDEDE !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        min-height: 380px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        display: none !important;
    }
    [data-testid="stFileUploader"] small {
        display: none !important;
    }
    [data-testid="stFileUploader"] button {
        display: none !important;
    }
    
    /* Hide upload visual since we're styling the uploader content directly */
    .upload-visual {
        display: none;
    }
    
    /* Custom content inside the dropzone */
    [data-testid="stFileUploaderDropzone"]::before {
        content: '';
        display: block;
        width: 56px;
        height: 56px;
        background: #333 url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 4L12 16M12 4L7 9M12 4L17 9' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M4 17L4 18C4 19.1046 4.89543 20 6 20L18 20C19.1046 20 20 19.1046 20 18L20 17' stroke='white' stroke-width='2.5' stroke-linecap='round'/%3E%3C/svg%3E") center/24px no-repeat;
        border-radius: 50%;
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stFileUploaderDropzone"]::after {
        content: '파일을 선택하거나 여기로 끌어다\A놓으세요.';
        white-space: pre-wrap;
        font-size: 1.15rem;
        color: #333;
        text-align: center;
        line-height: 1.7;
        font-weight: 400;
    }
    
    /* Uploaded image preview */
    .uploaded-preview {
        max-width: 800px;
        margin: 0 auto 1.5rem auto;
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .analyze-button-container {
        max-width: 400px;
        margin: 0 auto;
    }
    
    .no-risks-banner {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        color: #2E7D32;
        margin: 1rem auto;
        max-width: 900px;
    }
    
    .instruction-hint {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(0, 151, 167, 0.05);
        border-radius: 10px;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .footer-mini {
        text-align: center;
        padding: 1.5rem;
        color: #888;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div class="brand-title">🛡️ 계약서 리스크 하이라이터</div>
    <div class="brand-subtitle">위험한 조항을 바로 그 자리에서 확인하세요</div>
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

if not st.session_state.analysis_complete:
    uploaded_file = st.file_uploader(
        "계약서 이미지 선택",
        type=['png', 'jpg', 'jpeg'],
        help="계약서 사진을 드래그하거나 클릭해서 업로드하세요",
        label_visibility="collapsed",
        key="contract_uploader"
    )
    
    if uploaded_file is None:
        st.markdown("""
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <span class="privacy-badge">🔒 이미지는 분석 후 즉시 삭제됩니다</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.session_state.uploaded_image = uploaded_file
        
        st.markdown('<div class="uploaded-preview">', unsafe_allow_html=True)
        image = Image.open(uploaded_file)
        st.image(image, caption="📋 업로드된 계약서", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="analyze-button-container">', unsafe_allow_html=True)
        
        if st.button("🔍 계약서 분석하기", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 읽고 분석하고 있어요... 잠시만요! 📖"):
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_error:
            st.error(f"😥 {st.session_state.analysis_error}")
            if st.button("🔄 다시 시도하기"):
                st.session_state.analysis_error = None
                st.rerun()

else:
    result = st.session_state.analysis_result
    
    if result.summary:
        st.markdown(f"""
        <div class="summary-banner">
            ✅ {result.summary}
        </div>
        """, unsafe_allow_html=True)
    
    if result.missing_clauses and len(result.missing_clauses) > 0:
        missing_items = "".join([f'<div class="missing-item"><span>❓</span><span>{clause}</span></div>' for clause in result.missing_clauses])
        st.markdown(f"""
        <div class="missing-section">
            <div class="missing-title">📋 계약서에서 찾지 못한 중요 조항</div>
            {missing_items}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="risk-legend">
        <div class="legend-item"><span class="legend-dot high"></span> 🚨 위험 - 반드시 확인</div>
        <div class="legend-item"><span class="legend-dot medium"></span> ⚠️ 주의 - 확인 권장</div>
        <div class="legend-item"><span class="legend-dot low"></span> 💡 참고 - 알아두면 좋아요</div>
    </div>
    """, unsafe_allow_html=True)
    
    if result.risk_clauses and len(result.risk_clauses) > 0:
        st.markdown("""
        <div class="instruction-hint">
            💡 <strong>색칠된 부분에 마우스를 올리면</strong> 간단한 설명이 나타나요.<br>
            아래 카드를 <strong>클릭하면</strong> 상세 정보를 확인할 수 있어요!
        </div>
        """, unsafe_allow_html=True)
    
    from gemini_analyzer import highlight_text_with_risks, generate_annotation_cards
    
    if result.extracted_text:
        highlighted_html = highlight_text_with_risks(result.extracted_text, result.risk_clauses)
        
        st.markdown(f"""
        <div class="document-viewer">
            {highlighted_html}
        </div>
        """, unsafe_allow_html=True)
        
        if result.risk_clauses and len(result.risk_clauses) > 0:
            st.markdown("""
            <div class="section-title">
                📝 발견된 위험 조항 상세 분석
            </div>
            """, unsafe_allow_html=True)
            
            cards_html = generate_annotation_cards(result.risk_clauses)
            st.markdown(cards_html, unsafe_allow_html=True)
    else:
        st.info("텍스트를 추출하지 못했습니다.")
    
    if not result.risk_clauses or len(result.risk_clauses) == 0:
        st.markdown("""
        <div class="no-risks-banner">
            <strong>🎉 좋은 소식이에요!</strong><br>
            특별히 위험해 보이는 조항이 발견되지 않았어요.<br>
            그래도 서명 전에 모든 내용을 꼼꼼히 읽어보세요!
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🔄 다른 계약서 분석하기", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.uploaded_image = None
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None
            st.rerun()

st.markdown("""
<div class="footer-mini">
    🛡️ 계약서 리스크 하이라이터 | 당신의 권리를 지켜드립니다<br>
    <small>* 본 서비스는 참고용이며, 법률 자문을 대체하지 않습니다.</small>
</div>
""", unsafe_allow_html=True)
