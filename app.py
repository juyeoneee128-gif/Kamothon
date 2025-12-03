import streamlit as st
from PIL import Image
import io

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
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧾 계약서 리스크 하이라이터")
st.markdown("##### 복잡한 계약서, 위험 조항은 우리가 찾아드립니다")
st.markdown("---")

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

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
                import time
                time.sleep(2)
                st.session_state.analysis_complete = True
                st.rerun()

with col_result:
    st.markdown('<p class="step-header">2️⃣ 분석 결과</p>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
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
        st.markdown("""
        <div class="reassurance-text" style="margin-bottom: 1rem;">
        ✅ 분석이 완료되었습니다. 아래 내용을 확인해주세요.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚨 주의가 필요한 조항")
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ 휴게시간 미명시</strong><br>
            <span class="friendly-text">
            계약서에 휴게시간에 대한 내용이 명확하게 적혀있지 않아요.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ 해고 예고 조항 누락</strong><br>
            <span class="friendly-text">
            해고 시 사전 통보 기간에 대한 내용이 없어요.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 📚 왜 문제가 될까요?")
        st.markdown("""
        <div class="info-box">
            <strong>근로기준법 제54조 (휴게)</strong><br>
            <span class="friendly-text">
            "사용자는 근로시간이 4시간인 경우에는 30분 이상, 8시간인 경우에는 1시간 이상의 휴게시간을 근로시간 도중에 주어야 한다."<br><br>
            👉 <strong>쉽게 말하면:</strong> 4시간 일하면 30분, 8시간 일하면 1시간 쉬는 시간이 법으로 보장되어 있어요!
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <strong>근로기준법 제26조 (해고의 예고)</strong><br>
            <span class="friendly-text">
            "사용자는 근로자를 해고하려면 적어도 30일 전에 예고를 하여야 한다."<br><br>
            👉 <strong>쉽게 말하면:</strong> 갑자기 해고하면 안 되고, 최소 한 달 전에 미리 알려줘야 해요!
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🗣️ 이렇게 요청해보세요")
        st.markdown("""
        <div class="script-box">
            <strong>휴게시간 관련 요청:</strong><br>
            <span class="friendly-text">
            "안녕하세요, 계약서를 검토하다 보니 휴게시간에 대한 내용이 명시되어 있지 않은 것 같아요. 
            근로기준법 제54조에 따라 휴게시간을 계약서에 추가해주실 수 있을까요?"
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="script-box">
            <strong>해고 예고 관련 요청:</strong><br>
            <span class="friendly-text">
            "계약서에 해고 예고 기간이 명시되어 있지 않은데요, 
            근로기준법 제26조에 따른 30일 전 해고 예고 조항을 추가해주시면 감사하겠습니다."
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
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
🛡️ 계약서 리스크 하이라이터 | 당신의 권리를 지켜드립니다<br>
<small>* 본 서비스는 법률 자문을 대체하지 않습니다. 중요한 결정은 전문가와 상담하세요.</small>
</div>
""", unsafe_allow_html=True)
