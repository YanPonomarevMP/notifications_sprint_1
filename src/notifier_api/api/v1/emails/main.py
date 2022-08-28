from fastapi import APIRouter, Depends
from utils.dependencies import authorization_required
from notifier_api.api.v1.emails.html_templates import router as html_templates_router
from notifier_api.api.v1.emails.single_emails import router as single_emails_router
from notifier_api.api.v1.emails.group_emails import router as group_emails_router

router = APIRouter(
    prefix='/emails',
    tags=['emails']
)

router.include_router(html_templates_router)
router.include_router(single_emails_router)
router.include_router(group_emails_router)