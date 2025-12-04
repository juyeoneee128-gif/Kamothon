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
    /* ===== MODERN PREMIUM DESIGN SYSTEM ===== */
    
    /* Typography: Pretendard with Noto Sans KR fallback */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    :root {
        /* Neutral Background Palette */
        --bg-page: #F9F9F9;
        --bg-card: #FFFFFF;
        --bg-subtle: #F4F4F5;
        
        /* Text Colors */
        --text-primary: #18181B;
        --text-secondary: #52525B;
        --text-tertiary: #71717A;
        --text-muted: #A1A1AA;
        
        /* Brand Accent - Yellow for highlights only */
        --accent-yellow: #FACC15;
        --accent-yellow-hover: #EAB308;
        
        /* Risk Tokens */
        --risk-high: #DC2626;
        --risk-high-bg: #FEF2F2;
        --risk-medium: #F59E0B;
        --risk-medium-bg: #FFFBEB;
        --risk-low: #10B981;
        --risk-low-bg: #ECFDF5;
        
        /* UI Tokens */
        --border-color: #E4E4E7;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.05);
        --shadow-lg: 0 12px 24px rgba(0,0,0,0.08);
        
        /* Animation */
        --transition: 200ms ease;
    }
    
    * {
        font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    .main, .stApp {
        background: var(--bg-page);
    }
    
    /* ===== HEADER - Fixed at Top ===== */
    .brand-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: var(--bg-card);
        border-bottom: 1px solid var(--border-color);
        padding: 0.875rem 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    
    /* Spacer for fixed header */
    .header-spacer {
        height: 80px;
    }
    
    /* Hide Streamlit header to avoid overlap */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--accent-yellow);
        border-radius: var(--radius-sm);
        margin-right: 0.75rem;
        font-size: 1rem;
        vertical-align: middle;
    }
    .brand-title {
        display: inline;
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        vertical-align: middle;
    }
    .brand-subtitle {
        color: var(--text-tertiary);
        font-size: 0.85rem;
        font-weight: 400;
        margin-top: 0.25rem;
    }
    .brand-title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
    }
    
    /* ===== CARDS ===== */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* ===== SUMMARY SECTION ===== */
    .summary-section {
        max-width: 720px;
        margin: 0 auto 1.5rem auto;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    .summary-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .summary-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--accent-yellow);
        border-radius: var(--radius-sm);
        font-size: 1rem;
    }
    .summary-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .summary-text {
        font-size: 1rem;
        color: var(--text-primary);
        font-weight: 500;
        line-height: 1.5;
    }
    
    /* ===== MISSING CLAUSES ===== */
    .missing-section {
        max-width: 720px;
        margin: 0 auto 1.5rem auto;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    .missing-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    .missing-icon {
        color: var(--risk-medium);
        font-size: 1.1rem;
    }
    .missing-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .missing-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .missing-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    .missing-item::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--risk-medium);
        border-radius: 50%;
        margin-top: 0.5rem;
        flex-shrink: 0;
    }
    
    /* ===== RISK LEGEND ===== */
    .risk-legend {
        max-width: 720px;
        margin: 0 auto 1rem auto;
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        padding: 0.75rem 0;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        color: var(--text-tertiary);
        font-weight: 500;
    }
    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .legend-dot.high { background: var(--risk-high); }
    .legend-dot.medium { background: var(--risk-medium); }
    .legend-dot.low { background: var(--risk-low); }
    
    /* ===== DOCUMENT VIEWER ===== */
    .document-viewer {
        max-width: 720px;
        margin: 0 auto 2rem auto;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 2rem;
        font-size: 0.9375rem;
        line-height: 1.9;
        white-space: pre-wrap;
        color: var(--text-primary);
        box-shadow: var(--shadow-sm);
    }
    
    /* ===== RISK HIGHLIGHTS ===== */
    .risk-highlight-wrapper {
        position: relative;
        display: inline;
    }
    
    .risk-mark {
        cursor: pointer;
        border-radius: 3px;
        transition: all var(--transition);
        padding: 1px 2px;
        margin: 0 -2px;
    }
    .risk-mark:hover {
        filter: brightness(0.95);
    }
    
    /* Tooltip - Clean minimal style */
    .risk-tooltip {
        position: absolute;
        left: calc(100% + 12px);
        top: -4px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 12px 14px;
        width: max-content;
        max-width: 240px;
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transform: translateX(-8px);
        transition: all var(--transition);
        pointer-events: none;
    }
    
    .risk-tooltip::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 12px;
        width: 10px;
        height: 10px;
        background: var(--bg-card);
        border-left: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        transform: rotate(45deg);
    }
    
    .risk-highlight-wrapper:hover .risk-tooltip {
        opacity: 1;
        visibility: visible;
        transform: translateX(0);
        pointer-events: auto;
    }
    
    .tooltip-header {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    
    .tooltip-content {
        display: block;
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    .tooltip-hint {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid var(--border-color);
    }
    
    /* ===== MODAL ===== */
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
        align-items: center;
        justify-content: center;
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
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        cursor: pointer;
    }
    
    .risk-mark-label {
        cursor: pointer;
    }
    
    .modal-content {
        position: relative;
        z-index: 10000;
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        max-width: 480px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: var(--shadow-lg);
        animation: modalFadeIn 0.25s ease;
    }
    
    @keyframes modalFadeIn {
        from {
            opacity: 0;
            transform: scale(0.96);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .modal-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        background: var(--bg-card);
        z-index: 1;
    }
    
    .modal-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .modal-close {
        background: var(--bg-subtle);
        border: none;
        font-size: 1.1rem;
        cursor: pointer;
        color: var(--text-tertiary);
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-sm);
        transition: all var(--transition);
    }
    
    .modal-close:hover {
        background: var(--border-color);
        color: var(--text-primary);
    }
    
    .modal-body {
        padding: 1.5rem;
    }
    
    .modal-section {
        margin-bottom: 1.25rem;
    }
    
    .modal-section:last-child {
        margin-bottom: 0;
    }
    
    .modal-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .modal-section-content {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* Neutral sections - no background color */
    .modal-original-text {
        color: var(--text-tertiary);
        font-style: italic;
        padding: 0;
    }
    
    .modal-legal-ref {
        color: var(--text-tertiary);
        font-size: 0.8rem;
        padding: 0;
    }
    
    /* Emphasized sections */
    .modal-issue-section {
        background: var(--accent-yellow);
        padding: 14px 16px;
        border-radius: var(--radius-md);
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .modal-script {
        background: var(--text-primary);
        color: white;
        padding: 16px 18px;
        border-radius: var(--radius-md);
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .modal-script-section .modal-section-title {
        color: var(--text-primary);
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    /* ===== RISK BADGES ===== */
    .risk-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .risk-badge.high {
        background: var(--risk-high-bg);
        color: var(--risk-high);
    }
    
    .risk-badge.medium {
        background: var(--risk-medium-bg);
        color: #B45309;
    }
    
    .risk-badge.low {
        background: var(--risk-low-bg);
        color: var(--risk-low);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--text-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all var(--transition) !important;
    }
    .stButton > button:hover {
        background: var(--text-secondary) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        max-width: 720px !important;
        margin: 0 auto !important;
    }
    [data-testid="stFileUploader"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploader"] section {
        background: var(--bg-card) !important;
        border: 1px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        min-height: 280px !important;
        padding: 2rem !important;
        transition: all var(--transition) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--text-tertiary) !important;
        background: var(--bg-subtle) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        min-height: 240px !important;
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
        width: 48px;
        height: 48px;
        background: var(--bg-subtle) url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 4L12 16M12 4L7 9M12 4L17 9' stroke='%2371717A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M4 17L4 18C4 19.1046 4.89543 20 6 20L18 20C19.1046 20 20 19.1046 20 18L20 17' stroke='%2371717A' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") center/24px no-repeat;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
    }
    
    [data-testid="stFileUploaderDropzone"]::after {
        content: '계약서 이미지를 업로드하세요';
        font-size: 0.9rem;
        color: var(--text-tertiary);
        font-weight: 500;
    }
    
    /* Hide file name after upload */
    [data-testid="stFileUploaderFile"] {
        display: none !important;
    }
    
    /* Cancel button styling */
    .stButton button[kind="secondary"] {
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-tertiary) !important;
        font-weight: 600 !important;
    }
    .stButton button[kind="secondary"]:hover {
        background: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    
    /* ===== MISC ===== */
    .uploaded-preview {
        position: relative;
        width: 200px;
        height: 200px;
        margin: 0;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 8px;
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .uploaded-preview img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 6px;
    }
    
    .preview-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.75rem;
        max-width: 720px;
        margin: 0 auto 1rem auto;
    }
    
    .preview-item {
        flex: 0 0 auto;
    }
    
    .uploaded-preview > div:first-child {
        position: absolute !important;
        top: 0.5rem;
        right: 0.5rem;
        z-index: 10;
        width: auto !important;
    }
    
    .uploaded-preview > div:first-child button {
        width: 28px !important;
        height: 28px !important;
        min-width: 28px !important;
        min-height: 28px !important;
        padding: 0 !important;
        background: rgba(0,0,0,0.6) !important;
        border: none !important;
        border-radius: 50% !important;
        color: white !important;
        font-size: 0.9rem !important;
        line-height: 1 !important;
    }
    
    .uploaded-preview > div:first-child button:hover {
        background: rgba(0,0,0,0.8) !important;
    }
    
    .uploaded-preview > div:first-child p {
        display: none !important;
    }
    
    .analyze-button-container {
        max-width: 720px;
        margin: 0 auto 1rem auto;
    }
    
    .analyze-button-container button {
        width: 100% !important;
    }
    
    .add-image-btn {
        width: 200px;
        height: 200px;
        background: var(--bg-card);
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: var(--text-muted);
        transition: all 0.2s ease;
    }
    
    .add-image-btn:hover {
        border-color: var(--accent);
        color: var(--text-secondary);
    }
    
    .add-image-btn span {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .hide-uploader [data-testid="stFileUploader"] {
        display: none !important;
    }
    
    .no-risks-banner {
        max-width: 720px;
        margin: 1rem auto;
        background: var(--risk-low-bg);
        border: 1px solid #A7F3D0;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        color: var(--risk-low);
        font-weight: 500;
    }
    
    .instruction-hint {
        max-width: 720px;
        margin: 0 auto 1.5rem auto;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        padding: 0.75rem 1rem;
    }
    
    .privacy-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 0.75rem;
    }
    
    .footer-mini {
        text-align: center;
        padding: 2rem 1rem;
        color: var(--text-muted);
        font-size: 0.75rem;
    }
    
    /* ===== MOBILE ===== */
    @media (max-width: 768px) {
        .brand-header {
            padding: 2rem 1rem;
        }
        .document-viewer,
        .summary-section,
        .missing-section {
            margin-left: 1rem;
            margin-right: 1rem;
            max-width: none;
        }
        .risk-tooltip {
            position: fixed;
            left: 1rem !important;
            right: 1rem !important;
            top: auto !important;
            bottom: 5rem;
            max-width: none;
        }
        .risk-tooltip::before {
            display: none;
        }
        .modal-content {
            max-width: 100%;
            margin: 1rem;
            max-height: calc(100vh - 2rem);
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div class="brand-title-row">
        <div class="brand-icon">📋</div>
        <div class="brand-title">계약서 리스크 하이라이터</div>
    </div>
    <div class="brand-subtitle">사회 초년생의 권리를 지키는 AI 기반 계약서 리스크 분석 서비스</div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

from gemini_analyzer import DEMO_MODE, get_demo_result

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analysis_error' not in st.session_state:
    st.session_state.analysis_error = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def get_mime_type(filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'pdf': 'application/pdf'
    }
    return mime_types.get(ext, 'image/jpeg')

def is_pdf(filename: str) -> bool:
    return filename.lower().endswith('.pdf')

def pdf_to_images(pdf_bytes: bytes) -> list[tuple[bytes, str]]:
    """Convert PDF pages to PNG images using PyMuPDF."""
    import fitz
    import io
    
    images = []
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        images.append((img_bytes, "image/png"))
    
    pdf_doc.close()
    return images

if DEMO_MODE:
    st.session_state.analysis_result = get_demo_result()
    st.session_state.analysis_complete = True

if not st.session_state.analysis_complete:
    uploaded_files = st.file_uploader(
        "계약서 이미지 또는 PDF 선택",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="계약서 사진 또는 PDF를 드래그하거나 클릭해서 업로드하세요 (여러 개 선택 가능)",
        label_visibility="collapsed",
        key=f"contract_uploader_{st.session_state.uploader_key}",
        accept_multiple_files=True
    )
    
    if not uploaded_files:
        st.markdown("""
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <span class="privacy-badge">🔒 이미지는 분석 후 즉시 삭제됩니다</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.session_state.uploaded_images = uploaded_files
        
        st.markdown('<div class="analyze-button-container">', unsafe_allow_html=True)
        analyze_clicked = st.button("🔍 계약서 분석하기", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if analyze_clicked:
            progress_messages = [
                ("📄 계약서 이미지를 읽고 있어요...", 0.1),
                ("🔍 텍스트를 추출하고 있어요...", 0.25),
                ("⚖️ 근로기준법과 비교 분석 중이에요...", 0.45),
                ("🚨 위험 조항을 찾고 있어요...", 0.65),
                ("💬 협상 스크립트를 생성하고 있어요...", 0.85),
                ("✨ 거의 다 됐어요!", 0.95),
            ]
            
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            import time
            import threading
            
            analysis_done = threading.Event()
            analysis_result = {"result": None, "error": None}
            
            def run_analysis():
                try:
                    from gemini_analyzer import analyze_contract_images
                    
                    image_data_list = []
                    for uf in uploaded_files:
                        uf.seek(0)
                        file_bytes = uf.read()
                        
                        if is_pdf(uf.name):
                            pdf_images = pdf_to_images(file_bytes)
                            image_data_list.extend(pdf_images)
                        else:
                            mime_type = get_mime_type(uf.name)
                            image_data_list.append((file_bytes, mime_type))
                    
                    result = analyze_contract_images(image_data_list)
                    analysis_result["result"] = result
                except Exception as e:
                    analysis_result["error"] = str(e)
                finally:
                    analysis_done.set()
            
            thread = threading.Thread(target=run_analysis)
            thread.start()
            
            msg_idx = 0
            while not analysis_done.is_set():
                if msg_idx < len(progress_messages):
                    msg, progress = progress_messages[msg_idx]
                    status_container.markdown(f'<p style="text-align:center; font-size:1rem; color: var(--text-secondary);">{msg}</p>', unsafe_allow_html=True)
                    progress_bar.progress(progress)
                    msg_idx += 1
                time.sleep(2.5)
            
            progress_bar.progress(1.0)
            status_container.markdown('<p style="text-align:center; font-size:1rem; color: var(--text-secondary);">✅ 분석 완료!</p>', unsafe_allow_html=True)
            time.sleep(0.5)
            
            status_container.empty()
            progress_bar.empty()
            
            if analysis_result["error"]:
                st.session_state.analysis_error = analysis_result["error"]
                st.session_state.analysis_complete = False
            elif analysis_result["result"]:
                st.session_state.analysis_result = analysis_result["result"]
                st.session_state.analysis_complete = True
                st.session_state.analysis_error = None
            else:
                st.session_state.analysis_error = "분석 결과를 받지 못했어요. 다시 시도해주세요!"
                    
            st.rerun()
        
        pdf_count = sum(1 for uf in uploaded_files if is_pdf(uf.name))
        img_count = len(uploaded_files) - pdf_count
        
        file_desc_parts = []
        if img_count > 0:
            file_desc_parts.append(f"이미지 {img_count}장")
        if pdf_count > 0:
            file_desc_parts.append(f"PDF {pdf_count}개")
        file_desc = ", ".join(file_desc_parts)
        
        import base64
        from io import BytesIO
        import fitz
        
        total_pages = 0
        for uf in uploaded_files:
            if is_pdf(uf.name):
                uf.seek(0)
                pdf_doc = fitz.open(stream=uf.read(), filetype="pdf")
                total_pages += len(pdf_doc)
                pdf_doc.close()
            else:
                total_pages += 1
        
        st.markdown(f'<p style="text-align:center; color: var(--text-secondary); margin-bottom: 0.75rem; font-size: 0.875rem;">📄 총 {total_pages}장 선택됨</p>', unsafe_allow_html=True)
        
        preview_html = '<div class="preview-grid">'
        for idx, uf in enumerate(uploaded_files):
            if is_pdf(uf.name):
                uf.seek(0)
                pdf_bytes = uf.read()
                pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc[page_num]
                    pix = page.get_pixmap(dpi=72)
                    img_bytes = pix.tobytes("png")
                    img = Image.open(BytesIO(img_bytes))
                    img.thumbnail((160, 160))
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    preview_html += f'<div class="preview-item"><div class="uploaded-preview"><img src="data:image/png;base64,{img_base64}" /></div></div>'
                pdf_doc.close()
            else:
                uf.seek(0)
                img = Image.open(uf)
                img.thumbnail((160, 160))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                preview_html += f'<div class="preview-item"><div class="uploaded-preview"><img src="data:image/png;base64,{img_base64}" /></div></div>'
        preview_html += '</div>'
        
        st.markdown(preview_html, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ 업로드 취소", key="cancel_all", use_container_width=True):
                st.session_state.uploader_key += 1
                st.session_state.uploaded_images = []
                st.rerun()
        
        if st.session_state.analysis_error:
            st.error(f"😥 {st.session_state.analysis_error}")
            if st.button("🔄 다시 시도하기"):
                st.session_state.analysis_error = None
                st.rerun()

else:
    result = st.session_state.analysis_result
    
    if result.summary:
        st.markdown(f"""
        <div class="summary-section">
            <div class="summary-header">
                <div class="summary-icon">📊</div>
                <div class="summary-title">분석 요약</div>
            </div>
            <div class="summary-text">{result.summary}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="risk-legend">
        <div class="legend-item"><span class="legend-dot high"></span> 위험</div>
        <div class="legend-item"><span class="legend-dot medium"></span> 주의</div>
        <div class="legend-item"><span class="legend-dot low"></span> 참고</div>
    </div>
    """, unsafe_allow_html=True)
    
    if result.risk_clauses and len(result.risk_clauses) > 0:
        st.markdown("""
        <div class="instruction-hint">
            색칠된 부분에 마우스를 올리거나 클릭하면 상세 정보를 확인할 수 있어요
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
    
    if result.missing_clauses and len(result.missing_clauses) > 0:
        missing_items = "".join([f'<div class="missing-item">{clause}</div>' for clause in result.missing_clauses])
        st.markdown(f"""
        <div class="missing-section">
            <div class="missing-header">
                <span class="missing-icon">⚠</span>
                <span class="missing-title">계약서에서 찾지 못한 중요 조항</span>
            </div>
            <div class="missing-list">
                {missing_items}
            </div>
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
