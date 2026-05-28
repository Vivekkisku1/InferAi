from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.usage import UsageHistoryResponse, UsageLogResponse
from app.services.usage_service import list_usage_logs

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("", response_model=UsageHistoryResponse)
async def get_usage_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    logs = await list_usage_logs(db, str(current_user.id), limit=limit, offset=offset)
    items = [UsageLogResponse.model_validate(log) for log in logs]
    return UsageHistoryResponse(
        items=items,
        limit=limit,
        offset=offset,
        count=len(items),
    )
