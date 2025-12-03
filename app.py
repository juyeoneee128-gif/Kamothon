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
    
    .document-container {
        background: #ffffff;
        border: 1px solid rgba(0, 151, 167, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        max-height: 600px;
        overflow-y: auto;
        font-size: 0.95rem;
        line-height: 1.8;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.03);
    }
    
    .risk-highlight {
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .risk-highlight:hover {
        filter: brightness(0.95);
        transform: scale(1.01);
    }
    .risk-highlight.active {
        outline: 2px solid #0097A7;
        outline-offset: 2px;
    }
    
    .detail-panel {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 151, 167, 0.1);
        border: 1px solid rgba(0, 151, 167, 0.15);
        position: sticky;
        top: 1rem;
    }
    
    .clause-card {
        background: linear-gradient(135deg, #F6FAFB 0%, #E8F6F7 100%);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #0097A7;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .clause-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 151, 167, 0.15);
    }
    .clause-card.high {
        border-left-color: #EF5350;
        background: linear-gradient(135deg, #FFF5F5 0%, #FFEBEE 100%);
    }
    .clause-card.medium {
        border-left-color: #FFA726;
        background: linear-gradient(135deg, #FFFBF5 0%, #FFF3E0 100%);
    }
    .clause-card.low {
        border-left-color: #66BB6A;
        background: linear-gradient(135deg, #F5FFF5 0%, #E8F5E9 100%);
    }
    
    .clause-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #333;
        margin-bottom: 0.3rem;
    }
    .clause-preview {
        font-size: 0.85rem;
        color: #666;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .detail-expanded {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 1rem;
        border: 2px solid #0097A7;
        box-shadow: 0 4px 16px rgba(0, 151, 167, 0.15);
    }
    .detail-section {
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0, 151, 167, 0.1);
    }
    .detail-section:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
    .detail-label {
        font-size: 0.8rem;
        color: #0097A7;
        font-weight: 600;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .detail-content {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.6;
    }
    
    .script-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 10px;
        padding: 1rem;
        font-size: 0.9rem;
        color: #2E7D32;
        border-left: 3px solid #66BB6A;
    }
    
    .legal-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 10px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #1565C0;
        border-left: 3px solid #42A5F5;
    }
    
    .missing-clause-item {
        display: flex;
        align-items: flex-start;
        padding: 0.5rem 0;
        gap: 0.5rem;
    }
    .missing-icon {
        color: #FFA726;
        font-size: 1rem;
    }
    
    .upload-zone {
        border: 2px dashed rgba(0, 151, 167, 0.4);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: rgba(0, 151, 167, 0.03);
        transition: all 0.3s ease;
    }
    .upload-zone:hover {
        border-color: #0097A7;
        background: rgba(0, 151, 167, 0.06);
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
    
    .summary-banner {
        background: linear-gradient(135deg, #0097A7 0%, #00BCD4 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .summary-text {
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .risk-legend {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        color: #666;
    }
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .legend-dot.high { background: #EF5350; }
    .legend-dot.medium { background: #FFA726; }
    .legend-dot.low { background: #66BB6A; }
    
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
    
    .no-risks-banner {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: #2E7D32;
    }
    
    .friendly-text {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .footer-mini {
        text-align: center;
        padding: 1rem;
        color: #888;
        font-size: 0.8rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div class="brand-title">🛡️ 계약서 리스크 하이라이터</div>
    <div class="brand-subtitle">AI가 계약서에서 위험한 부분을 직접 표시해드려요</div>
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
if 'selected_clause' not in st.session_state:
    st.session_state.selected_clause = None

def get_mime_type(filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    return mime_types.get(ext, 'image/jpeg')

if not st.session_state.analysis_complete:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="card">
            <div class="step-header">
                <span class="step-badge">1</span>
                계약서 사진을 올려주세요
            </div>
            <p class="friendly-text">
            📸 계약서 사진이나 스캔본을 올려주시면<br>
            AI가 텍스트를 추출하고 위험한 부분을 표시해드려요!
            </p>
        """, unsafe_allow_html=True)
        
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
            
            st.markdown("""
            <div class="privacy-badge">
                🔒 이미지는 분석 후 즉시 삭제됩니다
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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
                            if result.risk_clauses and len(result.risk_clauses) > 0:
                                st.session_state.selected_clause = result.risk_clauses[0].clause_id
                        else:
                            st.session_state.analysis_error = "분석 결과를 받지 못했어요. 다시 시도해주세요!"
                            
                    except Exception as e:
                        st.session_state.analysis_error = str(e)
                        st.session_state.analysis_complete = False
                        
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
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
            <div class="summary-text">✅ {result.summary}</div>
        </div>
        """, unsafe_allow_html=True)
    
    col_doc, col_detail = st.columns([1.4, 1])
    
    with col_doc:
        st.markdown("""
        <div class="card">
            <div class="step-header">
                <span class="step-badge">1</span>
                계약서 원문 (위험 부분 표시됨)
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="risk-legend">
            <div class="legend-item"><span class="legend-dot high"></span> 위험</div>
            <div class="legend-item"><span class="legend-dot medium"></span> 주의</div>
            <div class="legend-item"><span class="legend-dot low"></span> 참고</div>
        </div>
        """, unsafe_allow_html=True)
        
        from gemini_analyzer import highlight_text_with_risks
        
        if result.extracted_text:
            highlighted_html = highlight_text_with_risks(result.extracted_text, result.risk_clauses)
            
            st.markdown(f"""
            <div class="document-container">
                {highlighted_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("텍스트를 추출하지 못했습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_detail:
        st.markdown("""
        <div class="card">
            <div class="step-header">
                <span class="step-badge">2</span>
                상세 분석 결과
            </div>
        """, unsafe_allow_html=True)
        
        if result.missing_clauses and len(result.missing_clauses) > 0:
            st.markdown("**📋 누락된 조항**", unsafe_allow_html=True)
            for clause in result.missing_clauses:
                st.markdown(f"""
                <div class="missing-clause-item">
                    <span class="missing-icon">❓</span>
                    <span>{clause}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        if result.risk_clauses and len(result.risk_clauses) > 0:
            st.markdown("**🚨 위험 조항 목록** (왼쪽 문서의 번호와 매칭됩니다)", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            from gemini_analyzer import get_risk_emoji, get_risk_border_color
            
            for idx, clause in enumerate(result.risk_clauses, 1):
                risk_class = clause.risk_level.lower()
                is_selected = st.session_state.selected_clause == clause.clause_id
                border_color = get_risk_border_color(clause.risk_level)
                emoji = get_risk_emoji(clause.risk_level)
                
                col_btn = st.columns([1])[0]
                with col_btn:
                    if st.button(
                        f"[{idx}] {emoji} {clause.issue_summary}",
                        key=f"clause_{clause.clause_id}",
                        use_container_width=True
                    ):
                        st.session_state.selected_clause = clause.clause_id
                        st.rerun()
                
                if is_selected:
                    st.markdown(f"""
                    <div class="detail-expanded">
                        <div class="detail-section">
                            <div class="detail-label">📍 해당 문구</div>
                            <div class="detail-content" style="background: #FFF3E0; padding: 0.75rem; border-radius: 8px;">
                                "{clause.original_text}"
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">💡 쉬운 설명</div>
                            <div class="detail-content">{clause.simple_explanation}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">📚 법적 근거</div>
                            <div class="legal-box">
                                <strong>{clause.legal_reference}</strong><br>
                                {clause.legal_article}
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">💬 이렇게 말해보세요</div>
                            <div class="script-box">
                                "{clause.negotiation_script}"
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="no-risks-banner">
                <strong>🎉 좋은 소식이에요!</strong><br>
                특별히 위험해 보이는 조항이 발견되지 않았어요.<br>
                그래도 서명 전에 모든 내용을 읽어보세요!
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔄 다른 계약서 분석하기", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.uploaded_image = None
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None
            st.session_state.selected_clause = None
            st.rerun()

st.markdown("""
<div class="footer-mini">
    🛡️ 계약서 리스크 하이라이터 | 당신의 권리를 지켜드립니다<br>
    <small>* 본 서비스는 참고용이며, 법률 자문을 대체하지 않습니다.</small>
</div>
""", unsafe_allow_html=True)
