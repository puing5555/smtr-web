"""
Database models for the investment engine
All tables linked through stock_code as the universal key
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

Base = declarative_base()
KST = pytz.timezone('Asia/Seoul')
now_kst = lambda: datetime.now(KST)


class Stock(Base):
    """종목 마스터 테이블 - 모든 데이터의 중심"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), unique=True, index=True, nullable=False)  # 종목코드 "005930"
    corp_code = Column(String(10), unique=True, index=True)  # DART 회사코드 "00126380"
    corp_name = Column(String(100), nullable=False)  # 회사명
    market = Column(String(20))  # KOSPI / KOSDAQ / KONEX
    sector = Column(String(100))  # 업종
    market_cap = Column(Float)  # 시가총액
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    # Relationships
    filings = relationship("DartFiling", back_populates="stock")
    price_alerts = relationship("PriceAlert", back_populates="stock")
    buzz_data = relationship("BuzzData", back_populates="stock")
    influencer_signals = relationship("InfluencerSignal", back_populates="stock")
    fund_flows = relationship("FundFlow", back_populates="stock")
    short_sellings = relationship("ShortSelling", back_populates="stock")


class WatchList(Base):
    """유저별 관심종목"""
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False)
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock")


class DartFiling(Base):
    """DART 공시"""
    __tablename__ = "dart_filings"
    
    id = Column(Integer, primary_key=True, index=True)
    rcept_no = Column(String(50), unique=True, index=True, nullable=False)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), index=True)  # 종목코드 연결
    corp_code = Column(String(10), index=True)
    corp_name = Column(String(100), nullable=False)
    corp_cls = Column(String(10))  # Y:유가 K:코스닥 N:코넥스 E:기타
    report_nm = Column(String(200), nullable=False)
    rcept_dt = Column(String(10), index=True)  # YYYYMMDD
    flr_nm = Column(String(100))
    rm = Column(Text)
    
    # 분류 및 분석
    grade = Column(String(1))  # A:정기공시 B:중요비정기 C:기타
    category = Column(String(50))  # earnings, equity, capital, governance, etc.
    ai_summary = Column(Text)  # AI 요약
    ai_analysis = Column(Text)  # AI 투자 분석
    is_alerted = Column(Boolean, default=False)  # 알림 발송 여부
    
    # 실적 데이터 (A등급용)
    revenue = Column(Float)  # 매출
    operating_income = Column(Float)  # 영업이익
    net_income = Column(Float)  # 순이익
    revenue_prev = Column(Float)  # 전년 매출
    operating_income_prev = Column(Float)  # 전년 영업이익
    net_income_prev = Column(Float)  # 전년 순이익
    revenue_estimate = Column(Float)  # 예상 매출
    operating_income_estimate = Column(Float)  # 예상 영업이익
    
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="filings")
    
    __table_args__ = (
        Index('ix_dart_stock_date', 'stock_code', 'rcept_dt'),
    )


class AlertsLog(Base):
    """발송 알림 기록"""
    __tablename__ = "alerts_log"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # DART, PRICE, NEWS, INFLUENCER, BUZZ
    stock_code = Column(String(10), index=True)  # 관련 종목
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(20), nullable=False)  # telegram, web, sns
    recipient = Column(String(100), nullable=False)
    sent_at = Column(DateTime, default=now_kst)
    status = Column(String(20), default="sent")


class News(Base):
    """뉴스"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text)
    url = Column(String(500), unique=True, index=True)
    source = Column(String(50), nullable=False)
    market = Column(String(10), default='kr', index=True)  # 'kr', 'us', 'global' 등
    published_at = Column(DateTime)
    stock_codes = Column(JSON)  # ["005930", "000660"] for KR, ["AAPL", "NVDA"] for US
    sentiment_score = Column(Float)
    importance_score = Column(Float)
    ai_summary = Column(Text)
    created_at = Column(DateTime, default=now_kst)


class PriceAlert(Base):
    """급등락 알림"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False)  # SURGE, PLUNGE
    price_change_pct = Column(Float, nullable=False)
    prev_price = Column(Float, nullable=False)
    curr_price = Column(Float, nullable=False)
    volume = Column(Integer)
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="price_alerts")


