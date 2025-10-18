# Autogram 배포 체크리스트

## ✅ 배포 전 준비

### 1. Supabase 설정
- [ ] Supabase 프로젝트 생성 완료
- [ ] DATABASE_URL 복사 및 확인
  - 형식: `postgresql+asyncpg://postgres.{ref}:password@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres`
  - 비밀번호 URL 인코딩 확인 (`!` → `%21`)
- [ ] Supabase 대시보드 접속 가능 확인

### 2. 환경 변수 준비
**필수 환경 변수 목록**:

```bash
# Application
APP_NAME=Autogram
APP_VERSION=1.0.0
DEBUG=False  # 프로덕션에서는 False

# Database
DATABASE_URL=postgresql+asyncpg://postgres.{ref}:password@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres
DATABASE_ECHO=False

# Security
SECRET_KEY=<생성된-시크릿-키>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=<생성된-암호화-키>

# CORS (배포 후 업데이트 필요)
CORS_ORIGINS=https://your-domain.vercel.app

# Instagram
HELPER_SESSION_DIR=./sessions

# KakaoTalk
KAKAOTALK_FILE_PATH=batch/kakaotalk/KakaoTalk_latest.txt
KAKAOTALK_OPEN_CHAT_LINK=https://open.kakao.com/your-link
KAKAOTALK_QR_CODE_PATH=/images/kakao-qr.png
```

### 3. 로컬 테스트
- [ ] `python scripts/test_supabase.py` 실행 성공
- [ ] `alembic upgrade head` 실행 성공
- [ ] `python scripts/create_admin.py` 실행 성공
- [ ] `python scripts/test_batch_jobs.py` 실행 성공
- [ ] `uvicorn api.index:app --reload` 실행 성공
- [ ] `http://localhost:8000/api/py/docs` 접속 확인
- [ ] `npm run dev` 실행 성공
- [ ] `http://localhost:3000` 접속 확인

---

## 🚂 Railway 배포 (백엔드)

### 4. Railway 프로젝트 생성
- [ ] Railway CLI 설치: `npm install -g @railway/cli`
- [ ] Railway 로그인: `railway login`
- [ ] 프로젝트 초기화: `railway init`
- [ ] 프로젝트 이름: `autogram-backend`

### 5. Railway 환경 변수 설정
Railway 대시보드 → Variables에서 설정:

- [ ] `APP_NAME=Autogram`
- [ ] `APP_VERSION=1.0.0`
- [ ] `DEBUG=False`
- [ ] `DATABASE_URL` (Supabase URL)
- [ ] `DATABASE_ECHO=False`
- [ ] `SECRET_KEY` (시크릿 키)
- [ ] `ALGORITHM=HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- [ ] `ENCRYPTION_KEY` (암호화 키)
- [ ] `CORS_ORIGINS` (Vercel 도메인으로 나중에 업데이트)
- [ ] `HELPER_SESSION_DIR=./sessions`
- [ ] `KAKAOTALK_FILE_PATH=batch/kakaotalk/KakaoTalk_latest.txt`
- [ ] `KAKAOTALK_OPEN_CHAT_LINK` (오픈채팅 링크)
- [ ] `KAKAOTALK_QR_CODE_PATH=/images/kakao-qr.png`

### 6. Railway 첫 배포
- [ ] `Procfile` 생성 확인
- [ ] `requirements.txt` 확인
- [ ] `railway up` 실행
- [ ] 배포 성공 확인

### 7. Railway 데이터베이스 마이그레이션
Railway 대시보드에서 실행:
- [ ] `railway run alembic upgrade head`
- [ ] `railway run python scripts/create_admin.py`
- [ ] 관리자 계정 정보 저장 (username: admin)

### 8. Railway 헬스 체크
- [ ] Railway 도메인 생성 (Settings → Domains → Generate Domain)
- [ ] 도메인 복사 및 저장: `_______________.up.railway.app`
- [ ] `curl https://{domain}/api/py/health` 테스트
- [ ] 응답 확인: `{"status": "healthy", "app": "Autogram", "version": "1.0.0"}`

---

## ▲ Vercel 배포 (프론트엔드)

### 9. Vercel 프로젝트 생성
- [ ] Vercel CLI 설치: `npm install -g vercel`
- [ ] Vercel 로그인: `vercel login`
- [ ] 프로젝트 배포: `vercel`
- [ ] 프로젝트 이름: `autogram`

### 10. Vercel 환경 변수 설정
Vercel 대시보드 → Settings → Environment Variables:

- [ ] `NEXT_PUBLIC_API_URL=https://{railway-domain}.up.railway.app`

### 11. Vercel 프로덕션 배포
- [ ] `vercel --prod` 실행
- [ ] 배포 성공 확인
- [ ] 도메인 저장: `_______________.vercel.app`

### 12. Vercel 접속 확인
- [ ] `https://{domain}` 접속
- [ ] 홈페이지 로딩 확인
- [ ] `/admin/login` 접속 확인
- [ ] 관리자 로그인 테스트

---

## 🔄 배포 후 설정

