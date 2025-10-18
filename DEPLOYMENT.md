# Autogram 배포 가이드

이 문서는 Autogram을 Vercel(프론트엔드) + Railway(백엔드)로 배포하는 방법을 설명합니다.

## 📋 배포 아키텍처

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │────────▶│   Railway       │
│   (Frontend)    │   API   │   (Backend)     │
│   Next.js 14    │         │   FastAPI       │
└─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   Supabase      │
                            │   (PostgreSQL)  │
                            └─────────────────┘
```

## 🚀 1단계: Supabase 설정

### 1.1 Supabase 프로젝트 생성
1. https://supabase.com 접속
2. "New Project" 클릭
3. 프로젝트 정보 입력:
   - Name: `autogram`
   - Database Password: 강력한 비밀번호 생성 및 저장
   - Region: `Northeast Asia (Seoul)`
   - Pricing: `Free` (개발) 또는 `Pro` (프로덕션)

### 1.2 연결 문자열 복사
1. Settings → Database → Connection string
2. URI 탭에서 연결 문자열 복사
3. `postgresql://` → `postgresql+asyncpg://`로 변경
4. `[YOUR-PASSWORD]`를 실제 비밀번호로 교체
5. 특수문자가 있으면 URL 인코딩 (`!` → `%21`)

**최종 형식**:
```
postgresql+asyncpg://postgres.{ref}:YourPassword%21@db.{ref}.supabase.co:5432/postgres
```

## 🛠️ 2단계: Railway 배포 (백엔드)

### 2.1 Railway CLI 설치
```bash
npm install -g @railway/cli
```

### 2.2 Railway 로그인
```bash
railway login
```

### 2.3 프로젝트 초기화
```bash
cd /path/to/autogram-latest
railway init
```

프로젝트 이름 입력: `autogram-backend`

### 2.4 환경 변수 설정
Railway 대시보드에서 설정:

```bash
# Application
APP_NAME=Autogram
APP_VERSION=1.0.0
DEBUG=False

# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres.{ref}:password@db.{ref}.supabase.co:5432/postgres
DATABASE_ECHO=False

# Security
SECRET_KEY=<생성된-시크릿-키>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=<생성된-암호화-키>

# CORS (프론트엔드 도메인으로 업데이트)
CORS_ORIGINS=https://your-domain.vercel.app,https://www.your-domain.com

# Instagram
HELPER_SESSION_DIR=./sessions

# KakaoTalk
KAKAOTALK_FILE_PATH=batch/kakaotalk/KakaoTalk_latest.txt
KAKAOTALK_OPEN_CHAT_LINK=https://open.kakao.com/your-link
KAKAOTALK_QR_CODE_PATH=/images/kakao-qr.png
```

### 2.5 requirements.txt 확인
Railway는 자동으로 `requirements.txt`를 감지합니다.

### 2.6 Procfile 생성
```bash
# Procfile
web: uvicorn api.index:app --host 0.0.0.0 --port $PORT
```

### 2.7 배포
```bash
railway up
```

### 2.8 데이터베이스 마이그레이션
Railway 터미널에서 실행:
```bash
railway run alembic upgrade head
railway run python scripts/create_admin.py
```

### 2.9 도메인 설정
1. Railway 대시보드 → Settings → Domains
2. "Generate Domain" 클릭
3. 생성된 도메인 복사 (예: `autogram-backend.up.railway.app`)

## 🌐 3단계: Vercel 배포 (프론트엔드)

### 3.1 Vercel CLI 설치
```bash
npm install -g vercel
```

### 3.2 Vercel 로그인
```bash
vercel login
```

### 3.3 프로젝트 배포
```bash
cd /path/to/autogram-latest
vercel
```

프롬프트에 응답:
- Set up and deploy? `Y`
- Which scope? (계정 선택)
- Link to existing project? `N`
- Project name? `autogram`
- In which directory is your code located? `./`
- Override settings? `N`

### 3.4 환경 변수 설정
Vercel 대시보드에서 설정:

1. Project Settings → Environment Variables
2. 다음 변수 추가:

```bash
NEXT_PUBLIC_API_URL=https://autogram-backend.up.railway.app
```

### 3.5 프로덕션 배포
```bash
vercel --prod
```

### 3.6 도메인 확인
배포 완료 후 제공되는 도메인:
- `https://autogram.vercel.app` (또는 커스텀 도메인)

## ⚙️ 4단계: 배치 작업 설정 (Railway)

### 4.1 Cron Job 설정
Railway에는 기본 Cron Job이 없으므로 외부 서비스 사용:

#### 옵션 1: GitHub Actions (권장)
`.github/workflows/batch.yml` 생성:

```yaml
name: Run Batch Jobs

on:
  schedule:
    # 매주 월요일 오전 1시 (UTC) = 한국시간 오전 10시
    - cron: '0 1 * * 1'
  workflow_dispatch: # 수동 실행 가능

jobs:
  run-batch:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run batch jobs
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
        run: |
          python batch/run_batch.py
```

#### 옵션 2: EasyCron (무료/유료)
1. https://www.easycron.com 가입
2. New Cron Job 생성:
   - URL: `https://autogram-backend.up.railway.app/api/py/admin/batch/run`
   - Schedule: `0 10 * * 1` (매주 월요일 10am KST)

### 4.2 배치 엔드포인트 추가 (선택사항)
관리자 API에 배치 트리거 엔드포인트 추가:

