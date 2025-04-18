from pydantic import BaseModel


class CreatePost(BaseModel):
    description: str


class CommentPost(BaseModel):
    post_id: int
    comment_text: str
