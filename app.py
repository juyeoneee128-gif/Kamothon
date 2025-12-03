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
    /* ===== KAKAO-INSPIRED DESIGN SYSTEM ===== */
    
    /* Typography: Pretendard with Noto Sans KR fallback */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    :root {
        /* Kakao Brand Colors */
        --kakao-yellow: #FEE500;
        --kakao-brown: #3C1E1E;
        
        /* Background */
        --bg-primary: #F7F7F7;
        --bg-white: #FFFFFF;
        
        /* Text Neutrals */
        --text-primary: #1A1A1A;
        --text-secondary: #3C3C3C;
        --text-tertiary: #707070;
        --text-muted: #999999;
        
        /* Risk Color Tokens */
        --color-danger: #E53935;
        --color-danger-bg: #FFEBEE;
        --color-warning: #FFB300;
        --color-warning-bg: #FFF8E1;
        --color-safe: #00A86B;
        --color-safe-bg: #E8F5E9;
        
        /* UI */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
        
        /* Animation */
        --transition-fast: 150ms ease;
        --transition-normal: 250ms ease;
    }
    
    * {
        font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: var(--bg-primary);
    }
    .stApp {
        background: var(--bg-primary);
    }
    
    /* Brand Header - Kakao Yellow */
    .brand-header {
        background: var(--kakao-yellow);
        padding: 1.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
    }
    .brand-title {
        color: var(--kakao-brown);
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .brand-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Document Viewer */
    .document-viewer {
        background: var(--bg-white);
        border: none;
        border-radius: var(--radius-lg);
        padding: 2rem;
        font-size: 1rem;
        line-height: 2;
        white-space: pre-wrap;
        box-shadow: var(--shadow-md);
        max-width: 900px;
        margin: 0 auto 2rem auto;
    }
    
    /* Risk Legend - Pill style */
    .risk-legend {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
        padding: 1rem 1.5rem;
        background: var(--bg-white);
        border-radius: var(--radius-xl);
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: var(--shadow-sm);
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary);
        padding: 0.5rem 1rem;
        border-radius: var(--radius-xl);
        background: var(--bg-primary);
    }
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .legend-dot.high { background: var(--color-danger); }
    .legend-dot.medium { background: var(--color-warning); }
    .legend-dot.low { background: var(--color-safe); }
    
    /* Missing Clauses Section */
    .missing-section {
        background: var(--color-warning-bg);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--color-warning);
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: var(--shadow-sm);
    }
    .missing-title {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    .missing-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.4rem 0;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Summary Banner - Kakao Yellow accent */
    .summary-banner {
        background: var(--kakao-yellow);
        color: var(--kakao-brown);
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius-lg);
        margin-bottom: 1.5rem;
        text-align: center;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        font-weight: 600;
        box-shadow: var(--shadow-md);
    }
    
    /* Buttons - Kakao Yellow CTA */
    .stButton > button {
        background: var(--kakao-yellow) !important;
        color: var(--kakao-brown) !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.875rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--transition-fast) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        filter: brightness(0.95) !important;
    }
    
    .privacy-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--bg-white);
        color: var(--text-tertiary);
        padding: 0.5rem 1rem;
        border-radius: var(--radius-xl);
        font-size: 0.85rem;
        margin-top: 1rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* File Uploader - Big Dropzone */
    [data-testid="stFileUploader"] {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    [data-testid="stFileUploader"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploader"] section {
        background: var(--bg-white) !important;
        border: 2px dashed #E0E0E0 !important;
        border-radius: var(--radius-xl) !important;
        min-height: 380px !important;
        padding: 2rem !important;
        transition: all var(--transition-fast) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--kakao-yellow) !important;
        background: #FFFEF5 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        min-height: 340px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzone"] > div:first-child,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] button {
        display: none !important;
    }
    
    [data-testid="stFileUploaderDropzone"]::before {
        content: '';
        display: block;
        width: 64px;
        height: 64px;
        background: var(--kakao-yellow) url("data:image/svg+xml,%3Csvg width='28' height='28' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 4L12 16M12 4L7 9M12 4L17 9' stroke='%233C1E1E' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M4 17L4 18C4 19.1046 4.89543 20 6 20L18 20C19.1046 20 20 19.1046 20 18L20 17' stroke='%233C1E1E' stroke-width='2.5' stroke-linecap='round'/%3E%3C/svg%3E") center/28px no-repeat;
        border-radius: var(--radius-lg);
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stFileUploaderDropzone"]::after {
        content: '계약서 이미지를 업로드하세요';
        font-size: 1.1rem;
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Uploaded image preview */
    .uploaded-preview {
        max-width: 800px;
        margin: 0 auto 1.5rem auto;
        background: var(--bg-white);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    
    .analyze-button-container {
        max-width: 400px;
        margin: 0 auto;
    }
    
    .no-risks-banner {
        background: var(--color-safe-bg);
        border-radius: var(--radius-lg);
        padding: 2rem;
        text-align: center;
        color: var(--color-safe);
        margin: 1rem auto;
        max-width: 900px;
        font-weight: 600;
        box-shadow: var(--shadow-sm);
    }
    
    .instruction-hint {
        text-align: center;
        color: var(--text-tertiary);
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        padding: 1rem 1.5rem;
        background: var(--bg-white);
        border-radius: var(--radius-lg);
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: var(--shadow-sm);
    }
    
    .footer-mini {
        text-align: center;
        padding: 1.5rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 2rem;
    }
    
    /* ===== TOOLTIP - Sticky Note Style ===== */
    .risk-highlight-wrapper {
        position: relative;
        display: inline-block;
    }
    
    .risk-mark {
        cursor: pointer;
        transition: all var(--transition-fast);
        border-radius: 4px;
    }
    
    .risk-mark:hover {
        filter: brightness(0.92);
        transform: scale(1.02);
    }
    
    .risk-tooltip {
        position: absolute;
        left: calc(100% + 8px);
        top: -8px;
        background: #FFFDE7;
        border: none;
        border-radius: var(--radius-md);
        padding: 14px 16px;
        width: max-content;
        max-width: 260px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05);
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transform: scale(0.95) translateX(-4px);
        transition: all var(--transition-fast);
        pointer-events: none;
        display: block;
    }
    
    .risk-tooltip::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 14px;
        width: 12px;
        height: 12px;
        background: #FFFDE7;
        transform: rotate(45deg);
        box-shadow: -2px 2px 4px rgba(0,0,0,0.05);
    }
    
    .risk-highlight-wrapper:hover .risk-tooltip {
        opacity: 1;
        visibility: visible;
        transform: scale(1) translateX(0);
        pointer-events: auto;
    }
    
    .tooltip-header {
        display: block;
        font-weight: 700;
        font-size: 0.9rem;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .tooltip-content {
        display: block;
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    .tooltip-hint {
        display: block;
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px dashed #E0E0E0;
    }
    
    /* ===== MODAL - Slide Up Animation ===== */
    .modal-toggle {
        display: none;
    }
    
    .css-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        display: none;
        align-items: flex-end;
        justify-content: center;
        padding-bottom: 0;
    }
    
    .modal-toggle:checked + .css-modal-overlay {
        display: flex;
    }
    
    .modal-overlay-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(4px);
        cursor: pointer;
    }
    
    .risk-mark-label {
        cursor: pointer;
    }
    
    /* Modal content - Bottom slide panel */
    .modal-content {
        position: relative;
        z-index: 10000;
        background: var(--bg-white);
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        max-width: 600px;
        width: 100%;
        max-height: 85vh;
        overflow-y: auto;
        box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.2);
        animation: modalSlideUp 0.3s ease;
    }
    
    @keyframes modalSlideUp {
        from {
            opacity: 0;
            transform: translateY(100%);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .modal-header {
        padding: 20px 24px;
        border-bottom: 1px solid #F0F0F0;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        position: sticky;
        top: 0;
        background: var(--bg-white);
        z-index: 1;
    }
    
    .modal-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .modal-close {
        background: var(--bg-primary);
        border: none;
        font-size: 1.25rem;
        cursor: pointer;
        color: var(--text-tertiary);
        padding: 8px 12px;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
        flex-shrink: 0;
    }
    
    .modal-close:hover {
        background: #E8E8E8;
        color: var(--text-primary);
    }
    
    .modal-body {
        padding: 24px;
    }
    
    .modal-section {
        margin-bottom: 20px;
    }
    
    .modal-section:last-child {
        margin-bottom: 0;
    }
    
    .modal-section-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--text-tertiary);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .modal-section-content {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.7;
        background: var(--bg-primary);
        padding: 14px 16px;
        border-radius: var(--radius-md);
    }
    
    .modal-original-text {
        background: var(--color-warning-bg);
        border-left: 4px solid var(--color-warning);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        font-weight: 500;
    }
    
    .modal-legal-ref {
        background: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    
    .modal-script {
        background: var(--color-safe-bg);
        border-left: 4px solid var(--color-safe);
    }
    
    /* Risk Badges - Pill shape */
    .risk-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 14px;
        border-radius: var(--radius-xl);
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    .risk-badge.high {
        background: var(--color-danger-bg);
        color: var(--color-danger);
    }
    
    .risk-badge.medium {
        background: var(--color-warning-bg);
        color: #BF8C00;
    }
    
    .risk-badge.low {
        background: var(--color-safe-bg);
        color: var(--color-safe);
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .risk-tooltip {
            position: fixed;
            left: 16px !important;
            right: 16px !important;
            top: auto !important;
            bottom: 80px;
            max-width: none;
            width: auto;
        }
        .risk-tooltip::before {
            display: none;
        }
        .modal-content {
            max-width: 100%;
            border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div class="brand-title">🛡️ 계약서 리스크 하이라이터</div>
    <div class="brand-subtitle">위험한 조항을 바로 그 자리에서 확인하세요</div>
</div>
""", unsafe_allow_html=True)

from gemini_analyzer import DEMO_MODE, get_demo_result

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

if DEMO_MODE:
    st.session_state.analysis_result = get_demo_result()
    st.session_state.analysis_complete = True

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
            💡 <strong>색칠된 부분에 마우스를 올리면</strong> 오른쪽에 메모가 나타나요.<br>
            <strong>클릭하면</strong> 상세 정보 팝업이 열립니다!
        </div>
        """, unsafe_allow_html=True)
    
    from gemini_analyzer import highlight_text_with_risks, generate_css_modals_html
    
    if result.extracted_text:
        highlighted_html, modal_data_list = highlight_text_with_risks(result.extracted_text, result.risk_clauses)
        
        if modal_data_list:
            modals_html = generate_css_modals_html(modal_data_list)
            st.markdown(modals_html, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="document-viewer">
            {highlighted_html}
        </div>
        """, unsafe_allow_html=True)
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
