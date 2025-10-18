# Autogram - Instagram Comment Exchange Service

Instagram 링크를 공유하고 서로 댓글을 달아주는 품앗이 서비스입니다.

## 🎯 Features

- **품앗이 관리**: 사용자들이 Instagram 링크를 공유하고 댓글 작성 현황 추적
- **AI 자동 댓글**: AI가 자동으로 자연스러운 댓글 생성 및 작성  
- **언팔 검색기**: 언팔로워 확인 기능
- **관리자 패널**: 사용자 및 헬퍼 계정 관리
- **주간 리포트**: 매주 참여 현황 확인

## 📦 Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy (async) + Python 3.11+
- **Instagram**: instaloader (read) + instagrapi (write)
- **Database**: PostgreSQL or MySQL
- **Deployment**: Vercel (frontend) + Railway (backend + batch)

## 🚀 Quick Start

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for complete implementation guide.

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/generate_keys.py
cp .env.example .env
# Edit .env with generated keys
```

### 2. Database Migration
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
python scripts/create_admin.py
```

### 3. Run Application
```bash
# Backend
uvicorn api.index:app --reload --port 8000

# Frontend  
npm install
npm run dev
```

## 📁 Project Structure

```
autogram-latest/
├── api/             # FastAPI backend
├── app/             # Next.js frontend
├── batch/           # Batch jobs
├── core/            # Shared code (models, schemas, security)
├── scripts/         # Utility scripts
├── alembic/         # Database migrations
└── .env.example     # Environment template
```

## 📚 Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Complete implementation status and guide
- **[.env.example](.env.example)** - Environment configuration template
- **API Docs**: http://localhost:8000/api/py/docs (after starting backend)

## 🚢 Deployment

**Recommended**: Hybrid deployment
- **Vercel** (Free): Next.js frontend
- **Railway** ($5/mo): FastAPI backend + batch jobs
- **PlanetScale** (Free): PostgreSQL database

Total cost: **$5/month**

## 📞 Support

For implementation questions, see PROJECT_STATUS.md or open an issue.

---

**Made with ❤️ for the Instagram community**
