# 🚀 Vercel 배포 가이드 - invest-sns

## 1. 사전 준비

### 필수 계정
- GitHub 계정
- Vercel 계정 (GitHub로 연동)
- Supabase 계정 (DB 연결용)

### 환경 변수 준비
```bash
# Supabase 설정
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# 외부 API (선택사항)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 기타 설정
NEXT_PUBLIC_SITE_URL=https://your-app.vercel.app
```

## 2. GitHub 저장소 설정

### 저장소 구조 확인
```
invest-sns/
├── src/app/           # Next.js 16 앱 라우터
├── components/        # React 컴포넌트
├── lib/              # 유틸리티 & API
├── public/           # 정적 파일
├── package.json      # 의존성 정의
├── next.config.js    # Next.js 설정
├── tailwind.config.js # Tailwind CSS
└── vercel.json       # Vercel 설정 (선택)
```

### package.json 확인
```json
{
  "scripts": {
    "build": "next build",
    "start": "next start",
    "dev": "next dev",
    "export": "next export"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "@supabase/supabase-js": "^2.0.0"
  }
}
```

## 3. Vercel 배포 단계

### Step 1: Vercel 대시보드 접속
1. https://vercel.com 로그인
2. "New Project" 클릭
3. GitHub 연동 승인

### Step 2: 저장소 선택
1. `puing5555/invest-sns` 저장소 선택
2. "Import" 클릭

### Step 3: 프로젝트 설정
```bash
Framework Preset: Next.js
Root Directory: ./        # 기본값
Build Command: npm run build   # 자동 감지됨
Output Directory: .next   # 자동 감지됨
Install Command: npm install   # 자동 감지됨
```

### Step 4: 환경 변수 설정
```bash
# Environment Variables 섹션에서 추가
NEXT_PUBLIC_SUPABASE_URL → https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY → eyJ0eXAi...
SUPABASE_SERVICE_ROLE_KEY → eyJ0eXAi... (서버 전용)
NEXT_PUBLIC_SITE_URL → https://invest-sns.vercel.app
```

### Step 5: 배포 실행
1. "Deploy" 버튼 클릭
2. 빌드 로그 확인 (2-3분 소요)
3. 배포 완료 시 URL 생성

## 4. 커스텀 도메인 설정 (선택)

### 도메인 연결
1. Vercel 프로젝트 → Settings → Domains
2. 도메인명 입력 (예: invest-sns.com)
3. DNS 설정 추가:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   
   Type: A
   Name: @
   Value: 76.76.19.61
   ```

## 5. 자동 배포 설정

### GitHub 연동 (기본 활성화)
- `main` 브랜치 푸시 시 자동 배포
- PR 생성 시 Preview 배포 자동 생성
- 커밋마다 빌드 로그 확인 가능

### 브랜치별 배포 설정
```bash
# Production: main 브랜치
main → https://invest-sns.vercel.app

# Preview: 기타 브랜치
develop → https://invest-sns-git-develop-puing5555.vercel.app
feature/new → https://invest-sns-git-feature-new-puing5555.vercel.app
```

## 6. 성능 최적화

### next.config.js 설정
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',  // 서버리스 최적화
  images: {
    domains: ['ui-avatars.com', 'supabase.co'],
    formats: ['image/webp', 'image/avif']
  },
  experimental: {
    serverComponentsExternalPackages: ['@supabase/supabase-js']
  }
}

module.exports = nextConfig
```

### Vercel Functions 활용
```bash
# API Routes 자동 서버리스 함수화
src/app/api/signals/route.ts → /api/signals
src/app/api/upload/route.ts → /api/upload
```

## 7. 모니터링 & 디버깅

### Vercel Analytics 활성화
1. 프로젝트 Settings → Analytics
2. "Enable Web Analytics" 클릭
3. 사용자 통계, 성능 지표 확인

### 로그 확인
```bash
# 실시간 로그 확인
npx vercel logs https://invest-sns.vercel.app

# 함수별 로그
Vercel 대시보드 → Functions → 함수명 클릭
```

### 빌드 실패 시 체크리스트
1. **package.json** dependencies 버전 호환성
2. **환경 변수** 누락 여부
3. **next.config.js** 설정 오류
4. **TypeScript** 타입 에러
5. **Import 경로** 대소문자 구분

## 8. 보안 설정

### 환경 변수 보안
```bash
# 클라이언트 노출 (NEXT_PUBLIC_)
NEXT_PUBLIC_SUPABASE_URL ← 공개 가능
NEXT_PUBLIC_SUPABASE_ANON_KEY ← RLS로 보호됨

# 서버 전용 (노출 금지)
SUPABASE_SERVICE_ROLE_KEY ← 절대 클라이언트 노출 금지
OPENAI_API_KEY ← 서버 API에서만 사용
```

### CORS 설정 (Supabase)
```sql
-- Supabase Dashboard → API → CORS
Allowed Origins: https://invest-sns.vercel.app
```

## 9. 배포 체크리스트

### 배포 전 확인사항
- [ ] 로컬 빌드 성공 (`npm run build`)
- [ ] 환경 변수 모두 설정
- [ ] Supabase 연결 테스트
- [ ] 중요한 API 키 보안 확인
- [ ] package.json dependencies 정리

### 배포 후 확인사항
- [ ] 메인 페이지 로딩
- [ ] Supabase 데이터 조회
- [ ] API Routes 동작
- [ ] 이미지 로딩 (UI Avatars)
- [ ] 모바일 반응형 확인

## 10. 배포 명령어 (자동화)

### 원클릭 배포 스크립트
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Vercel 배포 시작..."

# 1. 코드 품질 검사
npm run lint
npm run type-check

# 2. 로컬 빌드 테스트
npm run build

# 3. Git 커밋 & 푸시
git add .
git commit -m "deploy: $(date)"
git push origin main

# 4. Vercel CLI로 직접 배포 (선택)
# npx vercel --prod

echo "✅ 배포 완료!"
echo "📱 URL: https://invest-sns.vercel.app"
```

### Vercel CLI 사용법
```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 연결
vercel link

# 개발 서버 (로컬)
vercel dev

# 미리보기 배포
vercel

# 프로덕션 배포  
vercel --prod
```

## 11. 문제 해결

### 자주 발생하는 오류

**1. 빌드 실패 - TypeScript 에러**
```bash
# 해결: 타입 오류 수정 후 재배포
npm run type-check
```

**2. Supabase 연결 실패**
```bash
# 확인: 환경 변수 정확성
console.log(process.env.NEXT_PUBLIC_SUPABASE_URL)
```

**3. 404 페이지**
```bash
# 확인: next.config.js의 output 설정
output: 'export' vs 'standalone'
```

## 12. 성공 확인

### 최종 테스트 URL
- **메인**: https://invest-sns.vercel.app
- **피드**: https://invest-sns.vercel.app/feed
- **종목**: https://invest-sns.vercel.app/stock/005930
- **API**: https://invest-sns.vercel.app/api/signals

### 완료 알림
```
🎉 invest-sns Vercel 배포 완료!

📱 라이브: https://invest-sns.vercel.app
🔧 대시보드: https://vercel.com/puing5555/invest-sns
📊 Analytics: Vercel 대시보드에서 확인

다음: 자동 시그널 수집 파이프라인 연동
```

---

**💡 주의사항**: Next.js 16은 최신 버전이므로 일부 패키지 호환성 이슈가 있을 수 있습니다. 빌드 실패 시 Next.js 15로 다운그레이드를 고려하세요.