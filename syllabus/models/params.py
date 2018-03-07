from sqlalchemy import Column, String, Integer

from syllabus.database import Base


class Params(Base):
    __tablename__ = 'params'
    id = Column(Integer(), primary_key=True)
    git_hook_url = Column(String(80))  # we need to define a primary key to use the ORM

    def __init__(self, git_hook_url=None):
        self.id = 0
        self.git_hook_url = git_hook_url

    def to_dict(self):
        return {"git_hook_url": self.git_hook_url}
