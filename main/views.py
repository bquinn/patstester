import datetime
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import FormView

from pats import PATSBuyer, PATSSeller
from .forms import Buyer_SendOrderForm

# buy side
MEDIAOCEAN_AGENCY_API_KEY = 'yt6wsdwrauz7mrawha7rua8v'
AGENCY_ID = '35-IDSDKAD-7'
AGENCY_USER_ID = 'brenddlo@pats3'
TEST_COMPANY_ID = 'PATS3'
TEST_PERSON_ID = 'brenddlo'
# sell side
MEDIAOCEAN_PUBLISHER_API_KEY = 'nz5ta424wv8m2bmg4njbgwya'
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
        if not self.pats_seller and 'api_handle_seller' in self.request.session:
            self.pats_seller = self.request.session['api_handle_seller']
        else:
            self.pats_seller = PATSSeller(vendor_id=PATS_PUBLISHER_ID, api_key=MEDIAOCEAN_PUBLISHER_API_KEY, debug_mode=True)
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

class Buyer_SendOrderView(PATSAPIMixin, FormView):
    form_class = Buyer_SendOrderForm

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_SendOrderView, self).get_context_data(*args, **kwargs)
        return context_data

class Buyer_ListOrderRevisionsView(PATSAPIMixin, ListView):
    start_date = None
    end_date = None

    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        vendor_id = self.kwargs.get('publisher_id', None)
        self.start_date = self.request.GET.get('start_date', None)
        if not self.start_date:
            one_month_ago = datetime.datetime.today()-datetime.timedelta(30)
            self.start_date = one_month_ago.strftime("%Y-%m-%d")
        self.end_date = self.request.GET.get('end_date', None)
        if not self.end_date:
            self.end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        order_revisions_response = buyer_api.view_orders(
            buyer_email=AGENCY_USER_ID,
            start_date=datetime.datetime.strptime(self.start_date, "%Y-%m-%d"),
            end_date=datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
        )
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListOrderRevisionsView, self).get_context_data(*args, **kwargs)
        context_data['start_date'] = self.start_date
        context_data['end_date'] = self.end_date
        return context_data

class Seller_ListRFPsView(PATSAPIMixin, ListView):
    start_date = None
    end_date = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.start_date = self.request.GET.get('start_date', None)
        if not self.start_date:
            one_month_ago = datetime.datetime.today()-datetime.timedelta(30)
            self.start_date = one_month_ago.strftime("%Y-%m-%d")
        self.end_date = self.request.GET.get('end_date', None)
        if not self.end_date:
            self.end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        seller_rfps_response = seller_api.view_rfps(
            start_date=datetime.datetime.strptime(self.start_date, "%Y-%m-%d"),
            end_date=datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
        )
        return seller_rfps_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListRFPsView, self).get_context_data(*args, **kwargs)
        context_data['start_date'] = self.start_date
        context_data['end_date'] = self.end_date
        return context_data
    
class Seller_ListProposalsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        seller_proposals_response = seller_api.view_proposals(rfp_id=self.rfp_id)
        return seller_proposals_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListProposalsView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

