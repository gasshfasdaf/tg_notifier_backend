from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

RepositoryType = TypeVar("RepositoryType")

class BaseService(Generic[RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository