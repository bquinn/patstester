from django.contrib import admin

# Register your models here.
from .models import PATSEvent

class PATSEventAdmin(admin.ModelAdmin):
    """ PATS event (accept/decline order, expired order, revision requested, revision sent etc) """
    model = PATSEvent
    list_display = ('__str__', 'entity_id', 'entity_type', 'subscription_type', 'updated_date')

#class NewsFixedUserAdmin(admin.ModelAdmin):
#    list_filter = ('account_status', 'is_approved', 'is_staff', 'is_public', 'commissioner_role', 'commissioner_type', 'contributor_role', 'current_country')
#    search_fields = ['first_name', 'last_name', 'email']
#    list_display = ['email', 'first_name', 'last_name', 'last_login',
#        'is_public', 'is_approved', 'is_active', 'portfolio_items', 'account_status']
#    inlines = [UserPhoneNumberInline, UserLanguageInline,
#        UserCountryInline, UserAccountInline, UserAwardInline, UserBookInline,
#        UserFeedInline, UserPortfolioItemInline, UserLicenceInline,
#        UserTrainingInline]
#    form = UserAdminForm
#    readonly_fields = (
#        'date_joined', 'updated', 'last_mailchimp_sync', 'last_twitter_sync', 'editorial_notes_updated', 'account_status'
#    )
#    filter_horizontal = ('commission_type', 'equipment', 'affiliation')
#    fieldsets = (
#        (None, {
#            'fields': (
#                'first_name', 'last_name', 'strapline', 'bio', 'date_joined', 'account_status',
#                'editorial_notes', 'editorial_notes_updated'
#            ),
#        }),


admin.site.register(PATSEvent, PATSEventAdmin)
