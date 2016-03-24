from django.db import models
from django.utils.translation import ugettext_lazy as _

class PATSEvent(models.Model):
    """
    Order event notification from the Push API looks like

  {
    "entityId" : "O-XXXX",
    "eventDateInMillis" : 1438424445000,
    "entityType" : "Order",
    "subscriptionType" : "Sent",
    "attributes" : {
      "majorVersion" : "0",
      "minorVersion" : "1"
    }
  },
    """

    entity_id = models.CharField(_('entity ID'), max_length=15, blank=True)
    event_date = models.DateTimeField(_('event date'), blank=True)
    entity_type = models.CharField(_('entity type'), max_length=30, blank=True)
    subscription_type = models.CharField(_('entity type'), max_length=30, blank=True)
    major_version = models.CharField(_('major version'), max_length=5, blank=True)
    minor_version = models.CharField(_('minor version'), max_length=5, blank=True)

    # auto-track when this object was created
    created_date = models.DateTimeField(auto_now_add=True)

    # auto-track when this object was last updated
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return "PATS Event: %s %s %s.%s %s at %s" % (
                self.entity_type, self.entity_id,
                self.major_version, self.minor_version,
                self.subscription_type, self.event_date
            )
