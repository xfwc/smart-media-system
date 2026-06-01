from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.models.plan import ContentPlan, PlanIntent, PlanOutput, PlanTemplate
from app.models.hot import HotTopic
from app.schemas.plan import (
    PlanGenerateRequest, PlanStatusResponse, PlanDetailResponse,
    PlanData, TitleSuggestion, Outline, Advice, TemplateItem,
)
from app.schemas.common import ApiResponse

router = APIRouter()


@router.post("/plan/generate", status_code=202)
async def generate_plan(
    req: PlanGenerateRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    # Verify topic exists
    topic_result = await session.execute(select(HotTopic).where(HotTopic.id == req.topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        return ApiResponse(code=400, message="热点不存在"), 400

    plan = ContentPlan(
        user_id=user_id, topic_id=req.topic_id, template_id=req.template_id,
        status="processing",
    )
    session.add(plan)
    await session.flush()

    if req.intent:
        intent = PlanIntent(
            plan_id=plan.id,
            angle=req.intent.angle,
            audience=req.intent.audience,
            style=req.intent.style,
        )
        session.add(intent)

    # Generate plan content (simplified: template-based)
    title_suggestions = [
        {"title": f"深度解读：{topic.title}", "style": "深度分析"},
        {"title": f"关于{topic.title}，你必须知道的3件事", "style": "数字式"},
        {"title": f"{topic.title}背后，我们看到了什么？", "style": "疑问式"},
    ]
    outline = {
        "hook": f"你听说了吗？{topic.title}正在刷屏！",
        "step1": "这个热点是怎么回事？先讲清楚来龙去脉",
        "step2": "背后的3个关键点，逐一分析",
        "step3": "对我们普通人有什么影响？",
        "step4": "评论区聊聊你的看法！欢迎点赞转发",
    }
    advice = {
        "shooting": "建议使用真实场景拍摄，增加画面冲击力；可用数据图表辅助说明",
        "publishing": "建议在工作日晚上8-10点发布，配合热点话题标签",
        "tags": [topic.category or "热点", "短视频创作", "内容分析"],
    }

    output = PlanOutput(
        plan_id=plan.id,
        title_suggestions=title_suggestions,
        outline=outline,
        shooting_advice=advice.get("shooting"),
        publish_advice=advice.get("publishing"),
        recommended_tags=advice.get("tags"),
        risk_warning=f"注意：此话题风险等级为{getattr(topic.analysis, 'risk_level', 'low') if hasattr(topic, 'analysis') and topic.analysis else 'low'}，请确保内容客观公正",
    )
    session.add(output)

    plan.status = "completed"
    plan.generated_at = datetime.utcnow()

    return PlanStatusResponse(plan_id=plan.id, status="processing", message="企划生成中，请稍候...")


@router.get("/plan/{plan_id}/status")
async def get_plan_status(
    plan_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(ContentPlan).where(ContentPlan.id == plan_id, ContentPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return {"detail": "企划不存在"}, 404

    data = None
    if plan.status.value == "completed":
        output_result = await session.execute(
            select(PlanOutput).where(PlanOutput.plan_id == plan_id)
        )
        output = output_result.scalar_one_or_none()
        if output:
            data = PlanData(
                title_suggestions=[TitleSuggestion(**t) for t in (output.title_suggestions or [])],
                outline=Outline(**output.outline) if output.outline else None,
                advice=Advice(
                    shooting=output.shooting_advice,
                    publishing=output.publish_advice,
                    tags=output.recommended_tags if isinstance(output.recommended_tags, list) else [],
                ),
                risk_warning=output.risk_warning,
            )

    return PlanDetailResponse(
        plan_id=plan.id, status=plan.status.value, data=data,
        generated_at=plan.generated_at.isoformat() if plan.generated_at else None,
    )


@router.get("/plan/history")
async def get_plan_history(
    page: int = Query(1), page_size: int = Query(10),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(ContentPlan).where(ContentPlan.user_id == user_id)
        .order_by(ContentPlan.created_at.desc())
    )
    plans = result.scalars().all()
    items = []
    for p in plans:
        topic_result = await session.execute(select(HotTopic).where(HotTopic.id == p.topic_id))
        topic = topic_result.scalar_one_or_none()
        items.append({
            "id": p.id, "topic_title": topic.title if topic else "",
            "status": p.status.value, "generated_at": p.generated_at.isoformat() if p.generated_at else None,
        })
    return {"total": len(items), "items": items}


@router.get("/plan/templates")
async def get_templates(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(PlanTemplate).where(PlanTemplate.is_active == True)
    )
    templates = result.scalars().all()
    return {
        "templates": [
            TemplateItem(
                id=t.id, name=t.name, description=t.description,
                style_tags=t.style_tags if isinstance(t.style_tags, list) else [],
            )
            for t in templates
        ]
    }
