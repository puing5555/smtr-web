"""
SNS API Router - 소셜 피드 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.db.database import get_db
from src.db.models import SNSPost, SNSComment, UserProfile, UserFollow, Note
from pydantic import BaseModel

router = APIRouter(prefix="/api/sns", tags=["sns"])

# Pydantic Models
class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    stock_tags: Optional[List[str]] = None
    is_public: bool = True

class CommentCreate(BaseModel):
    content: str

class UserFollowRequest(BaseModel):
    following_id: str

# Helper functions
def get_current_user_id() -> str:
    # TODO: 실제 인증 시스템 연동
    return "user_me"

def get_user_profile(db: Session, user_id: str) -> UserProfile:
    """사용자 프로필 조회 또는 생성"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        # 기본 프로필 생성
        profile = UserProfile(
            user_id=user_id,
            username="사용자" + user_id[-4:],  # 임시 사용자명
            avatar_text=user_id[0].upper(),
            bio="투자자입니다"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

def update_user_stats(db: Session, user_id: str):
    """사용자 통계 업데이트"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        # 포스트 수 업데이트
        posts_count = db.query(SNSPost).filter(SNSPost.user_id == user_id).count()
        profile.posts_count = posts_count
        
        # 팔로워/팔로잉 수 업데이트
        followers_count = db.query(UserFollow).filter(UserFollow.following_id == user_id).count()
        following_count = db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()
        profile.followers_count = followers_count
        profile.following_count = following_count
        
        db.commit()

# API Endpoints
@router.get("/feed")
async def get_feed(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user_id: Optional[str] = Query(None, description="특정 사용자의 포스트만 조회")
):
    """SNS 피드 조회"""
    current_user_id = get_current_user_id()
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(SNSPost).filter(SNSPost.is_public == True)
    
    if user_id:
        query = query.filter(SNSPost.user_id == user_id)
    else:
        # 팔로우한 사용자들의 포스트 + 내 포스트
        following_ids = db.query(UserFollow.following_id).filter(
            UserFollow.follower_id == current_user_id
        ).subquery()
        
        query = query.filter(
            (SNSPost.user_id == current_user_id) |
            (SNSPost.user_id.in_(following_ids))
        )
    
    # Sort by created_at desc
    query = query.order_by(SNSPost.created_at.desc())
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    posts = query.offset(offset).limit(limit).all()
    
    # Format response
    formatted_posts = []
    for post in posts:
        # Get user profile
        profile = get_user_profile(db, post.user_id)
        
        # Get comments
        comments = db.query(SNSComment).filter(
            SNSComment.post_id == post.id
        ).order_by(SNSComment.created_at.asc()).limit(3).all()
        
        formatted_comments = []
        for comment in comments:
            comment_profile = get_user_profile(db, comment.user_id)
            formatted_comments.append({
                "id": comment.id,
                "author": comment_profile.username,
                "avatar": comment_profile.avatar_text,
                "content": comment.content,
                "time": get_time_ago(comment.created_at)
            })
        
        # Get scrap data if it's a scrap share
        scrap_data = None
        if post.is_scrap_share and post.note_id:
            note = db.query(Note).filter(Note.id == post.note_id).first()
            if note:
                scrap_data = {
                    "title": note.source_title or note.title,
                    "url": note.url,
                    "description": note.source_description or note.content[:100]
                }
        
        formatted_post = {
            "id": post.id,
            "author": profile.username,
            "author_id": post.user_id,
            "avatar": profile.avatar_text,
            "content": post.content,
            "image_url": post.image_url,
            "is_scrap_share": post.is_scrap_share,
            "scrap_data": scrap_data,
            "stock_tags": post.stock_tags or [],
            "likes": post.likes_count,
            "comments": formatted_comments,
            "comments_count": post.comments_count,
            "created_at": post.created_at.isoformat(),
            "liked": False,  # TODO: 사용자별 좋아요 상태 확인
            "scrapped": False  # TODO: 사용자별 스크랩 상태 확인
        }
        formatted_posts.append(formatted_post)
    
    return {
        "success": True,
        "posts": formatted_posts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit,
            "has_next": page * limit < total_count,
            "has_prev": page > 1
        }
    }

@router.post("/posts")
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """새 포스트 작성"""
    user_id = get_current_user_id()
    profile = get_user_profile(db, user_id)
    
    post = SNSPost(
        user_id=user_id,
        author_name=profile.username,
        content=post_data.content,
        image_url=post_data.image_url,
        stock_tags=post_data.stock_tags,
        is_public=post_data.is_public
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # 사용자 통계 업데이트
    update_user_stats(db, user_id)
    
    return {
        "success": True,
        "message": "포스트가 작성되었습니다",
        "post_id": post.id
    }

@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: int, db: Session = Depends(get_db)):
    """포스트 좋아요 토글"""
    user_id = get_current_user_id()
    
    post = db.query(SNSPost).filter(SNSPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    
    # TODO: 사용자별 좋아요 테이블 구현
    # 현재는 단순히 카운트만 증가/감소
    post.likes_count += 1
    db.commit()
    
    return {
        "success": True,
        "likes": post.likes_count
    }

@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, comment_data: CommentCreate, db: Session = Depends(get_db)):
    """댓글 추가"""
    user_id = get_current_user_id()
    profile = get_user_profile(db, user_id)
    
    post = db.query(SNSPost).filter(SNSPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    
    comment = SNSComment(
        post_id=post_id,
        user_id=user_id,
        author_name=profile.username,
        content=comment_data.content
    )
    
    db.add(comment)
    
    # 댓글 수 증가
    post.comments_count += 1
    
    db.commit()
    db.refresh(comment)
    
    return {
        "success": True,
        "message": "댓글이 추가되었습니다",
        "comment": {
            "id": comment.id,
            "author": profile.username,
            "avatar": profile.avatar_text,
            "content": comment.content,
            "time": "방금 전"
        }
    }

@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: int, db: Session = Depends(get_db)):
    """포스트 댓글 조회"""
    comments = db.query(SNSComment).filter(
        SNSComment.post_id == post_id
    ).order_by(SNSComment.created_at.asc()).all()
    
    formatted_comments = []
    for comment in comments:
        profile = get_user_profile(db, comment.user_id)
        formatted_comments.append({
            "id": comment.id,
            "author": profile.username,
            "avatar": profile.avatar_text,
            "content": comment.content,
            "time": get_time_ago(comment.created_at),
            "created_at": comment.created_at.isoformat()
        })
    
    return {
        "success": True,
        "comments": formatted_comments
    }

@router.post("/follow")
async def follow_user(follow_data: UserFollowRequest, db: Session = Depends(get_db)):
    """사용자 팔로우"""
    follower_id = get_current_user_id()
    following_id = follow_data.following_id
    
    if follower_id == following_id:
        raise HTTPException(status_code=400, detail="자기 자신을 팔로우할 수 없습니다")
    
    # 이미 팔로우 중인지 확인
    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == follower_id,
        UserFollow.following_id == following_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="이미 팔로우 중입니다")
    
    # 팔로우 관계 생성
    follow = UserFollow(
        follower_id=follower_id,
        following_id=following_id
    )
    
    db.add(follow)
    db.commit()
    
    # 통계 업데이트
    update_user_stats(db, follower_id)
    update_user_stats(db, following_id)
    
    return {
        "success": True,
        "message": "팔로우했습니다"
    }

@router.delete("/follow/{following_id}")
async def unfollow_user(following_id: str, db: Session = Depends(get_db)):
    """사용자 언팔로우"""
    follower_id = get_current_user_id()
    
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == follower_id,
        UserFollow.following_id == following_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=404, detail="팔로우 관계를 찾을 수 없습니다")
    
    db.delete(follow)
    db.commit()
    
    # 통계 업데이트
    update_user_stats(db, follower_id)
    update_user_stats(db, following_id)
    
    return {
        "success": True,
        "message": "언팔로우했습니다"
    }

@router.get("/following")
async def get_following(db: Session = Depends(get_db)):
    """팔로잉 목록 조회"""
    user_id = get_current_user_id()
    
    following = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id
    ).all()
    
    following_users = []
    for follow in following:
        profile = get_user_profile(db, follow.following_id)
        following_users.append({
            "user_id": profile.user_id,
            "username": profile.username,
            "avatar": profile.avatar_text,
            "bio": profile.bio,
            "following": True,
            "followers_count": profile.followers_count,
            "posts_count": profile.posts_count
        })
    
    return {
        "success": True,
        "following": following_users
    }

@router.get("/recommended")
async def get_recommended_users(db: Session = Depends(get_db)):
    """추천 사용자 목록"""
    user_id = get_current_user_id()
    
    # 현재 팔로우 중인 사용자 제외
    following_ids = db.query(UserFollow.following_id).filter(
        UserFollow.follower_id == user_id
    ).subquery()
    
    recommended = db.query(UserProfile).filter(
        UserProfile.user_id != user_id,
        ~UserProfile.user_id.in_(following_ids)
    ).limit(10).all()
    
    recommended_users = []
    for profile in recommended:
        recommended_users.append({
            "user_id": profile.user_id,
            "username": profile.username,
            "avatar": profile.avatar_text,
            "bio": profile.bio,
            "following": False,
            "followers_count": profile.followers_count,
            "posts_count": profile.posts_count
        })
    
    return {
        "success": True,
        "recommended": recommended_users
    }

@router.get("/profile")
async def get_my_profile(db: Session = Depends(get_db)):
    """내 프로필 조회"""
    user_id = get_current_user_id()
    profile = get_user_profile(db, user_id)
    
    return {
        "success": True,
        "profile": {
            "user_id": profile.user_id,
            "username": profile.username,
            "bio": profile.bio,
            "avatar": profile.avatar_text,
            "posts_count": profile.posts_count,
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "is_public": profile.is_public
        }
    }

def get_time_ago(dt: datetime) -> str:
    """시간 차이를 문자열로 변환"""
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "방금 전"
    elif seconds < 3600:
        return f"{int(seconds // 60)}분 전"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}시간 전"
    else:
        return f"{int(seconds // 86400)}일 전"