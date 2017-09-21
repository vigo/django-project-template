import logging

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models


__all__ = [
    'BaseModel',
    'BaseModelWithSoftDelete',
]


logger = logging.getLogger('user_logger')

class BaseModelQuerySet(models.QuerySet):
    """
    Common QuerySet for BaseModel and BaseModelWithSoftDelete. 
    Both querysets have:
    
    - `.deleted()`: Returns `status` = `STATUS_DELETED`
    - `.offlined()`: Returns `status` = `STATUS_OFFLINE`
    - `.drafted()`: Returns `status` = `STATUS_DRAFT`
    
    methods.
    
    """
    
    def deleted(self):
        return self.filter(
            status=BaseModelWithSoftDelete.STATUS_DELETED,
            deleted_at__isnull=False,
        )

    def offlined(self):
        return self.filter(
            status=BaseModelWithSoftDelete.STATUS_OFFLINE,
            deleted_at__isnull=True,
        )

    def drafted(self):
        return self.filter(
            status=BaseModelWithSoftDelete.STATUS_DRAFT,
            deleted_at__isnull=True,
        )


class BaseModelWithSoftDeleteQuerySet(BaseModelQuerySet):
    """
    Available methods are:
    
    - `.all()`: Mimics deleted records. Return only if the `deleted_at` value is NULL!
    - `.delete()`: Soft deletes give objects.
    - `.undelete()`: Recovers (sets `status` to `STATUS_ONLINE`) give objects.
    - `.deleted()`: Returns soft deleted objects.
    
    Also inherits from `BaseModelQuerySet`:
    
    - `.deleted()`: Returns `status` = `STATUS_DELETED`
    - `.offlined()`: Returns `status` = `STATUS_OFFLINE`
    - `.drafted()`: Returns `status` = `STATUS_DRAFT`

    """
    
    def _delete_or_undelete(self, undelete=False):
        processed_instances = {}
        call_method = 'undelete' if undelete else 'delete'

        for model_instance in self:
            _count, model_information = getattr(model_instance, call_method)()
            for app_label, row_amount in model_information.items():
                processed_instances.setdefault(app_label, 0)
                processed_instances[app_label] = processed_instances[app_label] + row_amount
        return (sum(processed_instances.values()), processed_instances)

    def all(self):
        return self.filter(deleted_at__isnull=True)

    def delete(self):
        return self._delete_or_undelete()

    def undelete(self):
        return self._delete_or_undelete(True)


class BaseModelWithSoftDeleteManager(models.Manager):
    """
    This is a manager for `BaseModelWithSoftDelete` instances.
    Do not forget! `.all()` will never return soft-deleted objects!
    """
    
    def get_queryset(self):
        return BaseModelWithSoftDeleteQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()

    def deleted(self):
        return self.get_queryset().deleted()

    def offlined(self):
        return self.get_queryset().offlined()

    def drafted(self):
        return self.get_queryset().drafted()

    def delete(self):
        return self.get_queryset().delete()

    def undelete(self):
        return self.get_queryset().undelete()


class BaseModel(models.Model):
    """
    Use this model for common functionality
    """

    STATUS_OFFLINE = 0
    STATUS_ONLINE = 1
    STATUS_DELETED = 2
    STATUS_DRAFT = 3

    STATUS_CHOICES = (
        (STATUS_OFFLINE, _('Offline')),
        (STATUS_ONLINE, _('Online')),
        (STATUS_DELETED, _('Deleted')),
        (STATUS_DRAFT, _('Draft')),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_ONLINE,
        verbose_name=_('Status'),
    )

    objects = models.Manager()
    objects_bm = BaseModelQuerySet.as_manager()

    class Meta:
        abstract = True


class BaseModelWithSoftDelete(BaseModel):
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted At'),
    )

    objects = models.Manager()
    objects_bm = BaseModelWithSoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        return self._delete_or_undelete()

    def undelete(self):
        return self._delete_or_undelete(True)

    def _delete_or_undelete(self, undelete=False):
        processed_instances = {}
        call_method = 'undelete' if undelete else 'delete'
        
        log_params = {
            'instance': self,
            'label': self._meta.label,
            'pk': self.pk,
        }
        log_message = '{action} on: "{instance} - pk: {pk}" [{label}]'

        if call_method == 'delete':
            models.signals.pre_delete.send(sender=self.__class__, instance=self,)
            status_value = self.STATUS_DELETED
            deleted_at_value = timezone.now()
            log_params.update(action='Soft-delete')
            logger.warning(log_message.format(**log_params))
        else:
            status_value = self.STATUS_ONLINE
            deleted_at_value = None
            log_params.update(action='Un-delete')
            logger.warning(log_message.format(**log_params))

        self.status = status_value
        self.deleted_at = deleted_at_value
        self.save()

        if call_method == 'delete':
            models.signals.post_delete.send(sender=self.__class__, instance=self,)

        processed_instances.update({self._meta.label: 1})

        for related_object in self._meta.related_objects:
            if hasattr(related_object, 'on_delete') and getattr(related_object, 'on_delete') == models.CASCADE:
                accessor_name = related_object.get_accessor_name()
                related_model_instances = getattr(self, accessor_name)
                related_model_instance_count = 0
                for related_model_instance in related_model_instances.all():
                    getattr(related_model_instance, call_method)()
                    processed_instances.setdefault(related_model_instance._meta.label, related_model_instance_count)
                    related_model_instance_count += 1
                    processed_instances.update({related_model_instance._meta.label: related_model_instance_count})
        return (sum(processed_instances.values()), processed_instances)