`api/routers/admin_router.py`:
```python
@router.post("/batch/run")
async def trigger_batch(
    current_admin: dict = Depends(get_current_admin)
):
    """Manually trigger batch jobs"""
    import subprocess
    result = subprocess.run(
        ["python", "batch/run_batch.py"],
        capture_output=True,
        text=True
    )
    return {"stdout": result.stdout, "stderr": result.stderr}
```

## 🔒 5단계: 보안 설정

### 5.1 Railway CORS 업데이트
백엔드 `.env`의 `CORS_ORIGINS`를 Vercel 도메인으로 업데이트:
```bash
CORS_ORIGINS=https://autogram.vercel.app,https://www.your-domain.com
```

### 5.2 Supabase RLS (Row Level Security)
Supabase 대시보드에서 RLS 정책 설정 (선택사항)

### 5.3 Rate Limiting
프로덕션 환경에서는 API rate limiting 추가 고려

## 📊 6단계: 모니터링 설정

### 6.1 Railway 로그
```bash
railway logs
```

### 6.2 Vercel 로그
Vercel 대시보드 → Deployments → Logs

### 6.3 Supabase 모니터링
Supabase 대시보드 → Database → Logs

### 6.4 Sentry 통합 (선택사항)
```bash
pip install sentry-sdk[fastapi]
```

`api/index.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## 🧪 7단계: 배포 후 테스트

### 7.1 백엔드 헬스 체크
```bash
curl https://autogram-backend.up.railway.app/api/py/health
```

예상 결과:
```json
{
  "status": "healthy",
  "app": "Autogram",
  "version": "1.0.0"
}
```

### 7.2 프론트엔드 확인
1. https://autogram.vercel.app 접속
2. 홈페이지 로딩 확인
3. 관리자 로그인: `/admin/login`

### 7.3 API 문서 확인
https://autogram-backend.up.railway.app/api/py/docs

### 7.4 데이터베이스 확인
Supabase 대시보드 → Table Editor에서 테이블 확인

## 🔄 8단계: 업데이트 및 롤백

### 8.1 백엔드 업데이트
```bash
# 코드 변경 후
git add .
git commit -m "Update backend"
railway up
```

### 8.2 프론트엔드 업데이트
```bash
# 코드 변경 후
git add .
git commit -m "Update frontend"
vercel --prod
```

### 8.3 롤백
**Railway**:
- 대시보드 → Deployments → 이전 배포 선택 → Redeploy

**Vercel**:
- 대시보드 → Deployments → 이전 배포 선택 → Promote to Production

## 💰 9단계: 비용 관리

### Hobby Plan 예상 비용
- **Supabase Free**: $0/월
  - 500MB 데이터베이스
  - 무제한 API 요청
  - 2GB 파일 스토리지

- **Railway**: $5/월
  - 512MB RAM
  - 1GB 디스크
  - 100GB 아웃바운드 트래픽

- **Vercel Hobby**: $0/월
  - 100GB 대역폭
  - 무제한 배포
  - 자동 HTTPS

**총 예상 비용**: **$5/월**

### Pro Plan 업그레이드 시
- **Supabase Pro**: $25/월 (8GB DB)
- **Railway Pro**: $20/월 (8GB RAM)
- **Vercel Pro**: $20/월 (1TB 대역폭)

**총 Pro 비용**: **$65/월**

## 🛠️ 10단계: 문제 해결

### 문제: Railway 배포 실패
**해결**:
1. `requirements.txt` 확인
2. `Procfile` 확인
3. 로그 확인: `railway logs`

### 문제: Vercel 빌드 실패
**해결**:
1. `package.json` dependencies 확인
2. `next.config.js` 확인
3. Vercel 빌드 로그 확인

### 문제: CORS 오류
**해결**:
1. Railway 환경 변수 `CORS_ORIGINS` 확인
2. Vercel 도메인이 포함되어 있는지 확인
3. `https://` 프로토콜 사용 확인

### 문제: 데이터베이스 연결 실패
**해결**:
1. `DATABASE_URL` 형식 확인
2. Supabase 프로젝트 활성화 상태 확인
3. 비밀번호 URL 인코딩 확인

## 📚 11단계: 추가 리소스

### 공식 문서
- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- Supabase: https://supabase.com/docs
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs

### 커뮤니티
- Railway Discord: https://discord.gg/railway
- Vercel Discord: https://discord.gg/vercel
- Supabase Discord: https://discord.supabase.com

## ✅ 배포 체크리스트

### 배포 전
- [ ] Supabase 프로젝트 생성 완료
- [ ] 환경 변수 모두 설정 완료
- [ ] 로컬에서 테스트 완료
- [ ] 데이터베이스 마이그레이션 확인
- [ ] 관리자 계정 생성 확인

### Railway 배포
- [ ] Railway 프로젝트 생성
- [ ] 환경 변수 설정
- [ ] Procfile 생성
- [ ] 첫 배포 완료
- [ ] 헬스 체크 성공
- [ ] 도메인 설정 완료

### Vercel 배포
- [ ] Vercel 프로젝트 생성
- [ ] 환경 변수 설정
- [ ] 프로덕션 배포 완료
- [ ] 프론트엔드 로딩 확인
- [ ] API 통신 확인

### 배포 후
- [ ] 모든 페이지 작동 확인
- [ ] 관리자 로그인 테스트
- [ ] CRUD 작업 테스트
- [ ] 배치 작업 스케줄 설정
- [ ] 모니터링 설정 완료

---

**배포 완료!** 🎉

프로덕션 URL:
- 프론트엔드: https://autogram.vercel.app
- 백엔드: https://autogram-backend.up.railway.app
- API 문서: https://autogram-backend.up.railway.app/api/py/docs
