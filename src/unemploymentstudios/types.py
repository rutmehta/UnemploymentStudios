from typing import List, Dict, Literal
from pydantic import BaseModel

class GameConcept(BaseModel):
    title: str
    tagline: str
    overview: str
    main_character: str
    supporting_characters: List[Dict[str, str]] 
    world_building: str
    levels: List[Dict[str, str]]
    enemies_and_obstacles: str
    gameplay_mechanics: str
    boss_battles: str
    emotional_arc: str
    conclusion: str
    visual_style: str
    audio_style: str

class FileSpec(BaseModel):
    filename: str
    purpose: str
    contentGuidelines: str

class FileStructureSpec(BaseModel):
    files: List[FileSpec]

class GameFile(BaseModel):
    filename: str
    filetype: Literal["html", "css", "js", "audio"]
    content: str
    status: Literal["draft", "under_review", "approved", "needs_revision"]

class QAFeedback(BaseModel):
    filename: str
    reviewer: str
    status: Literal["passed", "correction_needed", "failed"]
    comments: str
