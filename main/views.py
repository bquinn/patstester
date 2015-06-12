import datetime
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

from pats import PATSBuyer, PATSSeller
from .forms import Buyer_SendOrderForm, ConfigurationForm

# Default values for API buyer/seller parameters
# buy side
MEDIAOCEAN_AGENCY_API_KEY = 'yt6wsdwrauz7mrawha7rua8v'
AGENCY_ID = '35-IDSDKAD-7'
AGENCY_USER_ID = 'brenddlo@pats3'
AGENCY_COMPANY_ID = 'PATS3'
AGENCY_PERSON_ID = 'brenddlo'
# sell side
# MEDIAOCEAN_PUBLISHER_API_KEY = 'nz5ta424wv8m2bmg4njbgwya'
MEDIAOCEAN_PUBLISHER_API_KEY = 'yt6wsdwrauz7mrawha7rua8v'
PUBLISHER_ID = '35-EEBMG4J-4'

class PATSAPIMixin(object):
    pats_buyer = None
    pats_seller = None
    _agency_id = AGENCY_ID
    _agency_api_key = MEDIAOCEAN_AGENCY_API_KEY
    _agency_user_id = AGENCY_USER_ID
    _agency_person_id = AGENCY_PERSON_ID
    _agency_company_id = AGENCY_COMPANY_ID
    _publisher_id = PUBLISHER_ID
    _publisher_api_key = MEDIAOCEAN_PUBLISHER_API_KEY

    def get_agency_id(self):
        return self._agency_id

    def set_agency_id(self, agency_id):
        self._agency_id = agency_id

    def get_agency_api_key(self):
        return self._agency_api_key
 
    def set_agency_api_key(self, agency_api_key):
        self._agency_api_key = agency_api_key

    def get_agency_user_id(self):
        return self._agency_user_id
 
    def set_agency_user_id(self, agency_user_id):
        self._agency_user_id = agency_user_id

    def get_agency_person_id(self):
        return self._agency_person_id
 
    def set_agency_user_id(self, agency_person_id):
        self._agency_person_id = agency_person_id

    def get_agency_company_id(self):
        return self._agency_company_id
 
    def set_agency_company_id(self, agency_company_id):
        self._agency_company_id = agency_company_id

    def get_publisher_id(self):
        return self._publisher_id
 
    def set_publisher_id(self, publisher_id):
        self._publisher_id = publisher_id

    def get_publisher_api_key(self):
        return self._publisher_api_key
 
    def set_publisher_api_key(self, publisher_api_key):
        self._publisher_api_key = publisher_api_key

    def get_buyer_api_handle(self):
        if not self.pats_buyer and 'api_handle_buyer' in self.request.session:
            self.pats_buyer = self.request.session['api_handle_buyer']
        else:
            self.pats_buyer = PATSBuyer(agency_id=self.get_agency_id(), api_key=self.get_agency_api_key(), debug_mode=True)
        return self.pats_buyer

    def get_seller_api_handle(self):
        if not self.pats_seller and 'api_handle_seller' in self.request.session:
            self.pats_seller = self.request.session['api_handle_seller']
        else:
            self.pats_seller = PATSSeller(vendor_id=self.get_publisher_id(), api_key=self.get_publisher_api_key(), debug_mode=True)
        return self.pats_seller

class Buyer_GetPublishersView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        publishers_response = buyer_api.get_sellers(user_id=self.get_agency_user_id())
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
        publisher_users_response = buyer_api.get_users_for_seller(user_id=self.get_agency_user_id(), vendor_id=self.vendor_id)
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
        self.agency_id = self.request.GET.get('agency_id', self.kwargs.get('agency_id', self.get_agency_id()))
        self.search_name = self.request.GET.get('name', None)
        self.search_updated_date = self.request.GET.get('last_updated_date', None)
        agencies_response = buyer_api.get_buyers(user_id=self.get_agency_user_id(), agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
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
        rfp_detail_response = buyer_api.view_rfp_detail(sender_user_id=self.get_agency_user_id(), rfp_id=self.rfp_id)
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
            user_id=self.get_agency_user_id(),
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
        order_detail_response = buyer_api.view_order_detail(buyer_email=self.get_agency_person_id(), order_public_id=self.order_id)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderDetailView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        return context_data

class Buyer_SendOrderView(PATSAPIMixin, FormView):
    form_class = Buyer_SendOrderForm
    success_url = reverse_lazy('buyer_orders_create')

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        messages.success(self.request, 'Order successfully sent. (Not really)')
        return super(Buyer_SendOrderView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_SendOrderView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
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
            buyer_email=self.get_agency_user_id(),
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
        product_catalogue_response = buyer_api.list_products(vendor_id=self.vendor_id, user_id=self.get_agency_user_id())
        return product_catalogue_response['products']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListProductsView, self).get_context_data(*args, **kwargs)
        context_data['vendor_id'] = self.vendor_id
        return context_data

class Seller_GetAgenciesView(PATSAPIMixin, ListView):
    agency_id = None
    search_name = None
    search_updated_date = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.agency_id = self.request.GET.get('agency_id', self.kwargs.get('agency_id', self.get_agency_id()))
        self.search_name = self.request.GET.get('name', None)
        self.search_updated_date = self.request.GET.get('last_updated_date', None)
        agencies_response = seller_api.get_agency_by_id(user_id=self.get_agency_user_id(), agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
        return agencies_response['payload']

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_GetAgenciesView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.agency_id or ''
        context_data['name'] = self.search_name or ''
        context_data['last_updated_date'] = self.search_updated_date or ''
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
    
class ConfigurationView(PATSAPIMixin, FormView):
    form_class = Buyer_SendOrderForm

    def form_valid(self, form):
        messages.success(self.request, 'Order successfully sent. (Not really)')
        return super(Buyer_SendOrderView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(ConfigurationView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_api_key'] = self.get_agency_api_key()
        context_data['agency_user_id'] = self.get_agency_user_id()
        context_data['agency_company_id'] = self.get_agency_company_id()
        context_data['agency_person_id'] = self.get_agency_person_id()
        context_data['publisher_id'] = self.get_publisher_id()
        context_data['publisher_api_key'] = self.get_publisher_api_key()
        return context_data
    
