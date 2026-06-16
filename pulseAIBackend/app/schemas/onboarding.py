from pydantic import BaseModel
from typing import List, Optional


class OnboardingStepResponse(BaseModel):
    id: str
    label: str
    status: str
    detail: str
    due_label: Optional[str] = None


class OnboardingPathStep(BaseModel):
    id: str
    label: str
    status: str


class OnboardingResource(BaseModel):
    label: str
    type: str


class OnboardingContact(BaseModel):
    name: str
    role: str
    initials: str
    color: str
    main: bool = False


class OnboardingOverviewResponse(BaseModel):
    progress_percent: int
    completed_steps: int
    total_steps: int
    title: str
    subtitle: str
    path: List[OnboardingPathStep]
    tasks: List[OnboardingStepResponse]
    resources: List[OnboardingResource]
    contacts: List[OnboardingContact]
