from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PostRawFront(BaseModel):
    title: str
    create_time: datetime
    update_time: datetime
    tags: str


class PostRaw(BaseModel):
    front: PostRawFront
    file_name: Optional[str] = None


class PostTemplateInfo(BaseModel):
    title: str
    create_time: datetime
    update_time: datetime
    tags: List[str]
    content: str


class PostTemplateTocItemH2(BaseModel):
    title: str
    id: str


class PostTemplateTocItem(BaseModel):
    title: str
    id: str
    h2s: List[PostTemplateTocItemH2]


class PostTemplate(BaseModel):
    post: PostTemplateInfo
    toc: List[PostTemplateTocItem]
