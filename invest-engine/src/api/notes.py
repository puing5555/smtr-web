"""
Notes API Router - 노트 (메모+스크랩) 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from src.db.database import get_db
from src.db.models import Note, NoteFolder, Stock, SNSPost, UserProfile
from pydantic import BaseModel

router = APIRouter(prefix="/api/notes", tags=["notes"])

# Pydantic Models
class NoteCreate(BaseModel):
    note_type: str  # memo, scrap, news, filing
    title: str
    content: str
    url: Optional[str] = None
    source_title: Optional[str] = None
    source_description: Optional[str] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[List[str]] = None
    is_bookmarked: bool = False
    is_public: bool = False
    importance: int = 0
    source_id: Optional[str] = None
    source_type: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[List[str]] = None
    is_bookmarked: Optional[bool] = None
    is_public: Optional[bool] = None
    importance: Optional[int] = None

class NoteFolderCreate(BaseModel):
    folder_name: str
    folder_type: str  # memo, scrap, mixed
    color: str = "#667eea"
    is_default: bool = False

class SNSShareRequest(BaseModel):
    note_id: int
    content: Optional[str] = None
    stock_tags: Optional[List[str]] = None


# Helper functions
def get_current_user_id() -> str:
    # TODO: 실제 인증 시스템 연동
    return "user_me"

def update_folder_count(db: Session, user_id: str, folder_name: str):
    """폴더 내 노트 개수 업데이트"""
    if not folder_name:
        return
        
    folder = db.query(NoteFolder).filter(
        NoteFolder.user_id == user_id,
        NoteFolder.folder_name == folder_name
    ).first()
    
    if folder:
        count = db.query(Note).filter(
            Note.user_id == user_id,
            Note.folder == folder_name
        ).count()
        folder.note_count = count
        db.commit()

def ensure_default_folders(db: Session, user_id: str):
    """기본 폴더들이 없으면 생성"""
    default_folders = [
        {"name": "투자아이디어", "type": "memo", "color": "#667eea"},
        {"name": "종목분석", "type": "memo", "color": "#10b981"},
        {"name": "외부링크", "type": "scrap", "color": "#f59e0b"},
        {"name": "뉴스", "type": "scrap", "color": "#dc2626"},
        {"name": "공시", "type": "scrap", "color": "#3b82f6"},
    ]
    
    for folder_data in default_folders:
        existing = db.query(NoteFolder).filter(
            NoteFolder.user_id == user_id,
            NoteFolder.folder_name == folder_data["name"]
        ).first()
        
        if not existing:
            folder = NoteFolder(
                user_id=user_id,
                folder_name=folder_data["name"],
                folder_type=folder_data["type"],
                color=folder_data["color"],
                is_default=True
            )
            db.add(folder)
    
    db.commit()


# API Endpoints
@router.get("/")
async def get_notes(
    db: Session = Depends(get_db),
    note_type: Optional[str] = Query(None, description="all, memo, scrap, news, filing"),
    folder: Optional[str] = Query(None, description="폴더명"),
    search: Optional[str] = Query(None, description="검색어"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("newest", description="newest, oldest")
):
    """노트 목록 조회"""
    user_id = get_current_user_id()
    
    # 기본 폴더 확인/생성
    ensure_default_folders(db, user_id)
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(Note).filter(Note.user_id == user_id)
    
    # Apply filters
    if note_type and note_type != "all":
        query = query.filter(Note.note_type == note_type)
    
    if folder:
        query = query.filter(Note.folder == folder)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Note.title.ilike(search_filter)) |
            (Note.content.ilike(search_filter)) |
            (Note.stock_name.ilike(search_filter))
        )
    
    # Sort
    if sort == "oldest":
        query = query.order_by(Note.created_at.asc())
    else:
        query = query.order_by(Note.created_at.desc())
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    notes = query.offset(offset).limit(limit).all()
    
    # Format response
    formatted_notes = []
    for note in notes:
        formatted_note = {
            "id": note.id,
            "note_type": note.note_type,
            "title": note.title,
            "content": note.content,
            "url": note.url,
            "source_title": note.source_title,
            "source_description": note.source_description,
            "stock_code": note.stock_code,
            "stock_name": note.stock_name,
            "folder": note.folder,
            "tags": note.tags or [],
            "is_bookmarked": note.is_bookmarked,
            "is_public": note.is_public,
            "importance": note.importance,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
        formatted_notes.append(formatted_note)
    
    return {
        "success": True,
        "notes": formatted_notes,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit,
            "has_next": page * limit < total_count,
            "has_prev": page > 1
        }
    }

@router.post("/")
async def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """새 노트 생성"""
    user_id = get_current_user_id()
    
    # 종목 코드가 있는 경우 종목명 자동 조회
    stock_name = note_data.stock_name
    if note_data.stock_code and not stock_name:
        stock = db.query(Stock).filter(Stock.stock_code == note_data.stock_code).first()
        if stock:
            stock_name = stock.corp_name
    
    # 노트 생성
    note = Note(
        user_id=user_id,
        note_type=note_data.note_type,
        title=note_data.title,
        content=note_data.content,
        url=note_data.url,
        source_title=note_data.source_title,
        source_description=note_data.source_description,
        stock_code=note_data.stock_code,
        stock_name=stock_name,
        folder=note_data.folder,
        tags=note_data.tags,
        is_bookmarked=note_data.is_bookmarked,
        is_public=note_data.is_public,
        importance=note_data.importance,
        source_id=note_data.source_id,
        source_type=note_data.source_type
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # 폴더 카운트 업데이트
    update_folder_count(db, user_id, note_data.folder)
    
    return {
        "success": True,
        "message": "노트가 생성되었습니다",
        "note_id": note.id
    }

@router.get("/{note_id}")
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """노트 상세 조회"""
    user_id = get_current_user_id()
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다")
    
    return {
        "success": True,
        "note": {
            "id": note.id,
            "note_type": note.note_type,
            "title": note.title,
            "content": note.content,
            "url": note.url,
            "source_title": note.source_title,
            "source_description": note.source_description,
            "stock_code": note.stock_code,
            "stock_name": note.stock_name,
            "folder": note.folder,
            "tags": note.tags or [],
            "is_bookmarked": note.is_bookmarked,
            "is_public": note.is_public,
            "importance": note.importance,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }

@router.put("/{note_id}")
async def update_note(note_id: int, note_data: NoteUpdate, db: Session = Depends(get_db)):
    """노트 수정"""
    user_id = get_current_user_id()
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다")
    
    # 이전 폴더명 저장
    old_folder = note.folder
    
    # 업데이트
    update_data = note_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    note.updated_at = datetime.now()
    db.commit()
    
    # 폴더가 변경된 경우 카운트 업데이트
    if old_folder != note.folder:
        update_folder_count(db, user_id, old_folder)
        update_folder_count(db, user_id, note.folder)
    
    return {
        "success": True,
        "message": "노트가 수정되었습니다"
    }

@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """노트 삭제"""
    user_id = get_current_user_id()
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다")
    
    folder_name = note.folder
    db.delete(note)
    db.commit()
    
    # 폴더 카운트 업데이트
    update_folder_count(db, user_id, folder_name)
    
    return {
        "success": True,
        "message": "노트가 삭제되었습니다"
    }

@router.post("/bookmark-timeline-item")
async def bookmark_timeline_item(
    item_id: str,
    item_type: str,  # filing, news
    title: str,
    url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """타임라인 아이템을 노트로 북마크"""
    user_id = get_current_user_id()
    
    # 이미 북마크된 항목인지 확인
    existing = db.query(Note).filter(
        Note.user_id == user_id,
        Note.source_id == item_id,
        Note.source_type == item_type
    ).first()
    
    if existing:
        return {
            "success": True,
            "message": "이미 북마크된 항목입니다",
            "note_id": existing.id
        }
    
    # 폴더 설정
    folder = "공시" if item_type == "filing" else "뉴스"
    
    # 노트 생성
    note = Note(
        user_id=user_id,
        note_type=item_type,
        title=title,
        content="타임라인에서 북마크함",
        url=url,
        folder=folder,
        tags=[],
        is_bookmarked=True,
        source_id=item_id,
        source_type=item_type
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # 폴더 카운트 업데이트
    update_folder_count(db, user_id, folder)
    
    return {
        "success": True,
        "message": "노트에 저장되었습니다",
        "note_id": note.id
    }

@router.post("/{note_id}/share-to-sns")
async def share_note_to_sns(
    note_id: int,
    share_data: SNSShareRequest,
    db: Session = Depends(get_db)
):
    """노트를 SNS에 공유"""
    user_id = get_current_user_id()
    
    # 노트 조회
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다")
    
    # 사용자 프로필 조회
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        # 기본 프로필 생성
        profile = UserProfile(
            user_id=user_id,
            username="김투자",
            avatar_text="김"
        )
        db.add(profile)
        db.commit()
    
    # SNS 포스트 생성
    post_content = share_data.content or note.content
    
    # 스크랩 공유인 경우
    is_scrap_share = note.note_type in ['scrap', 'news', 'filing']
    
    sns_post = SNSPost(
        user_id=user_id,
        author_name=profile.username,
        content=post_content,
        is_scrap_share=is_scrap_share,
        note_id=note_id,
        stock_tags=share_data.stock_tags or ([note.stock_name] if note.stock_name else []),
        is_public=True
    )
    
    db.add(sns_post)
    db.commit()
    
    # 노트를 공개로 설정
    note.is_public = True
    db.commit()
    
    return {
        "success": True,
        "message": "SNS에 공유되었습니다",
        "post_id": sns_post.id
    }

@router.get("/folders/")
async def get_folders(db: Session = Depends(get_db)):
    """사용자 폴더 목록 조회"""
    user_id = get_current_user_id()
    
    # 기본 폴더 확인/생성
    ensure_default_folders(db, user_id)
    
    folders = db.query(NoteFolder).filter(
        NoteFolder.user_id == user_id
    ).order_by(NoteFolder.is_default.desc(), NoteFolder.folder_name.asc()).all()
    
    return {
        "success": True,
        "folders": [
            {
                "id": folder.id,
                "folder_name": folder.folder_name,
                "folder_type": folder.folder_type,
                "color": folder.color,
                "note_count": folder.note_count,
                "is_default": folder.is_default,
                "created_at": folder.created_at.isoformat()
            }
            for folder in folders
        ]
    }

@router.post("/folders/")
async def create_folder(folder_data: NoteFolderCreate, db: Session = Depends(get_db)):
    """새 폴더 생성"""
    user_id = get_current_user_id()
    
    # 중복 확인
    existing = db.query(NoteFolder).filter(
        NoteFolder.user_id == user_id,
        NoteFolder.folder_name == folder_data.folder_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="같은 이름의 폴더가 이미 있습니다")
    
    folder = NoteFolder(
        user_id=user_id,
        folder_name=folder_data.folder_name,
        folder_type=folder_data.folder_type,
        color=folder_data.color,
        is_default=folder_data.is_default
    )
    
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    return {
        "success": True,
        "message": "폴더가 생성되었습니다",
        "folder_id": folder.id
    }

@router.get("/stocks/search")
async def search_stocks(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """종목 검색"""
    query = f"%{q}%"
    
    stocks = db.query(Stock).filter(
        (Stock.corp_name.ilike(query)) |
        (Stock.stock_code.ilike(query))
    ).filter(Stock.is_active == True).limit(10).all()
    
    return {
        "success": True,
        "stocks": [
            {
                "stock_code": stock.stock_code,
                "corp_name": stock.corp_name,
                "market": stock.market
            }
            for stock in stocks
        ]
    }