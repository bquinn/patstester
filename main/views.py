from django.shortcuts import render
from django.views.generic.list import ListView

from pats import PATSBuyer, PATSSeller

MEDIAOCEAN_AGENCY_API_KEY = 'yt6wsdwrauz7mrawha7rua8v'
AGENCY_ID = '35-IDSDKAD-7'
AGENCY_USER_ID = 'brenddlo@pats3'

TEST_COMPANY_ID = 'PATS3'
TEST_PERSON_ID = 'brenddlo'
PATS_PUBLISHER_ID = '35-EEBMG4J-4'

class PATSAPIMixin(object):
    pats_buyer = None
    pats_seller = None

    def get_buyer_api_handle(self):
        if not self.pats_buyer and 'api_handle_buyer' in self.request.session:
            self.pats_buyer = self.request.session['api_handle_buyer']
        else:
            self.pats_buyer = PATSBuyer(agency_id=AGENCY_ID, api_key=MEDIAOCEAN_AGENCY_API_KEY, debug_mode=True)
        return self.pats_buyer

    def get_seller_api_handle(self):
        if not self.pats_seller and self.request.session['api_handle_seller']:
            self.pats_seller = self.request.session['api_handle_seller']
        else:
            self.pats_seller = PATSSeller(agency_id=AGENCY_ID, api_key=MEDIAOCEAN_AGENCY_API_KEY, debug_mode=True)
        return self.pats_seller

class Buyer_GetPublishersView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        publishers_response = buyer_api.get_sellers(user_id=AGENCY_USER_ID)
        # publishers list is actually the "payload" component of the dict
        return publishers_response['payload']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublishersView, self).get_context_data(*args, **kwargs)
        return context_data

class Buyer_GetPublisherUsersView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        vendor_id = self.kwargs.get('publisher_id', None)
        publisher_users_response = buyer_api.get_users_for_seller(user_id=AGENCY_USER_ID, vendor_id=vendor_id)
        # publisher emails list is actually the "payload" component of the dict
        return publisher_users_response['payload']['emails']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublisherUsersView, self).get_context_data(*args, **kwargs)
        context_data['vendor_id'] = self.kwargs.get('publisher_id', None)
        return context_data
