# 계약서 위험 탐지기 (Contract Risk Highlighter)

## Overview
AI-based contract risk analysis service for young workers and part-time employees. Uses Gemini Vision LLM to identify risky clauses in employment contracts and provides communication scripts for negotiation.

**Current Status**: Core features implemented - Gemini Vision integration complete
**Last Updated**: December 3, 2024

## Project Context

### Mission
Protect young workers from unfair contracts before signing by:
- Detecting risky/missing clauses in contracts
- Providing legal references from 근로기준법 (Korean Labor Standards Act)
- Generating ready-to-use negotiation scripts

### Target Users
- Part-time/contract/intern workers
- Young professionals entering the workforce
- Anyone unfamiliar with legal terminology

### Pain Points Addressed
- Hard to understand legal jargon in contracts
- Afraid to ask questions right before signing
- Signing without awareness of dangers
- Result: unfair treatment, financial damage

### UX Principles
- Friendly, non-intimidating tone
- Simple Korean language (no legal jargon)
- Reassuring messaging ("걱정하지 마세요")
- Single-screen flow for minimal friction
- Color-coded risk levels (orange for warning, red for danger)

## Tech Stack
- **Language**: Python 3.11
- **Frontend**: Streamlit (port 5000)
- **AI/ML**: 
  - Gemini 2.5 Pro (Vision LLM) - for contract image analysis
  - google-genai SDK
- **Document Processing**: PIL for image handling

## Project Structure
```
.
├── app.py                 # Main Streamlit application with UI
├── gemini_analyzer.py     # Gemini Vision contract analysis module
├── backend.py             # Backend logic (for future RAG integration)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration (port 5000)
└── replit.md             # This file
```

## Key Features (Implemented)
1. **Contract Image Upload**: Drag-and-drop image upload with preview
2. **Vision + LLM Analysis**: Gemini 2.5 Pro analyzes contract images
3. **Risk Detection**: Color-coded risk levels (high/medium/low)
4. **Legal References**: 근로기준법 citations in simple Korean
5. **Negotiation Scripts**: Ready-to-use phrases for each risk
6. **Privacy-First**: No image storage after analysis

## Environment Setup

### Required Secrets
- `GEMINI_API_KEY`: Google AI API key for Gemini

### Streamlit Configuration
- Port: 5000 (configured in `.streamlit/config.toml`)
- Host: 0.0.0.0 (allows Replit proxy)
- CORS: Disabled for Replit environment

## Main Flow
1. User uploads contract image (PNG/JPG/JPEG)
2. Click "계약서 분석하기" button
3. Gemini Vision analyzes the contract
4. Results displayed with:
   - Summary of analysis
   - List of missing clauses
   - Risk clauses with color-coded warnings
   - Legal references with simple explanations
   - Ready-to-use negotiation scripts

## Analysis Response Structure
```python
ContractAnalysisResult:
  - risk_clauses: List[RiskClause]
    - clause_text: str
    - risk_level: "high" | "medium" | "low"
    - issue_summary: str
    - legal_reference: str (e.g., "근로기준법 제54조")
    - legal_article: str (full legal text)
    - simple_explanation: str
    - negotiation_script: str
  - overall_risk_level: str
  - summary: str
  - missing_clauses: List[str]
```

## Design System (Modern Premium)
- **Style**: Clean, minimalist, professional
- **Background**: #F9F9F9 (soft neutral)
- **Cards**: White (#FFFFFF) with subtle border (#E4E4E7) and soft shadow
- **Text Neutrals**: #18181B / #52525B / #71717A / #A1A1AA
- **Accent**: #FACC15 (yellow) - icons and highlights only
- **Risk Tokens**:
  - High: #DC2626 (bg: #FEF2F2)
  - Medium: #F59E0B (bg: #FFFBEB)
  - Low: #10B981 (bg: #ECFDF5)
- **Typography**: Pretendard (Noto Sans KR fallback), clear hierarchy
- **Radius**: 6-12px (sleek, subtle corners)
- **Shadows**: Minimal (0 1px 2px to 0 4px 12px)
- **Layout**: Centered content (max-width 720px), wide margins

## Recent Changes
- **2024-12-04**:
  - **Chat Feature Removed**: Reverted chat functionality per user request
  - **Analysis UX Improvement**: During analysis, only progress bar shown (file preview and buttons hidden)
  - **Preview Grid UX Update**:
    - "이미지 추가" button now appears as last item in preview grid
    - X delete button overlays each preview item
    - 3 items per row layout
  - **Navigation Bar on Results Page**:
    - Back button (뒤로가기) - keeps uploaded files
    - Home button (홈으로) - resets everything

- **2024-12-03**: 
  - **Modern Premium Design Overhaul**:
    - Clean, minimalist, professional style
    - Soft neutral background (#F9F9F9)
    - Card-based layout with subtle borders and shadows
    - Yellow accent only for icons and highlights
    - Sleek border radius (6-12px)
    - Clear typography hierarchy
    - Centered content (max-width 720px)
    - Compact risk legend and missing clauses display
  - **Tooltip + Modal UX Enhancement**:
    - Hover tooltip: sticky-note style box appears to the right
    - Shows emoji, risk label, issue summary, and "click for details" hint
    - Click-to-modal: Pure CSS modal (checkbox hack, no JavaScript)
    - Modal displays: original text, explanation, legal reference, negotiation script
    - Click overlay background or X button to close modal
  - **Demo Mode**: DEMO_MODE flag for testing without API calls
    - Shows sample contract with 5 risk clauses and 3 missing clauses
    - Set DEMO_MODE = False in gemini_analyzer.py to enable real API
  - **Major UX Improvement**: Inline annotation experience
    - Single-column document view (removed separate right panel)
    - Color-coded `<mark>` highlights with native browser tooltips on hover
    - Security: All text properly HTML-escaped to prevent XSS
  - Added OCR: Gemini extracts full contract text from image
  - Color-coded inline highlights using design system tokens
  - Friendly Korean copywriting for young workers
  - Implemented Gemini Vision contract analysis
  - Created gemini_analyzer.py with structured response
  - Added privacy messaging

## Future Improvements
1. RAG integration with 근로기준법 database
2. PDF contract support
3. Multi-page contract analysis
4. Save/export analysis results
5. Industry-specific contract templates

## Team
- Core Developer: 클레버(A) - Vision + RAG Core, legal comparison logic
- Frontend Developer: 조앵(B) - Streamlit UI/UX, Replit deployment
