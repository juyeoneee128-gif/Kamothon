# 계약서 리스크 하이라이터 (Contract Risk Highlighter)

## Overview
AI-based contract risk analysis service for young workers and part-time employees. Uses Vision LLM + RAG to identify risky clauses in employment contracts and provides communication scripts for negotiation.

**Current Status**: Initial setup complete, ready for feature development
**Last Updated**: December 3, 2024

## Tech Stack
- **Language**: Python 3.11
- **Frontend**: Streamlit (port 5000)
- **AI/ML**: 
  - Gemini 2.5 Pro (Vision LLM)
  - LangChain
  - ChromaDB (Vector Store for RAG)
- **Document Processing**: pypdf, unstructured

## Project Structure
```
.
├── app.py                 # Main Streamlit application
├── backend.py             # Backend logic for risk analysis
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration (port 5000, allow all hosts)
└── replit.md             # This file
```

## Key Features (Planned)
1. **Contract Image Analysis**: Upload and analyze contract images using Vision LLM
2. **Risk Detection**: Highlight non-standard or unfavorable clauses
3. **Legal Reference**: Provide legal basis from Korean Labor Standards Act
4. **Communication Scripts**: Generate negotiation scripts for users
5. **Secure Storage**: Handle personal information and document data securely

## Environment Setup

### Required Environment Variables
The following environment variables need to be configured:
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: API key for Google Gemini AI

### Streamlit Configuration
- Port: 5000 (configured in `.streamlit/config.toml`)
- Host: 0.0.0.0 (allows Replit proxy)
- CORS: Disabled for Replit environment
- XSRF Protection: Disabled for dev mode

## Development Workflow
1. The app runs on Streamlit dev server on port 5000
2. Access via Replit webview proxy
3. Hot reload enabled for development

## Recent Changes
- **2024-12-03**: Initial Replit environment setup
  - Installed Python 3.11 and all dependencies
  - Configured Streamlit for Replit (port 5000, allow all hosts)
  - Set up workflow for Streamlit app
  - Added comprehensive .gitignore for Python project

## Target Users
- Part-time/contract/intern workers
- Young professionals entering workforce
- Anyone who finds legal terms difficult to understand

## Team
- Core Developer: 클레버(A) - Vision + RAG Core, legal comparison logic
- Frontend Developer: 조앵(B) - Streamlit UI/UX, Replit deployment

## Next Steps
1. Set up Gemini API integration
2. Implement contract image upload and processing
3. Build RAG system with Korean Labor Standards Act data
4. Create risk detection algorithm
5. Design communication script generator
6. Build Streamlit UI/UX
