from django.db import models
from django.utils.translation import ugettext_lazy as _

class PATSEvent(models.Model):
    """
    Order event notification from the Push API looks like

    [
        {
            'subscriptionType': 'Order',
            'eventType': 'Expired',
            'entityId': 'O-1MV6',
            'attributes': {
                'majorVersion': '4'
            },
            'eventDateInMillis': 1459224022554
        }
    ]
    Note that this is different from the docs: logged as PATS-1157.
    """

    entity_id = models.CharField(_('entity ID'), max_length=15, blank=True)
    event_date = models.DateTimeField(_('event date'), blank=True)
    subscription_type = models.CharField(_('subscription type'), max_length=30, blank=True)
    event_type = models.CharField(_('event type'), max_length=30, blank=True)
    major_version = models.CharField(_('major version'), max_length=5, blank=True)
    minor_version = models.CharField(_('minor version'), max_length=5, blank=True)

    # auto-track when this object was created
    created_date = models.DateTimeField(auto_now_add=True)

    # auto-track when this object was last updated
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return "PATS Event: %s %s %s.%s %s at %s" % (
                self.subscription_type, self.entity_id,
                self.major_version, self.minor_version,
                self.event_type, self.event_date
            )
