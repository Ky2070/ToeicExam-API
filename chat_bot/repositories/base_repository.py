from abc import ABC, abstractmethod
from typing import List, Optional, Any
from django.db import models


class BaseRepository(ABC):
    """Abstract base repository class"""
    
    def __init__(self, model: models.Model):
        self.model = model

    def get_all(self) -> List[models.Model]:
        """Get all records"""
        return list(self.model.objects.all())

    def get_by_id(self, id: int) -> Optional[models.Model]:
        """Get record by ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs) -> models.Model:
        """Create a new record"""
        return self.model.objects.create(**kwargs)

    def update(self, instance: models.Model, **kwargs) -> models.Model:
        """Update an existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: models.Model) -> bool:
        """Delete a record"""
        try:
            instance.delete()
            return True
        except Exception:
            return False

    def filter(self, **kwargs) -> List[models.Model]:
        """Filter records by criteria"""
        return list(self.model.objects.filter(**kwargs))

    def exists(self, **kwargs) -> bool:
        """Check if record exists"""
        return self.model.objects.filter(**kwargs).exists()
