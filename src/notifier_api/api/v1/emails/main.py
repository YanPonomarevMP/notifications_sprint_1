from fastapi import APIRouter, Depends
from utils.dependencies import authorization_required
from notifier_api.api.v1.emails.html_templates import router as html_templates_router


router = APIRouter(
    prefix='/emails',
    tags=['emails'],
    dependencies=[Depends(authorization_required)]
)

router.include_router(html_templates_router)