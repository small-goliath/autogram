# Supabase 설정 가이드

이 가이드는 Autogram 프로젝트를 Supabase PostgreSQL 데이터베이스와 연결하는 방법을 설명합니다.

## 1. Supabase 프로젝트 생성

### 1.1 Supabase 계정 생성
1. https://supabase.com 접속
2. "Start your project" 클릭
3. GitHub 계정으로 로그인

### 1.2 새 프로젝트 생성
1. "New Project" 클릭
2. 프로젝트 정보 입력:
   - **Name**: autogram (또는 원하는 이름)
   - **Database Password**: 강력한 비밀번호 생성 (저장해두세요!)
   - **Region**: Northeast Asia (Seoul) - 한국에서 가장 가까운 리전
   - **Pricing Plan**: Free (개발용) 또는 Pro (프로덕션용)
3. "Create new project" 클릭
4. 프로젝트 생성 완료 대기 (약 2분)

## 2. 데이터베이스 연결 문자열 가져오기

### 2.1 연결 정보 확인
1. Supabase 대시보드에서 프로젝트 선택
2. 왼쪽 메뉴에서 **Settings** (⚙️) 클릭
3. **Database** 클릭
4. "Connection string" 섹션에서 **URI** 탭 선택

### 2.2 연결 문자열 복사
다음 형식의 문자열이 표시됩니다:
```
postgresql://postgres.{project-ref}:[YOUR-PASSWORD]@db.{project-ref}.supabase.co:5432/postgres
```

**중요**: `[YOUR-PASSWORD]`를 프로젝트 생성 시 설정한 비밀번호로 교체하세요!

### 2.3 AsyncPG 형식으로 변경
Autogram은 비동기 PostgreSQL 드라이버를 사용하므로, 연결 문자열을 다음과 같이 변경해야 합니다:

**변경 전** (Supabase 제공):
```
postgresql://postgres.{project-ref}:your-password@db.{project-ref}.supabase.co:5432/postgres
```

**변경 후** (AsyncPG):
```
postgresql+asyncpg://postgres.{project-ref}:your-password@db.{project-ref}.supabase.co:5432/postgres
```

**주의**: `postgresql://` → `postgresql+asyncpg://`로 변경!

## 3. 환경 변수 설정

### 3.1 .env 파일 업데이트
프로젝트 루트의 `.env` 파일을 열고 `DATABASE_URL`을 업데이트합니다:

```bash
# 기존 SQLite (주석 처리)
# DATABASE_URL=sqlite+aiosqlite:///./autogram.db

# Supabase PostgreSQL (활성화)
DATABASE_URL=postgresql+asyncpg://postgres.abcdefghijkl:your-strong-password@db.abcdefghijkl.supabase.co:5432/postgres
```

**실제 값 예시**:
```bash
DATABASE_URL=postgresql+asyncpg://postgres.abcdefghijkl:MyStr0ngP@ssw0rd@db.abcdefghijkl.supabase.co:5432/postgres
```

### 3.2 기타 환경 변수 확인
`.env` 파일에 다음 설정들이 있는지 확인:

```bash
# Security
SECRET_KEY=t2gWxAlX3m5XGaIJCDPdEPA9eV4pPl3QFqUI1GyE-1k
ENCRYPTION_KEY=kJSOsCGSr0wvHWmlNzuWGRyv9KdzMq7vEtZ4kQqCZqg=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# KakaoTalk
HELPER_SESSION_DIR=./sessions
KAKAOTALK_FILE_PATH=batch/kakaotalk/KakaoTalk_latest.txt
KAKAOTALK_OPEN_CHAT_LINK=https://open.kakao.com/your-link
KAKAOTALK_QR_CODE_PATH=/images/kakao-qr.png
```

## 4. 데이터베이스 마이그레이션 실행

### 4.1 가상환경 활성화
```bash
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 4.2 의존성 확인
```bash
pip install asyncpg psycopg2-binary
```

### 4.3 마이그레이션 실행
```bash
# 마이그레이션 생성 (이미 있으면 건너뛰기)
alembic revision --autogenerate -m "Initial migration for Supabase"

# 마이그레이션 적용
alembic upgrade head
```

### 4.4 마이그레이션 확인
Supabase 대시보드에서 확인:
1. 왼쪽 메뉴 **Table Editor** 클릭
2. 다음 테이블들이 생성되었는지 확인:
   - admin
   - sns_raise_user
   - request_by_week
   - user_action_verification
   - helper
   - consumer
   - producer
   - notice
   - alembic_version

## 5. 관리자 계정 생성

```bash
python scripts/create_admin.py
```

입력 정보:
- Username: admin
- Email: admin@autogram.com
- Password: (원하는 비밀번호)
- Confirm Password: (동일한 비밀번호)

## 6. 서버 실행 및 테스트

### 6.1 백엔드 서버 실행
```bash
# 터미널 1
source venv/bin/activate
uvicorn api.index:app --reload --port 8000
```

### 6.2 API 테스트
```bash
# 헬스 체크
curl http://localhost:8000/api/py/health

