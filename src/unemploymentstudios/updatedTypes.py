from typing import List, Dict, Literal, Optional
from pydantic import BaseModel, Field

# ---------------------------------------
# 1. Core Game Conceptualization Models
# ---------------------------------------

class Character(BaseModel):
    name: str
    role: str  # e.g., Protagonist, Antagonist, Supporting
    description: str
    abilities: Optional[List[str]] = None
    emotional_arc: Optional[str] = None

class Level(BaseModel):
    name: str
    description: str
    difficulty: Literal["Easy", "Medium", "Hard", "Boss"]
    key_objectives: List[str]
    enemies_obstacles: List[str]
    boss_battle: Optional[str] = None

class GameConcept(BaseModel):
    title: str
    tagline: str
    overview: str
    main_character: Character
    supporting_characters: List[Character]
    world_building: str
    levels: List[Level]
    gameplay_mechanics: List[str]
    visual_style: str
    audio_style: str
    emotional_arc: str
    conclusion: str

# ---------------------------------------
# 2. Technical Planning Models
# ---------------------------------------

class FileSpec(BaseModel):
    filename: str
    purpose: str
    content_guidelines: str
    dependencies: Optional[List[str]] = Field(default_factory=list)

class FileStructureSpec(BaseModel):
    files: List[FileSpec]

# ---------------------------------------
# 3. File Development and Tracking Models
# ---------------------------------------

class GameFile(BaseModel):
    filename: str
    filetype: Literal["html", "css", "js", "audio", "json", "asset"]
    content: str
    responsible_crew: str  # e.g., "Core JavaScript Crew", "Audio Crew"
    status: Literal["draft", "under_review", "approved", "needs_revision"]
    revision_history: Optional[List[str]] = Field(default_factory=list)

# ---------------------------------------
# 4. Quality Assurance & Feedback Models
# ---------------------------------------

class ReviewerType(Literal["AI", "Technical QA", "Gameplay QA", "Human QA"]):
    pass

class QAFeedback(BaseModel):
    filename: str
    reviewer: str
    reviewer_type: ReviewerType
    status: Literal["passed", "correction_needed", "failed"]
    comments: Optional[str] = None
    suggestions: Optional[List[str]] = Field(default_factory=list)
    review_timestamp: Optional[str] = None

class FeedbackLoop(BaseModel):
    file: GameFile
    feedback_history: List[QAFeedback] = Field(default_factory=list)
    review_attempts: int = 0
    max_attempts: int = 3

# ---------------------------------------
# 5. Project Management Models
# ---------------------------------------

class CrewMember(BaseModel):
    name: str
    role: str
    specialization: Optional[str] = None

class Crew(BaseModel):
    name: str
    members: List[CrewMember]
    current_task: Optional[str] = None
    completed_tasks: Optional[List[str]] = Field(default_factory=list)

class ProjectTimelineEntry(BaseModel):
    phase: str
    tasks: List[str]
    assigned_crew: List[str]
    deadline: Optional[str] = None
    status: Literal["pending", "in_progress", "completed", "overdue"]

class ProjectTimeline(BaseModel):
    entries: List[ProjectTimelineEntry]

# ---------------------------------------
# 6. Project-Wide Knowledge Base Model
# ---------------------------------------

class KnowledgeBaseEntry(BaseModel):
    topic: str
    issue_description: str
    solution: Optional[str] = None
    references: Optional[List[str]] = Field(default_factory=list)

class KnowledgeBase(BaseModel):
    entries: List[KnowledgeBaseEntry]
