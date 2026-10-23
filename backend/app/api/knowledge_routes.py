import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.knowledge_models import KnowledgeArticleModel
from app.models.security_models import AuditLogModel

router = APIRouter(prefix="/knowledge", tags=["Portal 8: Knowledge Base"])

class ArticlePayload(BaseModel):
    title: str
    category: str = "troubleshooting"  # troubleshooting, sop, playbook, postmortem, faq
    summary: str
    content: str
    service_id: Optional[str] = None
    tags: Optional[List[str]] = []
    author: Optional[str] = "CascadeShield Reliability Team"
    actor_id: Optional[str] = "usr-admin-01"

@router.get("")
def list_knowledge_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    service_id: Optional[str] = Query(None, description="Filter by service"),
    q: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeArticleModel)
    if category:
        query = query.filter(KnowledgeArticleModel.category == category.lower())
    if service_id:
        query = query.filter(KnowledgeArticleModel.service_id == service_id)
    if q:
        query = query.filter(
            KnowledgeArticleModel.title.ilike(f"%{q}%") |
            KnowledgeArticleModel.summary.ilike(f"%{q}%") |
            KnowledgeArticleModel.content.ilike(f"%{q}%")
        )

    articles = query.order_by(KnowledgeArticleModel.updated_at.desc()).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "summary": a.summary,
            "service_id": a.service_id,
            "tags": json.loads(a.tags_json) if a.tags_json and a.tags_json.startswith("[") else [],
            "author": a.author,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        } for a in articles
    ]

@router.get("/{article_id}")
def get_article(article_id: str, db: Session = Depends(get_db)):
    a = db.query(KnowledgeArticleModel).filter(KnowledgeArticleModel.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Knowledge article not found")

    return {
        "id": a.id,
        "title": a.title,
        "category": a.category,
        "summary": a.summary,
        "content": a.content,
        "service_id": a.service_id,
        "tags": json.loads(a.tags_json) if a.tags_json and a.tags_json.startswith("[") else [],
        "author": a.author,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None
    }

@router.post("")
def create_article(payload: ArticlePayload, db: Session = Depends(get_db)):
    article = KnowledgeArticleModel(
        title=payload.title,
        category=payload.category.lower(),
        summary=payload.summary,
        content=payload.content,
        service_id=payload.service_id,
        tags_json=json.dumps(payload.tags or []),
        author=payload.author or "CascadeShield Reliability Team"
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # Log audit event
    audit = AuditLogModel(
        actor_id=payload.actor_id or "usr-admin-01",
        actor_name="Sarah Connor",
        actor_role="Administrator",
        action="KNOWLEDGE_CREATE",
        resource_type="knowledge_article",
        resource_id=article.id,
        status="SUCCESS",
        details_json=json.dumps({"title": article.title, "category": article.category})
    )
    db.add(audit)
    db.commit()

    return {"message": "Knowledge article created successfully", "article_id": article.id}

@router.put("/{article_id}")
def update_article(article_id: str, payload: ArticlePayload, db: Session = Depends(get_db)):
    a = db.query(KnowledgeArticleModel).filter(KnowledgeArticleModel.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")

    a.title = payload.title
    a.category = payload.category.lower()
    a.summary = payload.summary
    a.content = payload.content
    a.service_id = payload.service_id
    a.tags_json = json.dumps(payload.tags or [])
    a.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Article updated successfully", "article_id": a.id}

@router.delete("/{article_id}")
def delete_article(article_id: str, db: Session = Depends(get_db)):
    a = db.query(KnowledgeArticleModel).filter(KnowledgeArticleModel.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(a)
    db.commit()
    return {"message": "Knowledge article removed"}
