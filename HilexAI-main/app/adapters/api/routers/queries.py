from fastapi import APIRouter, Depends, HTTPException
from ....schemas import (
    QueryCreateRequest, QueryUpdateRequest, QueryResponse,
)
from ....domain.entities import Query
from ....domain.ports import QueryRepositoryPort
from ....config import get_query_repo


router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=QueryResponse)
async def create_query(
    payload: QueryCreateRequest,
    repo: QueryRepositoryPort = Depends(get_query_repo),
):
    q = Query(
        id=None,
        name=payload.name,
        search_text=payload.search_text,
        filters=payload.filters,
        schedule_interval=payload.schedule_interval,
        is_active=payload.is_active,
    )
    saved = await repo.save(q)
    return QueryResponse(**saved.__dict__)


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(query_id: int, repo: QueryRepositoryPort = Depends(get_query_repo)):
    q = await repo.get_by_id(query_id)
    if not q:
        raise HTTPException(status_code=404, detail="Query not found")
    return QueryResponse(**q.__dict__)


@router.get("", response_model=list[QueryResponse])
async def list_active(repo: QueryRepositoryPort = Depends(get_query_repo)):
    items = await repo.list_active()
    return [QueryResponse(**q.__dict__) for q in items]


@router.patch("/{query_id}", response_model=QueryResponse)
async def update_query(query_id: int, payload: QueryUpdateRequest, repo: QueryRepositoryPort = Depends(get_query_repo)):
    current = await repo.get_by_id(query_id)
    if not current:
        raise HTTPException(status_code=404, detail="Query not found")
    updated = Query(
        id=query_id,
        name=payload.name or current.name,
        search_text=payload.search_text or current.search_text,
        filters=payload.filters if payload.filters is not None else current.filters,
        schedule_interval=payload.schedule_interval if payload.schedule_interval is not None else current.schedule_interval,
        is_active=payload.is_active if payload.is_active is not None else current.is_active,
        created_at=current.created_at,
        last_run_at=current.last_run_at,
    )
    saved = await repo.save(updated)
    return QueryResponse(**saved.__dict__)


@router.delete("/{query_id}")
async def delete_query(query_id: int, repo: QueryRepositoryPort = Depends(get_query_repo)):
    ok = await repo.delete(query_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"deleted": True}

