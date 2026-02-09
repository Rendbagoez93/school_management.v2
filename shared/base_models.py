from django.db import models
from django.utils import timezone


class SoftDeletableManager(models.Manager):
    """Custom manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that includes soft-deleted objects."""
    
    def get_queryset(self):
        return super().get_queryset()


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides
    self-updating 'created' and 'modified' fields.
    """

    created = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    class Meta:
        abstract = True
        ordering = ["-created"]
        indexes = [models.Index(fields=["created"])]


class SoftDeletableModel(models.Model):
    """
    Abstract base model that provides a soft delete functionality.
    """

    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted At")

    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
        ordering = ["-deleted_at"]


class BaseSoftDeletableModel(TimeStampedModel, SoftDeletableModel):
    """
    Abstract base model that combines timestamping and soft deletion.
    """

    class Meta:
        abstract = True
        ordering = ["-created", "-modified"]
