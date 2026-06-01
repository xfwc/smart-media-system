from pydantic import BaseModel


class PlanIntentInput(BaseModel):
    angle: str | None = None
    audience: str | None = None
    style: str | None = None


class PlanGenerateRequest(BaseModel):
    topic_id: int
    intent: PlanIntentInput | None = None
    template_id: int | None = None


class PlanStatusResponse(BaseModel):
    plan_id: int
    status: str
    message: str = ""


class TitleSuggestion(BaseModel):
    title: str
    style: str = ""


class Outline(BaseModel):
    hook: str = ""
    step1: str = ""
    step2: str = ""
    step3: str = ""
    step4: str = ""


class Advice(BaseModel):
    shooting: str | None = None
    publishing: str | None = None
    tags: list[str] = []


class PlanData(BaseModel):
    title_suggestions: list[TitleSuggestion] = []
    outline: Outline | None = None
    advice: Advice | None = None
    risk_warning: str | None = None


class PlanDetailResponse(BaseModel):
    plan_id: int
    status: str
    data: PlanData | None = None
    generated_at: str | None = None


class TemplateItem(BaseModel):
    id: int
    name: str
    description: str | None = None
    style_tags: list[str] = []
