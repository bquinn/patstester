import datetime
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView

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
    vendor_id = None
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.vendor_id = self.kwargs.get('publisher_id', None)
        publisher_users_response = buyer_api.get_users_for_seller(user_id=AGENCY_USER_ID, vendor_id=self.vendor_id)
        # publisher emails list is actually the "payload" component of the dict
        return publisher_users_response['payload']['emails']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublisherUsersView, self).get_context_data(*args, **kwargs)
        context_data['vendor_id'] = self.vendor_id
        return context_data

class Buyer_GetAgenciesView(PATSAPIMixin, ListView):
    agency_id = None
    search_name = None
    search_updated_date = None

    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.agency_id = self.request.GET.get('agency_id', self.kwargs.get('agency_id', None))
        self.search_name = self.request.GET.get('name', None)
        self.search_updated_date = self.request.GET.get('last_updated_date', None)
        agencies_response = buyer_api.get_buyers(user_id=AGENCY_USER_ID, agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
        return agencies_response['payload']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetAgenciesView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.agency_id or ''
        context_data['name'] = self.search_name or ''
        context_data['last_updated_date'] = self.search_updated_date or ''
        return context_data

class Buyer_RFPDetailView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        rfp_detail_response = buyer_api.view_rfp_detail(sender_user_id=AGENCY_USER_ID, rfp_id=self.rfp_id)
        return rfp_detail_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_RFPDetailView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Buyer_RFPSearchView(PATSAPIMixin, ListView):
    search_advertiser_name = None
    search_rfp_start_date = None
    search_rfp_end_date = None
    search_campaign_urn = None
    search_response_due_date = None
    search_status = None

    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.search_advertiser_name = self.request.GET.get('advertiser_name', None)
        self.search_rfp_start_date = self.request.GET.get('rfp_start_date', None)
        self.search_rfp_end_date = self.request.GET.get('rfp_end_date', None)
        self.search_campaign_urn = self.request.GET.get('campaign_urn', None)
        self.search_response_due_date = self.request.GET.get('response_due_date', None)
        self.search_status = self.request.GET.get('status', None)
        rfp_list = buyer_api.search_rfps(
            user_id=AGENCY_USER_ID,
            advertiser_name=self.search_advertiser_name,
            rfp_start_date=self.search_rfp_start_date,
            rfp_end_date=self.search_rfp_end_date,
            campaign_urn=self.search_campaign_urn,
            response_due_date=self.search_response_due_date,
            status=self.search_status
        )
        return rfp_list

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_RFPSearchView, self).get_context_data(*args, **kwargs)
        context_data['search_advertiser_name'] = self.search_advertiser_name or ''
        context_data['search_rfp_start_date'] = self.search_rfp_start_date
        context_data['search_rfp_end_date'] = self.search_rfp_end_date
        context_data['search_campaign_urn'] = self.search_campaign_urn or ''
        context_data['search_response_due_date'] = self.search_response_due_date
        context_data['search_status'] = self.search_status or ''
        return context_data

class Buyer_OrderDetailView(PATSAPIMixin, DetailView):
    order_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        order_detail_response = buyer_api.view_order_detail(buyer_email=TEST_PERSON_ID, order_public_id=self.order_id)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderDetailView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        return context_data

class Buyer_SendOrderView(PATSAPIMixin, FormView):
    form_class = Buyer_SendOrderForm
    agency_id = AGENCY_ID
    success_url = reverse_lazy('buyer_orders_create')

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        messages.success(self.request, 'Order successfully sent. (Not really)')
        return super(Buyer_SendOrderView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_SendOrderView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.agency_id
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
        order_revisions_response = buyer_api.view_order_revisions(
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

class Buyer_ListProductsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.vendor_id = self.kwargs.get('publisher_id', None)
        product_catalogue_response = buyer_api.list_products(vendor_id=self.vendor_id, user_id=AGENCY_USER_ID)
        return product_catalogue_response['products']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListProductsView, self).get_context_data(*args, **kwargs)
        context_data['vendor_id'] = self.vendor_id
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

class Seller_ListOrdersView(PATSAPIMixin, ListView):
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
        order_revisions_response = seller_api.view_orders(
            start_date=datetime.datetime.strptime(self.start_date, "%Y-%m-%d"),
            end_date=datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
        )
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListOrdersView, self).get_context_data(*args, **kwargs)
        context_data['start_date'] = self.start_date
        context_data['end_date'] = self.end_date
        return context_data

class Seller_OrderDetailView(PATSAPIMixin, DetailView):
    order_id = None
    version = None

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        # version defaults to 0
        self.version = self.kwargs.get('version', 0)
        order_detail_response = seller_api.view_order_detail(order_id=self.order_id, version=self.version)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderDetailView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        return context_data
    
class Seller_OrderHistoryView(PATSAPIMixin, ListView):
    order_id = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        order_history_response = seller_api.view_order_history(order_id=self.order_id)
        return order_history_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderHistoryView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        return context_data
    
