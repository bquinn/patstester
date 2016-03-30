from django.contrib import admin

# Register your models here.
from .models import PATSEvent

class PATSEventAdmin(admin.ModelAdmin):
    """ PATS event (accept/decline order, expired order, revision requested, revision sent etc) """
    model = PATSEvent
    list_display = ('__str__', 'entity_id', 'subscription_type', 'event_type', 'updated_date')

admin.site.register(PATSEvent, PATSEventAdmin)