class PriceHistory(Base):
    """주가 히스토리 (공시 후 수익률 추적용)"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYYMMDD
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    change_pct = Column(Float)
    created_at = Column(DateTime, default=now_kst)
    
    __table_args__ = (
        Index('ix_price_stock_date', 'stock_code', 'date', unique=True),
    )


class BuzzData(Base):
    """쏠림 데이터"""
    __tablename__ = "buzz_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # NAVER_FORUM, GOOGLE_TRENDS, etc.
    mention_count = Column(Integer, default=0)
    sentiment_score = Column(Float)
    buzz_score = Column(Float)
    data_date = Column(String(10), nullable=False)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="buzz_data")
    
    __table_args__ = (
        Index('ix_buzz_stock_date', 'stock_code', 'data_date'),
    )


class InfluencerVideo(Base):
    """유튜브 인플루언서 영상"""
    __tablename__ = "influencer_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(50), nullable=False, index=True)
    channel_name = Column(String(100), nullable=False)
    video_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    transcript = Column(Text)  # 자막/STT 텍스트
    created_at = Column(DateTime, default=now_kst)


class InfluencerSignal(Base):
    """인플루언서 종목 시그널 (영상에서 추출)"""
    __tablename__ = "influencer_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), ForeignKey("influencer_videos.video_id"), nullable=False, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    channel_name = Column(String(100), nullable=False)
    signal_type = Column(String(20))  # BUY, SELL, HOLD, MENTION
    confidence = Column(Float)  # 신뢰도 0~1
    context = Column(Text)  # 언급 맥락
    mentioned_at = Column(DateTime, nullable=False)
    
    # 시그널 이후 수익률 추적
    price_at_signal = Column(Float)
    price_1d = Column(Float)
    price_3d = Column(Float)
    price_1w = Column(Float)
    price_1m = Column(Float)
    return_1d = Column(Float)
    return_3d = Column(Float)
    return_1w = Column(Float)
    return_1m = Column(Float)
    
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="influencer_signals")
    video = relationship("InfluencerVideo")
    
    __table_args__ = (
        Index('ix_signal_stock_date', 'stock_code', 'mentioned_at'),
    )


class FundFlow(Base):
    """외국인/기관 수급"""
    __tablename__ = "fund_flow"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    date = Column(String(10), nullable=False)
    foreign_net = Column(Float)  # 외국인 순매수 (억원)
    institution_net = Column(Float)  # 기관 순매수
    pension_net = Column(Float)  # 연기금 순매수
    trust_net = Column(Float)  # 투신 순매수
    retail_net = Column(Float)  # 개인 순매수
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="fund_flows")
    
    __table_args__ = (
        Index('ix_fund_stock_date', 'stock_code', 'date', unique=True),
    )


class ShortSelling(Base):
    """공매도 데이터"""
    __tablename__ = "short_selling"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    date = Column(String(10), nullable=False)
    short_volume = Column(Integer)  # 공매도 수량
    short_amount = Column(Float)  # 공매도 금액 (억원)
    short_ratio = Column(Float)  # 공매도 비율 (%)
    balance_volume = Column(Integer)  # 대차잔고 수량
    balance_amount = Column(Float)  # 대차잔고 금액
    created_at = Column(DateTime, default=now_kst)
    
    stock = relationship("Stock", back_populates="short_sellings")
    
    __table_args__ = (
        Index('ix_short_stock_date', 'stock_code', 'date', unique=True),
    )


class Note(Base):
    """노트 (메모 + 스크랩 통합)"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)  # 사용자 ID
    note_type = Column(String(20), nullable=False)  # memo, scrap, news, filing
    
    # 기본 정보
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # 스크랩 관련
    url = Column(String(500), nullable=True)  # 스크랩된 URL
    source_title = Column(String(300), nullable=True)  # 원본 제목
    source_description = Column(Text, nullable=True)  # 원본 설명
    
    # 종목 연결
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=True, index=True)
    stock_name = Column(String(100), nullable=True)  # 빠른 조회용 복사본
    
    # 분류
    folder = Column(String(50), nullable=True)  # 폴더명
    tags = Column(JSON, nullable=True)  # ["태그1", "태그2"]
    
    # 메타데이터
    is_bookmarked = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # SNS 공유 여부
    importance = Column(Integer, default=0)  # 0:일반, 1:중요
    
    # 자동 스크랩 메타데이터 (timeline에서 북마크시)
    source_id = Column(String(50), nullable=True)  # 원본 뉴스/공시 ID
    source_type = Column(String(20), nullable=True)  # news, filing
    
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    # Relationships
    stock = relationship("Stock")
    
    __table_args__ = (
        Index('ix_note_user_type', 'user_id', 'note_type'),
        Index('ix_note_user_created', 'user_id', 'created_at'),
    )


