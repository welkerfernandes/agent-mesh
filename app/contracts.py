from typing import Literal
from pydantic import BaseModel,Field,model_validator

class Mission(BaseModel):
    objective: str=Field(min_length=5,max_length=2000)
    data_mode: Literal['demo','live']='demo'
    inference: Literal['demo','ollama']='demo'
    max_tool_calls: int=Field(default=3,ge=1,le=3)
    max_model_calls: int=Field(default=3,ge=1,le=5)

class Task(BaseModel):
    id: str=Field(pattern=r'^[a-z][a-z0-9_-]{0,30}$')
    tool: Literal['weather','economy','registry']
    question: str=Field(min_length=1,max_length=300)

class Plan(BaseModel):
    tasks: list[Task]=Field(min_length=1,max_length=3)

    @model_validator(mode='after')
    def unique(self):
        if len({t.id for t in self.tasks})!=len(self.tasks): raise ValueError('Duplicate task ids')
        return self

class Claim(BaseModel):
    text: str=Field(min_length=1,max_length=1000)
    evidence_ids: list[str]=Field(min_length=1,max_length=3)

class Report(BaseModel):
    summary: str=Field(min_length=1,max_length=2000)
    claims: list[Claim]=Field(min_length=1,max_length=10)
    limitations: list[str]=Field(min_length=1,max_length=8)

class Review(BaseModel):
    approved: bool
    reasons: list[str]=Field(max_length=8)
