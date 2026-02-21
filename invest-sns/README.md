# 투자SNS - 스마트한 투자 소통 플랫폼

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3+-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![Supabase](https://img.shields.io/badge/Supabase-green?style=flat-square&logo=supabase)](https://supabase.com/)

## 📝 프로젝트 소개

투자SNS는 투자자들이 서로 소통하고 인플루언서의 투자 시그널을 공유하는 모바일 퍼스트 SNS 플랫폼입니다.

### ✨ 주요 기능

- 🚀 **실시간 투자 피드** - 인플루언서와 일반 투자자들의 투자 인사이트 공유
- 📊 **투자 시그널** - 검증된 인플루언서들의 매수/매도 시그널
- 🔔 **스마트 알림** - 관심 종목 및 팔로우한 인플루언서 활동 알림
- 🤖 **AI 트레이딩 봇** - AI 기반 투자 추천 및 분석
- ⭐ **관심종목 관리** - 개인화된 종목 관리 및 추적
- 📰 **뉴스 분석** - AI를 통한 투자 관련 뉴스 분석
- 👑 **프리미엄 기능** - 고급 분석 도구 및 독점 콘텐츠
- 👤 **인플루언서 프로필** - 성과 기반 인플루언서 검증 시스템

## 🛠️ 기술 스택

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: Zustand
- **Icons**: Lucide React

### Backend
- **API**: Next.js API Routes
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Real-time**: Supabase Realtime

### Development
- **Package Manager**: npm
- **Code Quality**: ESLint
- **Deployment**: Vercel (예정)

## 📁 프로젝트 구조

```
invest-sns/
├── database/
│   └── schema.sql              # 데이터베이스 스키마
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # 인증 관련 페이지
│   │   ├── (main)/            # 메인 애플리케이션
│   │   │   ├── feed/          # SNS 피드
│   │   │   ├── signals/       # 투자 시그널
│   │   │   ├── alerts/        # 알림 시스템
│   │   │   ├── bots/          # AI 트레이딩 봇
│   │   │   ├── stocks/        # 관심종목
│   │   │   ├── news/          # 뉴스 분석
│   │   │   ├── premium/       # 프리미엄 기능
│   │   │   └── profile/       # 프로필
│   │   ├── globals.css        # 글로벌 스타일
│   │   └── layout.tsx         # 루트 레이아웃
│   ├── components/
│   │   ├── ui/                # shadcn/ui 컴포넌트
│   │   ├── feed/              # 피드 관련 컴포넌트
│   │   ├── signals/           # 시그널 관련 컴포넌트
│   │   └── common/            # 공통 컴포넌트
│   ├── lib/
│   │   ├── supabase/          # Supabase 클라이언트
│   │   ├── api/               # API 헬퍼 함수
│   │   └── utils.ts           # 유틸리티 함수
│   ├── types/
│   │   └── database.ts        # TypeScript 타입 정의
│   └── stores/
│       ├── auth.ts            # 인증 상태 관리
│       └── feed.ts            # 피드 상태 관리
├── public/                     # 정적 파일
├── components.json             # shadcn/ui 설정
├── tailwind.config.ts          # Tailwind CSS 설정
├── tsconfig.json              # TypeScript 설정
└── package.json               # 의존성 및 스크립트
```

## 🚀 시작하기

### 필요 조건

- Node.js 18 이상
- npm 또는 yarn
- Supabase 계정 (데이터베이스 연결 시)

### 설치 및 실행

1. **의존성 설치**
   ```bash
   npm install
   ```

2. **개발 서버 실행**
   ```bash
   npm run dev
   ```

3. **브라우저에서 확인**
   - http://localhost:3000 접속

### 환경 설정 (향후 Supabase 연동 시)

1. `.env.local` 파일 생성
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

2. Supabase 데이터베이스 스키마 적용
   ```bash
   # database/schema.sql 파일을 Supabase SQL 에디터에서 실행
   ```

## 🗃️ 데이터베이스 스키마

주요 테이블:
- `users` - 사용자 프로필 및 투자 성향
- `influencers` - 인플루언서 정보 및 성과
- `posts` - SNS 피드 게시물
- `signals` - 투자 시그널
- `stocks` - 종목 정보
- `comments` - 댓글
- `likes` - 좋아요
- `follows` - 팔로우 관계
- `watchlist` - 관심종목
- `notifications` - 알림
- `news` - 뉴스 데이터

자세한 스키마는 `database/schema.sql` 파일을 참조하세요.

## 🎨 디자인 시스템

### 컬러 팔레트
- **Primary**: Blue (#3B82F6)
- **Secondary**: Purple (#8B5CF6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)

### 타이포그래피
- **제목**: font-bold, text-xl ~ text-3xl
- **본문**: font-normal, text-sm ~ text-base
- **캡션**: font-medium, text-xs

### 컴포넌트
- **모바일 퍼스트** 반응형 디자인
- **shadcn/ui** 기반 일관된 UI 컴포넌트
- **Tailwind CSS** 유틸리티 클래스 활용

## 📱 주요 화면

1. **피드** (`/feed`) - 메인 SNS 피드
2. **시그널** (`/signals`) - 투자 시그널 목록
3. **알림** (`/alerts`) - 실시간 알림
4. **AI봇** (`/bots`) - AI 트레이딩 봇
5. **관심종목** (`/stocks`) - 개인 관심종목 관리
6. **뉴스** (`/news`) - 투자 뉴스 및 분석
7. **프리미엄** (`/premium`) - 유료 기능
8. **프로필** (`/profile`) - 사용자/인플루언서 프로필

## 🔄 상태 관리

### Zustand 스토어

- **Auth Store** (`stores/auth.ts`)
  - 사용자 인증 상태
  - 로그인/로그아웃/회원가입

- **Feed Store** (`stores/feed.ts`)
  - 피드 게시물 목록
  - 필터링 및 페이지네이션
  - 좋아요/댓글 상호작용

## 🧪 개발 도구

### 스크립트
```bash
npm run dev          # 개발 서버 실행
npm run build        # 프로덕션 빌드
npm run start        # 프로덕션 서버 실행
npm run lint         # ESLint 실행
npm run type-check   # TypeScript 타입 체크
```

### VS Code 확장 프로그램 (권장)
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets

## 🛣️ 로드맵

### Phase 1 (현재)
- ✅ 기본 프로젝트 구조 설정
- ✅ UI 컴포넌트 및 레이아웃
- ✅ 피드 페이지 기본 기능
- 🔄 Supabase 연동 준비

### Phase 2 (예정)
- [ ] 사용자 인증 시스템
- [ ] 실제 데이터베이스 연동
- [ ] 투자 시그널 기능
- [ ] 실시간 알림

### Phase 3 (예정)
- [ ] AI 트레이딩 봇
- [ ] 뉴스 분석 기능
- [ ] 프리미엄 기능
- [ ] 모바일 앱 (React Native)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📧 연락처

프로젝트 관련 문의: [이메일 주소]

---

**투자SNS**로 더 스마트한 투자 결정을 내려보세요! 🚀