# 예상 결과:
# {"status":"healthy","app":"Autogram","version":"1.0.0"}
```

### 6.3 관리자 로그인 테스트
```bash
curl -X POST "http://localhost:8000/api/py/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your-password"

# 예상 결과:
# {"access_token":"eyJ...","token_type":"bearer"}
```

### 6.4 프론트엔드 실행
```bash
# 터미널 2
npm run next-dev
```

브라우저에서 접속:
- 프론트엔드: http://localhost:3000
- 관리자 로그인: http://localhost:3000/admin/login

## 7. Supabase 대시보드 활용

### 7.1 Table Editor
- 실시간으로 데이터 확인 및 편집
- SQL 쿼리 직접 실행 가능

### 7.2 Database Backups
1. **Settings** → **Database** → **Backups**
2. 자동 백업 설정 (Pro 플랜)
3. 수동 백업 생성 가능

### 7.3 SQL Editor
복잡한 쿼리 실행:
```sql
-- 모든 사용자 조회
SELECT * FROM sns_raise_user;

-- 활성 사용자 수 확인
SELECT COUNT(*) FROM sns_raise_user WHERE is_active = true;

-- 최근 요청 조회
SELECT * FROM request_by_week
ORDER BY created_at DESC
LIMIT 10;
```

## 8. 프로덕션 배포 시 추가 설정

### 8.1 환경 변수 보안
프로덕션에서는 `.env` 파일 대신 환경 변수 사용:
- Vercel: Settings → Environment Variables
- Railway: Settings → Variables
- Docker: docker-compose.yml 또는 .env 파일

### 8.2 DATABASE_URL 설정 (프로덕션)
```bash
# Pooling 활성화 (권장)
DATABASE_URL=postgresql+asyncpg://postgres.{ref}:password@{host}:6543/postgres?pgbouncer=true

# 또는 Direct connection
DATABASE_URL=postgresql+asyncpg://postgres.{ref}:password@{host}:5432/postgres
```

**Connection Pooling (PgBouncer)**:
- 포트 6543 사용
- 동시 연결 수 제한
- 성능 향상

### 8.3 SSL 연결 (권장)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### 8.4 CORS 설정
프로덕션 도메인 추가:
```bash
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 9. 문제 해결

### 문제: "connection refused" 또는 "could not connect"
**해결책**:
1. DATABASE_URL이 정확한지 확인
2. 비밀번호에 특수문자가 있으면 URL 인코딩
3. Supabase 프로젝트가 활성화되어 있는지 확인

### 문제: "database does not exist"
**해결책**:
1. 데이터베이스 이름이 `postgres`인지 확인
2. Supabase는 기본적으로 `postgres` 데이터베이스 사용

### 문제: "password authentication failed"
**해결책**:
1. Supabase 대시보드에서 비밀번호 재설정
2. Settings → Database → Reset database password

### 문제: "too many connections"
**해결책**:
1. Connection pooling 사용 (포트 6543)
2. DATABASE_URL에 `?pgbouncer=true` 추가

### 문제: "SSL connection required"
**해결책**:
DATABASE_URL에 SSL 파라미터 추가:
```bash
DATABASE_URL=postgresql+asyncpg://...?ssl=require
```

## 10. 유용한 Supabase 명령어

### 데이터베이스 초기화 (주의!)
```sql
-- 모든 테이블 삭제 (개발 환경에서만!)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- 그 후 마이그레이션 재실행
alembic upgrade head
```

### 테이블 통계 확인
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 11. 요금 및 제한사항

### Free Tier (무료)
- ✅ 500MB 데이터베이스
- ✅ 무제한 API 요청
- ✅ 2GB 파일 스토리지
- ✅ 50MB 파일 업로드
- ⚠️ 7일간 비활성 시 일시정지

### Pro Tier ($25/월)
- ✅ 8GB 데이터베이스
- ✅ 100GB 파일 스토리지
- ✅ 5GB 파일 업로드
- ✅ 자동 백업
- ✅ 커스텀 도메인

## 12. 추가 리소스

- 📚 Supabase 문서: https://supabase.com/docs
- 🎓 SQLAlchemy + AsyncPG: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg
- 💬 Supabase Discord: https://discord.supabase.com
- 🐛 이슈 리포트: https://github.com/supabase/supabase/issues

---

**완료!** 🎉 Autogram이 이제 Supabase PostgreSQL과 연결되었습니다!
