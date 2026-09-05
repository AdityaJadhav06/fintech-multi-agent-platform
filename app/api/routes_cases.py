import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import AuthenticatedUser, get_current_user, AuditLogger, verify_tenant_access
from app.db import Case, Document, get_db, vector_store
from app.schemas import CaseCreate, CaseResponse, DocumentResponse

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new multi-agent analysis case.
    """
    new_case = Case(
        org_id=user.org_id,
        created_by=user.user_id,
        title=payload.title,
        master_question=payload.master_question,
        business_context=payload.business_context or "",
        constraints_json=payload.constraints,
        status="CREATED",
    )
    db.add(new_case)
    await db.flush()

    await AuditLogger.log_event(
        db=db,
        org_id=user.org_id,
        user_id=user.user_id,
        case_id=new_case.id,
        action="CASE_CREATED",
        resource_type="Case",
        resource_id=new_case.id,
        details={"title": payload.title, "master_question": payload.master_question},
    )

    return new_case


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all cases belonging to the authenticated tenant.
    """
    stmt = select(Case).where(Case.org_id == user.org_id).order_by(Case.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves case details by ID with tenant security check.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)
    return case


@router.post("/{case_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a document, extracts text, chunks it, and indexes it into the vector store.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)

    # Read content
    content_bytes = await file.read()
    text_content = content_bytes.decode("utf-8", errors="ignore")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_path = os.path.join(settings.UPLOAD_DIR, f"{case_id}_{file.filename}")
    with open(saved_path, "wb") as f:
        f.write(content_bytes)

    doc = Document(
        case_id=case_id,
        filename=file.filename,
        file_type=file.filename.split(".")[-1] if "." in file.filename else "txt",
        file_size=len(content_bytes),
        storage_path=saved_path,
        uploaded_by=user.user_id,
    )
    db.add(doc)
    await db.flush()

    # Index into vector store for RAG
    vector_store.add_document(
        document_id=doc.id,
        filename=file.filename,
        text_content=text_content,
    )

    await AuditLogger.log_event(
        db=db,
        org_id=user.org_id,
        user_id=user.user_id,
        case_id=case_id,
        action="DOCUMENT_UPLOADED",
        resource_type="Document",
        resource_id=doc.id,
        details={"filename": file.filename, "size_bytes": len(content_bytes)},
    )

    return doc


@router.get("/{case_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all documents attached to a case.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)

    doc_stmt = select(Document).where(Document.case_id == case_id)
    doc_res = await db.execute(doc_stmt)
    return doc_res.scalars().all()