### 13. CORS 업데이트
- [ ] Railway 대시보드로 돌아가기
- [ ] `CORS_ORIGINS` 환경 변수 업데이트:
  ```
  https://{vercel-domain}.vercel.app
  ```
- [ ] Railway 서비스 재시작

### 14. 전체 API 테스트
- [ ] `/api/py/health` - 헬스 체크
- [ ] `/api/py/docs` - API 문서
- [ ] `/api/py/admin/login` - 관리자 로그인
- [ ] `/api/py/admin/users` - 사용자 목록
- [ ] `/api/py/public/instagram-links` - 공개 API

### 15. 프론트엔드 전체 테스트
- [ ] 홈페이지 (`/`)
- [ ] 신청 페이지 (`/apply`)
- [ ] 랭킹 페이지 (`/ranking`)
- [ ] 관리자 로그인 (`/admin/login`)
- [ ] 관리자 대시보드 (`/admin/dashboard`)
- [ ] 사용자 관리 (`/admin/users`)
- [ ] 요청 관리 (`/admin/requests`)

---

## ⚙️ 배치 작업 설정

### 16. GitHub Secrets 설정
GitHub 레포지토리 → Settings → Secrets and variables → Actions:

- [ ] `DATABASE_URL` (Supabase URL)
- [ ] `SECRET_KEY`
- [ ] `ENCRYPTION_KEY`

### 17. GitHub Actions 확인
- [ ] `.github/workflows/batch.yml` 파일 확인
- [ ] GitHub Actions 탭에서 워크플로우 확인
- [ ] 수동 실행 테스트 (Actions → Run Batch Jobs → Run workflow)

### 18. Cron Job 스케줄 확인
- [ ] 스케줄: 매주 월요일 오전 10시 (한국시간)
- [ ] Cron 표현식: `0 1 * * 1` (UTC)

---

## 📊 모니터링 설정

### 19. Railway 모니터링
- [ ] Railway 대시보드 → Observability 확인
- [ ] 로그 확인: `railway logs`
- [ ] 메트릭 확인 (CPU, 메모리, 네트워크)

### 20. Vercel 모니터링
- [ ] Vercel 대시보드 → Deployments
- [ ] 로그 확인
- [ ] Analytics 확인 (옵션)

### 21. Supabase 모니터링
- [ ] Supabase 대시보드 → Database → Logs
- [ ] Table Editor에서 데이터 확인
- [ ] 쿼리 성능 확인

---

## 🔒 보안 체크

### 22. 환경 변수 보안
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] GitHub에 민감한 정보가 커밋되지 않았는지 확인
- [ ] Railway와 Vercel의 환경 변수가 안전하게 저장되어 있는지 확인

### 23. API 보안
- [ ] CORS 설정이 올바른지 확인
- [ ] JWT 인증이 작동하는지 확인
- [ ] 관리자 엔드포인트가 보호되어 있는지 확인

### 24. 데이터베이스 보안
- [ ] Supabase 프로젝트 비밀번호가 강력한지 확인
- [ ] DATABASE_URL이 노출되지 않았는지 확인

---

## 📝 문서화

### 25. README 업데이트
- [ ] 배포된 URL 추가
- [ ] API 문서 링크 추가
- [ ] 사용 방법 업데이트

### 26. 배포 정보 문서화
다음 정보를 안전한 곳에 저장:

```
# 프로덕션 URL
프론트엔드: https://_______________.vercel.app
백엔드: https://_______________.up.railway.app
API 문서: https://_______________.up.railway.app/api/py/docs

# 관리자 계정
Username: admin
Password: ______________

# 데이터베이스
Supabase Project: ______________
Database URL: postgresql+asyncpg://...

# 배포 날짜
배포 완료: 2025-__-__
```

---

## ✅ 최종 확인

### 27. 사용자 시나리오 테스트
- [ ] 신규 사용자 등록
- [ ] Instagram 링크 신청
- [ ] 랭킹 조회
- [ ] 관리자 로그인
- [ ] 요청 승인/거부
- [ ] 사용자 활성화/비활성화

### 28. 성능 테스트
- [ ] 페이지 로딩 속도 확인
- [ ] API 응답 시간 확인
- [ ] 데이터베이스 쿼리 성능 확인

### 29. 에러 처리 테스트
- [ ] 잘못된 로그인 시도
- [ ] 존재하지 않는 페이지 접근
- [ ] API 권한 오류
- [ ] 네트워크 오류 처리

---

## 🎉 배포 완료!

모든 체크리스트를 완료했다면 배포가 성공적으로 완료되었습니다!

### 다음 단계
1. 실제 사용자에게 테스트 요청
2. 피드백 수집
3. 버그 수정 및 기능 개선
4. 정기적인 모니터링

### 비용 관리
- **현재 예상 비용**: $5/월 (Railway)
- Supabase Free: $0/월
- Vercel Hobby: $0/월

### 지원 및 문서
- DEPLOYMENT.md: 상세 배포 가이드
- SUPABASE_SETUP.md: Supabase 설정 가이드
- API 문서: `/api/py/docs`

---

**배포 완료 날짜**: _______________
**배포자**: _______________