class NoteFolder(Base):
    """사용자별 노트 폴더 관리"""
    __tablename__ = "note_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    folder_name = Column(String(50), nullable=False)
    folder_type = Column(String(20), nullable=False)  # memo, scrap, mixed
    color = Column(String(7), default="#667eea")  # 폴더 색상
    note_count = Column(Integer, default=0)  # 폴더 내 노트 수
    is_default = Column(Boolean, default=False)  # 기본 폴더 여부
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    __table_args__ = (
        Index('ix_folder_user', 'user_id', 'folder_name', unique=True),
    )


class SNSPost(Base):
    """SNS 포스트"""
    __tablename__ = "sns_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    author_name = Column(String(100), nullable=False)
    
    # 포스트 내용
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # 스크랩 공유인 경우
    is_scrap_share = Column(Boolean, default=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)  # 연결된 노트
    
    # 종목 태그
    stock_tags = Column(JSON, nullable=True)  # ["삼성전자", "AAPL"]
    
    # 상호작용
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # 메타데이터
    is_public = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    # Relationships
    note = relationship("Note")
    comments = relationship("SNSComment", back_populates="post")
    
    __table_args__ = (
        Index('ix_sns_user_created', 'user_id', 'created_at'),
        Index('ix_sns_public_created', 'is_public', 'created_at'),
    )


class SNSComment(Base):
    """SNS 댓글"""
    __tablename__ = "sns_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("sns_posts.id"), nullable=False)
    user_id = Column(String(50), nullable=False)
    author_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=now_kst)
    
    # Relationships
    post = relationship("SNSPost", back_populates="comments")


class UserFollow(Base):
    """사용자 팔로우 관계"""
    __tablename__ = "user_follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String(50), nullable=False, index=True)  # 팔로우하는 사람
    following_id = Column(String(50), nullable=False, index=True)  # 팔로우 당하는 사람
    created_at = Column(DateTime, default=now_kst)
    
    __table_args__ = (
        Index('ix_follow_relation', 'follower_id', 'following_id', unique=True),
    )


class UserProfile(Base):
    """사용자 프로필"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_text = Column(String(2), nullable=False)  # 아바타 텍스트 (예: "김")
    
    # 통계
    posts_count = Column(Integer, default=0)
    notes_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    
    # 설정
    is_public = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    __table_args__ = (
        Index('ix_user_profile_username', 'username'),
    )


class User(Base):
    """유저 정보"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # 외부 사용자 ID
    name = Column(String(100), nullable=False)
    email = Column(String(255))
    bio = Column(Text)  # 소개
    
    # 투자성향 (필수)
    investment_style = Column(String(50), nullable=False, default="가치투자자")
    # 가치투자자, 모멘텀투자자, 단타, 스윙, 배당투자자, 인덱스투자자, 비트코이너
    
    # 프로필 설정
    avatar = Column(String(255))  # 프로필 이미지 URL
    is_public = Column(Boolean, default=True)  # 공개 프로필 여부
    is_verified = Column(Boolean, default=False)  # 인증된 사용자
    
    # 통계
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="user")


class Badge(Base):
    """뱃지 마스터 테이블"""
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # 뱃지명
    description = Column(Text)  # 뱃지 설명
    icon = Column(String(100))  # 아이콘/이미지 URL 또는 이모지
    category = Column(String(30), default="general")  # general, achievement, special
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=now_kst)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    """사용자-뱃지 연결 테이블"""
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)
    
    # 뱃지 획득 관련
    earned_at = Column(DateTime, default=now_kst)  # 획득 시간
    earned_reason = Column(String(200))  # 획득 사유
    is_displayed = Column(Boolean, default=True)  # 프로필에 표시할지 여부
    
    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    __table_args__ = (
        Index('ix_user_badge_unique', 'user_id', 'badge_id', unique=True),
    )
