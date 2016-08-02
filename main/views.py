import base64
import datetime
import json
import logging
import os
import random
import re
import string
import pytz
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from oauth2_provider.views.generic import ProtectedResourceView

from pats import PATSBuyer, PATSSeller, PATSException, CampaignDetails, Product

from .forms import (
    Buyer_CampaignForm,
    Buyer_CreateRFPForm, Buyer_CreateRFPWithCampaignForm, Buyer_ReturnProposalForm,
    Buyer_ReturnOrderRevisionForm, Buyer_RequestOrderRevisionForm,
    Buyer_CreateOrderRawForm, Buyer_CreateOrderForm, Buyer_CreateOrderWithCampaignForm,
    Seller_CreateProposalRawForm,
    Seller_OrderRespondForm, Seller_OrderReviseForm,
    Seller_ProductForm, Seller_MediaPropertyForm,
    ConfigurationForm
)
from .models import PATSEvent

# Default values for API buyer/seller parameters
# buy side
CONFIG_DEFAULTS = {
    'DMG Media': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': '4ust6fh2x38hcw8pq2vcef4r',
        'PUBLISHER_ID': '35-PUOEFOA-9',
        'PUBLISHER_USER': 'mona.tawfik@mailnewspapers.co.uk'
    },
    'ESI Media': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-UJTPWVA-1',
        'PUBLISHER_USER': 'John.Gay@esimedia.co.uk'
    },
    'Guardian': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-SKDCCGM-2',
        'PUBLISHER_USER': 'Marsha.Sappleton@guardian.co.uk'
    },
    'News UK': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-OMXDD1T-5',
        'PUBLISHER_USER': 'Rob.Scott@news.co.uk'
    },
    'PATS Media': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-EEBMG4J-4',
        'PUBLISHER_USER': 'brendan.quinn@pats.org.uk'
    },
    'Telegraph': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-OIFNHJ7-6',
        'PUBLISHER_USER': 'gareth.jones@telegraph.co.uk'
    },
    'Trinity Mirror': {
        'AGENCY_API_KEY': 'yt6wsdwrauz7mrawha7rua8v',
        'AGENCY_ID': '35-IDSDKAD-7',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS3',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-49UUMIY-3',
        'PUBLISHER_USER': 'markc.turner@trinitymirror.com'
    },
    'Adazzle': {
        'AGENCY_API_KEY': 'm95d2up63susdaxv5qxme4hu',
        'AGENCY_ID': '35-URIDWNA-4',
        'AGENCY_USER_ID': 'brenddlo',
        'AGENCY_GROUP_ID': 'PATS4',
        'PUBLISHER_API_KEY': 'nz5ta424wv8m2bmg4njbgwya',
        'PUBLISHER_ID': '35-EEBMG4J-4',
        'PUBLISHER_USER': 'brendan.quinn@pats.org.uk'
    },
 
}
# the default default?!
CONFIG_DEFAULTS_DEFAULT = 'PATS Media'

ADVERTISER_NAMES = {
    #'AA': 'AMEX',
    'AA4': 'ALTON', 'AAB': 'FORD', 'AAH': 'SATAC',
    'AB2': 'AMAZ', 'AMI': 'AUTOMOBILES', 'ARR': 'AAA', 'DEM': 'DEMO',
    'GE1': 'GR ENTERTAIN', 'HFC': 'HEALTH', 'MOA': 'MOU TRAVEL',
    'SLO': 'BRIT. RAIL',
    # 'SU1': 'SUPERMARKET',
    'VOT': 'VODKA'
}
ADVERTISER_LIST = ADVERTISER_NAMES.keys()

class PATSAPIMixin(object):
    pats_buyer = None
    pats_seller = None
    logger = None
    debug_mode = True   # hardcoded for now
    raw_mode = True     # hardcoded for now

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(PATSAPIMixin, self).__init__(*args, **kwargs)

    def get_agency_id(self):
        if 'agency_id' not in self.request.session:
            self.request.session['agency_id'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['AGENCY_ID']
        return self.request.session['agency_id']

    def set_agency_id(self, agency_id):
        self.request.session['agency_id'] = agency_id

    def get_agency_api_key(self):
        if 'agency_api_key' not in self.request.session:
            self.request.session['agency_api_key'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['AGENCY_API_KEY']
        return self.request.session['agency_api_key']
 
    def set_agency_api_key(self, agency_api_key):
        self.request.session['agency_api_key'] = agency_api_key

    def get_agency_user_id(self):
        if 'agency_user_id' not in self.request.session:
            self.request.session['agency_user_id'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['AGENCY_USER_ID']
        return self.request.session['agency_user_id']

    def set_agency_user_id(self, agency_user_id):
        self.request.session['agency_user_id'] = agency_user_id
 
    def get_agency_group_id(self):
        if 'agency_group_id' not in self.request.session:
            self.request.session['agency_group_id'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['AGENCY_GROUP_ID']
        return self.request.session['agency_group_id']

    def set_agency_group_id(self, agency_group_id):
        self.request.session['agency_group_id'] = agency_group_id

    def get_publisher_id(self):
        if 'publisher_id' not in self.request.session:
            self.request.session['publisher_id'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['PUBLISHER_ID']
        return self.request.session['publisher_id']

    def set_publisher_id(self, publisher_id):
        self.request.session['publisher_id'] = publisher_id

    def get_publisher_api_key(self):
        if 'publisher_api_key' not in self.request.session:
            self.request.session['publisher_api_key'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['PUBLISHER_API_KEY']
        return self.request.session['publisher_api_key']

    def set_publisher_api_key(self, publisher_api_key):
        self.request.session['publisher_api_key'] = publisher_api_key

    def get_publisher_user(self):
        if 'publisher_user' not in self.request.session:
            self.request.session['publisher_user'] = CONFIG_DEFAULTS[CONFIG_DEFAULTS_DEFAULT]['PUBLISHER_USER']
        return self.request.session['publisher_user']
        
    def set_publisher_user(self, publisher_user):
        self.request.session['publisher_user'] = publisher_user

    def get_buyer_api_handle(self):
        if not self.pats_buyer and 'api_handle_buyer' in self.request.session:
            self.pats_buyer = self.request.session['api_handle_buyer']
        else:
            self.pats_buyer = PATSBuyer(agency_id=self.get_agency_id(), agency_group_id=self.get_agency_group_id(), user_id=self.get_agency_user_id(), api_key=self.get_agency_api_key(), debug_mode=self.debug_mode, raw_mode=self.raw_mode, session=self.request.session)
        return self.pats_buyer

    def get_seller_api_handle(self):
        if not self.pats_seller and 'api_handle_seller' in self.request.session:
            self.pats_seller = self.request.session['api_handle_seller']
        else:
            self.pats_seller = PATSSeller(vendor_id=self.get_publisher_id(), api_key=self.get_publisher_api_key(), user_id=self.get_publisher_user(), debug_mode=self.debug_mode, raw_mode=self.raw_mode, session=self.request.session)
        return self.pats_seller

    def get_defaults_key(self):
        # in the context processor we actually load this directly from the session
        # because we don't have access to this method
        if 'defaults_key' not in self.request.session:
            self.set_defaults_key(CONFIG_DEFAULTS_DEFAULT)
        return self.request.session['defaults_key']

    def set_defaults_key(self, defaults_key):
        self.request.session['defaults_key'] = defaults_key

    def set_config_defaults(self, defaults=CONFIG_DEFAULTS_DEFAULT):
        if defaults not in CONFIG_DEFAULTS:
            raise Exception('defaults must be one of %s' % ','.join(keys(CONFIG_DEFAULTS)))
        self.set_agency_api_key(CONFIG_DEFAULTS[defaults]['AGENCY_API_KEY'])
        self.set_agency_id(CONFIG_DEFAULTS[defaults]['AGENCY_ID'])
        self.set_agency_user_id(CONFIG_DEFAULTS[defaults]['AGENCY_USER_ID'])
        self.set_agency_group_id(CONFIG_DEFAULTS[defaults]['AGENCY_GROUP_ID'])
        self.set_publisher_api_key(CONFIG_DEFAULTS[defaults]['PUBLISHER_API_KEY'])
        self.set_publisher_id(CONFIG_DEFAULTS[defaults]['PUBLISHER_ID'])
        self.set_publisher_user(CONFIG_DEFAULTS[defaults]['PUBLISHER_USER'])
        self.set_defaults_key(defaults)

    def clear_curl_history(self):
        if self.request.session:
            self.request.session['curl_command'] = ''
            self.request.session['response_status'] = ''
            self.request.session['response_text'] = ''

    def get_example_campaign_id(self):
        if not hasattr(self, 'example_campaign_id'):
            self.example_campaign_id = "CAMP"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return self.example_campaign_id

    def get_example_campaign_name(self):
        if not hasattr(self, 'example_campaign_name'):
            self.example_campaign_name = "Test Campaign "+self.get_example_campaign_id()
        return self.example_campaign_name

    def get_example_campaign_start_date(self):
        if not hasattr(self, 'example_campaign_start_date'):
            self.example_campaign_start_date = datetime.datetime.today()+datetime.timedelta(30)
        return self.example_campaign_start_date.strftime("%Y-%m-%d")

    def get_example_campaign_end_date(self):
        if not hasattr(self, 'example_campaign_end_date'):
            self.example_campaign_end_date = datetime.datetime.today()+datetime.timedelta(60)
        return self.example_campaign_end_date.strftime("%Y-%m-%d")

    def get_example_advertiser_id(self):
        return random.choice(ADVERTISER_LIST)

    def get_example_respond_by_date(self):
        if not hasattr(self, 'example_respond_by_date'):
            self.example_respond_by_date = datetime.datetime.today()+datetime.timedelta(14)
        return self.example_respond_by_date.strftime("%Y-%m-%d")

    def get_example_budget(self):
        if not hasattr(self, 'example_budget'):
            self.example_budget = random.randint(50000,100000)
        return self.example_budget

    def replace_template_strings(self, payload, publisher_id, publisher_email, user_id, campaign_id, campaign_start_date, campaign_end_date, respond_by_date):
        payload = payload.replace("PUBLISHER_ID", publisher_id)
        payload = payload.replace("PUBLISHER_EMAIL", publisher_email)
        payload = payload.replace("CAMPAIGN_ID", campaign_id)
        payload = payload.replace("CAMPAIGN_START_DATE", campaign_start_date.strftime("%Y-%m-%d"))
        payload = payload.replace("CAMPAIGN_END_DATE", campaign_end_date.strftime("%Y-%m-%d"))
        payload = payload.replace("RESPOND_BY_DATE", respond_by_date.strftime("%Y-%m-%d"))
        payload = payload.replace("CAMPAIGN_START_MONTH", str(campaign_start_date.month))
        payload = payload.replace("CAMPAIGN_START_YEAR", str(campaign_start_date.year))
        payload = payload.replace("CAMPAIGN_END_MONTH", str(campaign_end_date.month))
        payload = payload.replace("CAMPAIGN_END_YEAR", str(campaign_end_date.year))
        return payload

class TestOrdersMixin(object):
    test_data_id = None
    test_data = None

    def get_test_files_list(self, force_reload=False):
        if 0: # 'test_orders' in self.request.session:
            test_files = self.request.session['test_orders']
        else:
            # build up list of test files from disk store
            files = []; test_files = {}
            for (dirpath, dirnames, filenames) in os.walk(settings.TEST_ORDERS_PATH):
                files.extend(filenames)
            for filename in files:
                matches = re.match("([^_]+)_(.*)", filename)
                file_id = matches.group(1)
                test_files[file_id] = filename
            self.request.session['test_orders'] = test_files
        return test_files

    def load_test_file(self, test_file_id):
        test_files = self.get_test_files_list()
        json_test_file_data = None
        if test_file_id in test_files:
            filename = test_files[test_file_id]
            with open(settings.TEST_ORDERS_PATH+"/"+filename, "r") as file_handle:
                raw_file = file_handle.read()
                raw_data = raw_file.decode('utf-8')
                json_test_file_data = json.loads(raw_data)
        return json_test_file_data

class Buyer_CallbackView(PATSAPIMixin, ProtectedResourceView):
    # disable CSRF checking for this view because it's being called via OAuth, not from a form
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Buyer_CallbackView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        received_json_data=json.loads(request.body.decode("utf-8"))
        self.logger.info("event handler: received data:")
        self.logger.info(received_json_data)
        if type(received_json_data) is not list:
            return HttpResponseBadRequest('Data should be a JSON array of objects')
        tz = pytz.timezone('UTC')
        for record in received_json_data:
            # in 2016.3 this will become "eventTime" and will be ISO date
            eventTime = record.get('eventTime',None)
            # eventTime = record.get('eventDateInMillis',None)
            eventDateTime = None
            if eventTime:
                # 2016.2 eventDateTime = datetime.datetime.fromtimestamp(eventTime/1000, tz)
                # 2016.3:
                eventDateTime = datetime.datetime.strptime(eventTime,'%Y-%m-%dT%H:%M:%SZ')
            attributes = record.get('attributes',None)
            event = PATSEvent(
                entity_id=record.get('entityId',None),
                event_date=eventDateTime,
                subscription_type=record.get('subscriptionType',None),
                event_type=record.get('eventType',None),
                major_version=attributes.get('majorVersion',0),
                minor_version=attributes.get('minorVersion',0),
            )
            event.save()

        return HttpResponse('Event received')

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'], 'Please send data in a JSON payload in a POST request to this endpoint.')

class Buyer_ListEventsView(PATSAPIMixin, ListView):
    model = PATSEvent
    paginate_by = settings.RESULTS_PER_PAGE

    def get_queryset(self, **kwargs):
        queryset = super(Buyer_ListEventsView, self).get_queryset(**kwargs)
        self.search_subscription_type = self.request.GET.get('search_subscription_type', None)
        self.search_event_type = self.request.GET.get('search_event_type', None)
        self.search_from_date = self.request.GET.get('search_from_date', None)
        self.search_to_date = self.request.GET.get('search_to_date', None)
        if self.search_subscription_type:
            queryset = queryset.filter(subscription_type = self.search_subscription_type)
        if self.search_event_type:
            queryset = queryset.filter(event_type = self.search_event_type)
        if self.search_from_date:
            queryset = queryset.filter(event_date__gt = self.search_from_date)
        if self.search_to_date:
            queryset = queryset.filter(event_date__lt = self.search_to_date)
        queryset = queryset.order_by('-event_date')
        return queryset

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListEventsView, self).get_context_data(*args, **kwargs)
        context_data['search_subscription_type'] = self.search_subscription_type
        context_data['subscription_types'] = { '' : 'None', 'order': 'Order', 'revision' : 'Revision' }
        context_data['search_event_type'] = self.search_event_type
        context_data['event_types'] = {
            '' : 'None',
            'Sent': 'Sent',
            'Accepted': 'Accepted',
            'Rejected': 'Rejected',
            'RevisionRequested': 'Revision requested',
            'RevisionSent': 'Revision sent',
            'RevisionReturned': 'Revision returned',
            'Expired' : 'Expired'
        }
        context_data['search_from_date'] = self.search_from_date
        context_data['search_to_date'] = self.search_to_date
        return context_data

class Buyer_ReprocessEventsView(PATSAPIMixin, TemplateView):
    since_date = None

    def get(self, *args, **kwargs):
        self.clear_curl_history()
        since_date_string = self.request.GET.get('since_date', None)
        if since_date_string:
            self.since_date = datetime.datetime.strptime(since_date_string,'%Y-%m-%dT%H:%M')
            buyer_api = self.get_buyer_api_handle()
            response = None
            try:
                response = buyer_api.reprocess_events(since_date=self.since_date)
            except PATSException as error:
                messages.error(self.request, "Reprocess events failed. Error: %s %s" % (error, response))
            else:
                messages.success(self.request, "Event reprocessing requested successfully!")
        return super(Buyer_ReprocessEventsView, self).get(*args, **kwargs)

class Buyer_GetPublishersView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        publishers_response = None
        response = None
        try:
            publishers_response = buyer_api.get_sellers(user_id=self.get_agency_user_id())
        except PATSException as error:
            messages.error(self.request, "Get publishers failed. Error: %s %s" % (error, publishers_response))
        else:
            response = publishers_response['payload']
            # publishers list is actually the "payload" component of the dict
        return response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublishersView, self).get_context_data(*args, **kwargs)
        return context_data

class Buyer_GetPublisherUsersView(PATSAPIMixin, ListView):
    vendor_id = None
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.vendor_id = self.kwargs.get('publisher_id', None)
        publisher_users_response = {}
        try:
            publisher_users_response = buyer_api.get_users_for_seller(user_id=self.get_agency_user_id(), vendor_id=self.vendor_id)
            # publisher_users_response = buyer_api.get_users_for_seller(user_id='brenddlo@pats3', vendor_id=self.vendor_id)
            # publisher emails list is actually the "payload" component of the dict
            return publisher_users_response['payload']['emails']
        except PATSException as error:
            messages.error(self.request, "Get publisher users failed. Error: %s" % error)
        return

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublisherUsersView, self).get_context_data(*args, **kwargs)
        context_data['vendor_id'] = self.vendor_id
        return context_data

class Buyer_GetPublisherMediaPropertiesView(PATSAPIMixin, TemplateView):
    media_property_details = None

    def get(self, *args, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.publisher_id = self.get_publisher_id()
        self.media_property_details = seller_api.get_media_property_details(organisation_id=self.publisher_id)
        return super(Buyer_GetPublisherMediaPropertiesView, self).get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_GetPublisherMediaPropertiesView, self).get_context_data(*args, **kwargs)
        context_data['media_properties'] = self.media_property_details
        context_data['publisher_id'] = self.publisher_id
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
        agencies_response = None
        try:
            agencies_response = buyer_api.get_buyers(user_id=self.get_agency_user_id(), agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
            # agencies_response = buyer_api.get_buyers(user_id='brenddlo@pats3', agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
            return agencies_response['payload']
        except PATSException as error:
            messages.error(self.request, "Get agencies failed. Error: %s" % error)
        return

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
        rfp_detail_response = ''
        try:
            rfp_detail_response = buyer_api.view_rfp_detail(user_id=self.get_agency_user_id(), rfp_id=self.rfp_id)
        except PATSException as error:
            messages.error(self.request, "Get RFP detail failed. Error: %s" % error)
        return rfp_detail_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_RFPDetailView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Buyer_ViewRFPAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        rfp_attachment_response = ''
        try:
            rfp_attachment_response = buyer_api.get_rfp_attachment(user_id=self.get_agency_user_id(), rfp_id=self.rfp_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get RFP attachment failed. Error: %s" % error)
        return rfp_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ViewRFPAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['rfp_id'] = self.rfp_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Buyer_DownloadRFPAttachmentView(PATSAPIMixin, DetailView):
    def get(self, *args, **kwargs):
        old_response = super(Buyer_DownloadRFPAttachmentView, self).get(*args, **kwargs)
        file_contents = base64.b64decode(self.rfp_attachment['contents'])
        http_response = HttpResponse(content_type=self.rfp_attachment['mimeType'])
        # the "attachment" makes the browser pop up a "do you wish to download?" window
        http_response['Content-Disposition'] = 'attachment; filename="'+self.rfp_attachment['name']+'"'
        http_response['Content-Length'] = len(file_contents)
        http_response.write(file_contents)
        return http_response

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        rfp_attachment_response = ''
        try:
            rfp_attachment_response = buyer_api.get_rfp_attachment(user_id=self.get_agency_user_id(), rfp_id=self.rfp_id, attachment_id=self.attachment_id)
            self.rfp_attachment = rfp_attachment_response
        except PATSException as error:
            messages.error(self.request, "Get RFP attachment failed. Error: %s" % error)
        return rfp_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_DownloadRFPAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['rfp_id'] = self.rfp_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Buyer_ViewOrderAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            order_attachment_response = buyer_api.get_order_attachment(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id, order_id=self.order_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get order attachment failed. Error: %s" % error)
        return order_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ViewOrderAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Buyer_DownloadOrderAttachmentView(PATSAPIMixin, DetailView):
    def get(self, *args, **kwargs):
        old_response = super(Buyer_DownloadOrderAttachmentView, self).get(*args, **kwargs)
        file_contents = base64.b64decode(self.order_attachment['contents'])
        http_response = HttpResponse(content_type=self.order_attachment['mimeType'])
        # the "attachment" version pops up a "do you wish to download?" window
        http_response['Content-Disposition'] = 'attachment; filename="'+self.order_attachment['name']+'"'
        http_response['Content-Length'] = len(file_contents)
        http_response.write(file_contents)
        return http_response

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            order_attachment_response = buyer_api.get_order_attachment(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id, order_id=self.order_id, attachment_id=self.attachment_id)
            self.order_attachment = order_attachment_response
        except PATSException as error:
            messages.error(self.request, "Get order attachment failed. Error: %s" % error)
        return order_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_DownloadOrderAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Buyer_ViewProposalAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            proposal_attachment_response = buyer_api.get_proposal_attachment(user_id=self.get_agency_user_id(), proposal_id=self.proposal_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get proposal attachment failed. Error: %s" % error)
        return proposal_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ViewProposalAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['rfp_id'] = self.rfp_id
        context_data['proposal_id'] = self.proposal_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Buyer_DownloadProposalAttachmentView(PATSAPIMixin, DetailView):
    def get(self, *args, **kwargs):
        old_response = super(Buyer_DownloadProposalAttachmentView, self).get(*args, **kwargs)
        file_contents = base64.b64decode(self.proposal_attachment['contents'])
        http_response = HttpResponse(content_type=self.proposal_attachment['mimeType'])
        # the "attachment" makes the browser pop up a "do you wish to download?" window
        http_response['Content-Disposition'] = 'attachment; filename="'+self.proposal_attachment['name']+'"'
        http_response['Content-Length'] = len(file_contents)
        http_response.write(file_contents)
        return http_response

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        try:
            proposal_attachment_response = buyer_api.get_proposal_attachment(user_id=self.get_agency_user_id(), proposal_id=self.proposal_id, attachment_id=self.attachment_id)
            self.proposal_attachment = proposal_attachment_response
        except PATSException as error:
            messages.error(self.request, "Get proposal attachment failed. Error: %s" % error)
        return proposal_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_DownloadProposalAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        context_data['proposal_id'] = self.proposal_id
        context_data['attachment_id'] = self.attachment_id
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
        if not self.search_rfp_start_date:
            one_month_ago = datetime.datetime.today()-datetime.timedelta(7)
            self.search_rfp_start_date = one_month_ago.strftime("%Y-%m-%d")
        self.search_rfp_end_date = self.request.GET.get('rfp_end_date', None)
        if not self.search_rfp_end_date:
            today = datetime.datetime.today()
            self.search_rfp_end_date = today.strftime("%Y-%m-%d")
        self.search_campaign_urn = self.request.GET.get('campaign_urn', None)
        self.search_response_due_date = self.request.GET.get('response_due_date', None)
        self.search_status = self.request.GET.get('status', None)
        rfp_list = ''
        try:
            rfp_list = buyer_api.search_rfps(
                advertiser_name=self.search_advertiser_name,
                rfp_start_date=self.search_rfp_start_date,
                rfp_end_date=self.search_rfp_end_date,
                campaign_urn=self.search_campaign_urn,
                response_due_date=self.search_response_due_date,
                status=self.search_status
            )
        except PATSException as error:
            messages.error(self.request, "Search RFPs failed. Error: %s" % error)
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

class Buyer_RFPsForCampaignView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        rfp_list = ''
        try:
            rfp_list = buyer_api.list_rfps_for_campaign(campaign_id=self.campaign_id)
        except PATSException as error:
            messages.error(self.request, "List RFPs for Campaign failed. Error: %s" % error)
        return rfp_list

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_RFPsForCampaignView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id or ''
        return context_data

class Buyer_RequestOrderRevisionView(PATSAPIMixin, FormView):
    form_class = Buyer_RequestOrderRevisionForm
    order_id = None

    def get(self, *args, **kwargs):
#        self.clear_curl_history()
        return super(Buyer_RequestOrderRevisionView, self).get(*args, **kwargs)

    def get_initial(self):
        if 'version' in self.kwargs:
            self.version = self.kwargs.get('version', None)
        if 'campaign_id' in self.kwargs:
            self.campaign_id = self.kwargs.get('campaign_id', None)
        if 'order_id' in self.kwargs:
            self.order_id = self.kwargs.get('order_id', None)
        return {
            'version': self.version,
            'campaign_id': self.campaign_id,
            'order_id': self.order_id,
            'user_id': self.get_agency_user_id(),
            'seller_email': self.get_publisher_user()
        }

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        self.order_id = form.cleaned_data['order_id']
        user_id = form.cleaned_data['user_id']
        seller_email = form.cleaned_data['seller_email']
        comments = form.cleaned_data['comments']
        due_date = form.cleaned_data['due_date']
        campaign_id = None
        if 'campaign_id' in self.kwargs:
            campaign_id = self.kwargs['campaign_id']
        response = ''
        try:
            response = buyer_api.request_order_revision(campaign_id=campaign_id, order_id=self.order_id, version=self.version, user_id=user_id, seller_email=seller_email, revision_due_date=due_date, comment=comments)
        except PATSException as error:
            messages.error(self.request, "Request order revision failed: %s" % error)
        else:
            messages.success(self.request, "Order revision requested successfully.")
        return super(Buyer_RequestOrderRevisionView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_RequestOrderRevisionView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id or ''
        context_data['order_id'] = self.order_id or ''
        context_data['version'] = self.version or ''
        return context_data

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('buyer_orders_requestrevision', kwargs={'campaign_id':self.campaign_id,'order_id':self.order_id,'version':self.version})

class Buyer_ReturnOrderRevisionView(PATSAPIMixin, FormView):
    form_class = Buyer_ReturnOrderRevisionForm
    order_id = None

    def get(self, *args, **kwargs):
        # self.clear_curl_history()
        return super(Buyer_ReturnOrderRevisionView, self).get(*args, **kwargs)

    def get_initial(self):
        if 'campaign_id' in self.kwargs:
            self.campaign_id = self.kwargs.get('campaign_id', None)
        if 'order_id' in self.kwargs:
            self.order_id = self.kwargs.get('order_id', None)
        if 'version' in self.kwargs:
            self.version = self.kwargs.get('version', None)
        if 'revision' in self.kwargs:
            self.revision = self.kwargs.get('revision', None)
        return {
            'seller_email': self.get_publisher_user()
        }

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        seller_email = form.cleaned_data['seller_email']
        comments = form.cleaned_data['comments']
        due_date = form.cleaned_data['due_date']
        user_id = self.get_agency_user_id()
        response = ''
        try:
            response = buyer_api.return_order_revision(user_id=user_id, campaign_id=self.campaign_id, order_id=self.order_id, version=self.version, revision=self.revision, seller_email=seller_email, revision_due_date=due_date, comment=comments)
        except PATSException as error:
            messages.error(self.request, "Return order revision failed: %s" % error)
        else:
            messages.success(self.request, "Order revision returned successfully. %s" % response)
        return super(Buyer_ReturnOrderRevisionView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ReturnOrderRevisionView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id or ''
        context_data['order_id'] = self.order_id or ''
        context_data['version'] = self.version or ''
        context_data['revision'] = self.revision or ''
        return context_data

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('buyer_orders_revisions_return', kwargs={'campaign_id':self.campaign_id,'order_id':self.order_id,'version':self.version,'revision':self.revision})

class Buyer_ReturnProposalView(PATSAPIMixin, FormView):
    form_class = Buyer_ReturnProposalForm

    def get(self, *args, **kwargs):
        self.clear_curl_history()
        return super(Buyer_ReturnProposalView, self).get(*args, **kwargs)

    def get_initial(self):
        if 'rfp_id' in self.kwargs:
            self.rfp_id = self.kwargs.get('rfp_id', None)
        if 'proposal_id' in self.kwargs:
            self.proposal_id = self.kwargs.get('proposal_id', None)
        return {
            'rfp_id': self.rfp_id,
            'proposal_id': self.proposal_id,
            'user_id': self.get_agency_user_id()
        }

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ReturnProposalView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id or ''
        context_data['proposal_id'] = self.proposal_id or ''
        return context_data

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        proposal_id = form.cleaned_data['proposal_id']
        user_id = form.cleaned_data['user_id']
        comments = form.cleaned_data['comments']
        due_date = form.cleaned_data['due_date']
        # turn single email into an array
        emails = [ form.cleaned_data['email'] ]
        # TODO: handle attachments
        attachments = []
        response = ''
        try:
            response = buyer_api.return_proposal(user_id=user_id, proposal_public_id=proposal_id, comments=comments, due_date=due_date, emails=emails, attachments=attachments)
        except PATSException as error:
            messages.error(self.request, "Return proposal failed: %s" % error)
        else:
            messages.success(self.request, "Proposal returned successfully." % response)
        return super(Buyer_ReturnProposalView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('buyer_rfps_proposals_return', kwargs={'rfp_id':self.rfp_id, 'proposal_id':self.proposal_id})

class Buyer_OrderVersionsView(PATSAPIMixin, ListView):
    campaign_id = None
    order_id = None

    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        order_versions_response = None
        try:
            order_versions_response = buyer_api.list_order_versions(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id, order_id=self.order_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load order versions: %s' % error)
        return order_versions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderVersionsView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        return context_data

class Buyer_OrderVersionDetailView(PATSAPIMixin, DetailView):
    order_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.version = self.kwargs.get('version', None)
        order_detail_response = None
        try:
            order_detail_response = buyer_api.view_order_version_detail(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id, order_id=self.order_id, version=self.version)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load order version: %s' % error)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderVersionDetailView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        return context_data

class Buyer_ProposalDetailView(PATSAPIMixin, DetailView):
    proposal_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        proposal_detail_response = None
        try:
            proposal_detail_response = buyer_api.view_proposal_detail(proposal_id=self.proposal_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load proposal: %s' % error)
        return proposal_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ProposalDetailView, self).get_context_data(*args, **kwargs)
        context_data['proposal_id'] = self.proposal_id
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Buyer_OrderStatusView(PATSAPIMixin, DetailView):
    order_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.version = self.kwargs.get('version', None)
        order_status_response = None
        try:
            order_status_response = buyer_api.view_order_status(user_id=self.get_agency_user_id(), agency_group_id=self.get_agency_group_id(), campaign_id=self.campaign_id, order_id=self.order_id, version=self.version)
        except PATSException as error:
            messages.error(self.request, 'Couldn\'t get order status: %s' % error)
        return order_status_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderStatusView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        context_data['campaign_id'] = self.campaign_id
        context_data['version'] = self.version
        return context_data

class Buyer_CreateCampaignView(PATSAPIMixin, FormView):
    form_class = Buyer_CampaignForm
    success_url = reverse_lazy('buyer_campaigns_create')

    def get(self, *args, **kwargs):
        # self.clear_curl_history()
        return super(Buyer_CreateCampaignView, self).get(*args, **kwargs)

    def get_initial(self):
        return {
            'agency_group_id': self.get_agency_group_id(),
            'organisation_id': self.get_agency_id(),
            'user_id': self.get_agency_user_id()
        }

    def form_valid(self, form):
        # because we use forms.DateField, the dates come through already formatted as datetime objects
        campaign_details = CampaignDetails(
            organisation_id = form.cleaned_data['organisation_id'],
            agency_group_id = form.cleaned_data['agency_group_id'],
            user_id = form.cleaned_data['user_id'],
            campaign_name = form.cleaned_data['campaign_name'],
            start_date = form.cleaned_data['start_date'],
            end_date = form.cleaned_data['end_date'],
            advertiser_code = form.cleaned_data['advertiser_code'],
            print_campaign = form.cleaned_data['print_flag'],
            print_campaign_budget = form.cleaned_data['print_budget'],
            digital_campaign = form.cleaned_data['digital_flag'],
            digital_campaign_budget = form.cleaned_data['digital_budget'],
            campaign_budget = form.cleaned_data['campaign_budget'],
            external_id = form.cleaned_data['external_campaign_id'],
        )
        buyer_api = self.get_buyer_api_handle()
        response = ''
        try:
            response = buyer_api.create_campaign(campaign_details)
        except PATSException as error:
            messages.error(self.request, 'Create Campaign failed: %s' % error)
        else:
            messages.success(self.request, 'Create Campaign succeeded: response is %s' % response)
        return super(Buyer_CreateCampaignView, self).form_valid(form)

class Buyer_CampaignDetailView(PATSAPIMixin, DetailView):
    campaign_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        campaign_detail_response = None
        try:
            campaign_detail_response = buyer_api.view_campaign_detail(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load campaign: %s' % error)
        return campaign_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CampaignDetailView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        return context_data

class Buyer_UpdateCampaignDetailView(PATSAPIMixin, FormView):
    campaign_id = None
    form_class = Buyer_CampaignForm

    def form_valid(self, form, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        campaign_details = CampaignDetails(
            organisation_id = form.cleaned_data['organisation_id'],
            agency_group_id = form.cleaned_data['agency_group_id'],
            user_id = form.cleaned_data['user_id'],
            campaign_name = form.cleaned_data['campaign_name'],
            start_date = form.cleaned_data['start_date'],
            end_date = form.cleaned_data['end_date'],
            advertiser_code = form.cleaned_data['advertiser_code'],
            print_campaign = form.cleaned_data['print_flag'],
            print_campaign_budget = form.cleaned_data['print_budget'],
            digital_campaign = form.cleaned_data['digital_flag'],
            digital_campaign_budget = form.cleaned_data['digital_budget'],
            campaign_budget = form.cleaned_data['campaign_budget'],
            external_id = form.cleaned_data['external_campaign_id'],
        )
        result = ''
        try:
            response = buyer_api.update_campaign(campaign_id=self.campaign_id, campaign_details=campaign_details)
        except PATSException as error:
            messages.error(self.request, 'Update campaign failed: %s' % error)
        else:
            messages.success(self.request, 'Campaign updated! Response is %s' % response)
        return super(Buyer_UpdateCampaignDetailView, self).form_valid(form)

    def get_initial(self):
        object = self.get_object()
        print_flag = False; digital_flag = False
        print_budget = 0; digital_budget = 0

        for media in object['mediaBudget']['medias']['media']:
            if media['mediaMix'] == 'Print':
                print_flag = True
                if media['budget']:
                    print_budget = media['budget']
            if media['mediaMix'] == 'Online':
                digital_flag = True
                if media['budget']:
                    digital_budget = media['budget']

        return {
            'organisation_id': self.get_agency_id(),
            'agency_group_id': self.get_agency_group_id(),
            'user_id': self.get_agency_user_id(),
            'advertiser_code': object['advertiser'],
            'external_campaign_id': object['externalDetails']['externalId'],
            'campaign_name': object['campaignName'],
            'start_date': object['startDate'],
            'end_date': object['endDate'],
            'end_date': object['endDate'],
            'campaign_budget': object['mediaBudget']['campaignBudget'],
            'print_flag': print_flag,
            'print_budget': print_budget,
            'digital_flag': digital_flag,
            'digital_budget': digital_budget
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('buyer_campaigns_view', kwargs={'campaign_id':self.campaign_id})

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        campaign_detail_response = None
        try:
            campaign_detail_response = buyer_api.view_campaign_detail(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load campaign: %s' % error)
        return campaign_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_UpdateCampaignDetailView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        return context_data

class Buyer_CreateRFPView(PATSAPIMixin, FormView):
    form_class = Buyer_CreateRFPForm
    success_url = reverse_lazy('buyer_rfps_create')

    def get(self, *args, **kwargs):
        self.clear_curl_history()
        return super(Buyer_CreateRFPView, self).get(*args, **kwargs)

    def get_initial(self):
        return {
            'user_id': self.get_agency_user_id(),
            'publisher_id': self.get_publisher_id()
        }

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        user_id = form.cleaned_data.get('user_id')
        campaign_id = form.cleaned_data.get('campaign_id')
        budget_amount = form.cleaned_data.get('budget_amount')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        respond_by_date = form.cleaned_data.get('respond_by_date')
        comments = form.cleaned_data.get('comments')
        publisher_id = form.cleaned_data.get('publisher_id')
        # API requires a list, so give it a list of one element for now
        publisher_emails = [ form.cleaned_data.get('publisher_emails') ]
        media_print = form.cleaned_data.get('media_print')
        media_online = form.cleaned_data.get('media_online')
        strategy = form.cleaned_data.get('strategy')
        requested_products = form.cleaned_data.get('requested_products')
        attachments = []
        if self.request.FILES:
            # take uploaded file and convert to JSON
            file = self.request.FILES['attachment']
            attachments = [ {
                'fileName': file._name,
                'mimeType': file.content_type,
                'contents': base64.b64encode(file.read())
            }]
        # convert the text string to a json object
        # take submitted values and call API
        result = ''
        try:
            rfp_id = buyer_api.send_rfp(user_id=user_id, campaign_id=campaign_id, budget_amount=budget_amount, start_date=start_date, end_date=end_date, respond_by_date=respond_by_date, comments=comments, publisher_id=publisher_id, publisher_emails=publisher_emails, media_print=media_print, media_online=media_online, strategy=strategy, requested_products=requested_products, attachments=attachments)
        except PATSException as error:
            messages.error(self.request, 'Submit RFP failed: %s' % error)
        else:
            if rfp_id:
                messages.success(self.request, 'RFP sent successfully! RFP ID is %s' % rfp_id)
            else:
                messages.error(self.request, 'Submit RFP failed, blank response: %s' % rfp_id)
        return super(Buyer_CreateRFPView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateRFPView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
        return context_data

class Buyer_CreateRFPWithCampaignView(PATSAPIMixin, FormView):
    form_class = Buyer_CreateRFPWithCampaignForm
    success_url = reverse_lazy('buyer_rfps_create_with_campaign')

    def get(self, *args, **kwargs):
        # self.clear_curl_history()
        return super(Buyer_CreateRFPWithCampaignView, self).get(*args, **kwargs)

    def get_initial(self):
        initial_campaign_start_date = self.get_example_campaign_start_date()
        initial_campaign_end_date = self.get_example_campaign_end_date()
        rfp_respond_by_date = self.get_example_respond_by_date()
        return {
            'advertiser_code': self.get_example_advertiser_id(),
            'agency_id': self.get_agency_id(),
            'agency_group_id': self.get_agency_group_id(),
            'campaign_start_date':  initial_campaign_start_date,
            'campaign_end_date':  initial_campaign_end_date,
            'rfp_start_date':  initial_campaign_start_date,
            'rfp_end_date':  initial_campaign_end_date,
            'rfp_respond_by_date':  rfp_respond_by_date,
            'print_flag': True,
            'digital_flag': True,
            'campaign_budget': self.get_example_budget(),
            'campaign_id': self.get_example_campaign_id(),
            'campaign_name': self.get_example_campaign_name(),
            'user_id': self.get_agency_user_id(),
            'publisher_id': self.get_publisher_id(),
            'publisher_email': self.get_publisher_user()
        }

    def form_valid(self, form):
        organisation_id = form.cleaned_data.get('agency_id')
        agency_group_id = form.cleaned_data.get('agency_group_id')
        user_id = form.cleaned_data.get('user_id')
        publisher_id = form.cleaned_data.get('publisher_id')
        publisher_email = form.cleaned_data.get('publisher_email')
        campaign_id = form.cleaned_data.get('campaign_id')
        # because we use forms.DateField, the dates come through already formatted as datetime objects
        campaign_start_date = form.cleaned_data.get('campaign_start_date')
        campaign_end_date = form.cleaned_data.get('campaign_end_date')
        respond_by_date = form.cleaned_data.get('respond_by_date')
        rfp_budget_amount = form.cleaned_data.get('rfp_budget_amount')
        rfp_start_date = form.cleaned_data.get('rfp_start_date')
        rfp_end_date = form.cleaned_data.get('rfp_end_date')
        rfp_respond_by_date = form.cleaned_data.get('rfp_respond_by_date')
        rfp_comments = form.cleaned_data.get('rfp_comments')
        print_flag = form.cleaned_data.get('print_flag')
        digital_flag = form.cleaned_data.get('digital_flag')
        strategy = form.cleaned_data.get('strategy')
        requested_products = form.cleaned_data.get('requested_products')
        attachments = []
        if self.request.FILES:
            # take uploaded file and convert to JSON
            file = self.request.FILES['attachment']
            attachments = [ {
                'fileName': file._name,
                'mimeType': file.content_type,
                'contents': base64.b64encode(file.read())
            }]
        result = ''
        try:
            campaign_details = CampaignDetails(
                organisation_id = organisation_id,
                agency_group_id = agency_group_id,
                user_id = user_id,
                campaign_name = form.cleaned_data['campaign_name'],
                start_date = campaign_start_date,
                end_date = campaign_end_date,
                advertiser_code = form.cleaned_data['advertiser_code'],
                print_campaign = print_flag,
                print_campaign_budget = form.cleaned_data['print_budget'],
                digital_campaign = digital_flag,
                digital_campaign_budget = form.cleaned_data['digital_budget'],
                campaign_budget = form.cleaned_data['campaign_budget'],
                external_id = campaign_id
            )
        except PATSException as error:
            messages.error(self.request, 'Create CampaignDetails object failed: %s' % error)

        buyer_api = self.get_buyer_api_handle()
        pats_campaign_id = None

        # use the campaigndetails object to make a campaign
        try:
            pats_campaign_id = buyer_api.create_campaign(campaign_details)
        except PATSException as error:
            messages.error(self.request, 'Create Campaign failed: %s' % error)
        else:
            messages.success(self.request, 'Create Campaign succeeded: campaign ID is %s' % pats_campaign_id)

            # now that campaign creation was successful, make an RFP
            try:
                rfp_id = buyer_api.send_rfp(
                    user_id=user_id,
                    campaign_id=pats_campaign_id,
                    budget_amount=rfp_budget_amount,
                    start_date=rfp_start_date, end_date=rfp_end_date, respond_by_date=rfp_respond_by_date,
                    comments=rfp_comments,
                    publisher_id=publisher_id,
                    publisher_emails=[publisher_email],
                    media_print=print_flag, media_online=digital_flag,
                    strategy=strategy,
                    requested_products=requested_products,
                    attachments=attachments
                )
            except PATSException as error:
                messages.error(self.request, 'Submit RFP failed: %s' % error)
            else:
                if rfp_id:
                    messages.success(self.request, 'RFP sent successfully! RFP ID is %s' % rfp_id)
                else:
                    messages.error(self.request, 'Submit RFP failed, blank response: %s' % rfp_id)
        return super(Buyer_CreateRFPWithCampaignView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateRFPWithCampaignView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_group_id'] = self.get_agency_group_id()
        context_data['agency_user_id'] = self.get_agency_user_id()
        return context_data

class Buyer_CreateOrderRawView(PATSAPIMixin, FormView):
    form_class = Buyer_CreateOrderRawForm
    success_url = reverse_lazy('buyer_orders_create_raw')

    def get(self, *args, **kwargs):
        # self.clear_curl_history()
        return super(Buyer_CreateOrderRawView, self).get(*args, **kwargs)

    def get_initial(self):
        return {
            'agency_id': self.get_agency_id(),
            'agency_group_id': self.get_agency_group_id(),
            'user_id': self.get_agency_user_id(),
        }

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        agency_group_id = form.cleaned_data.get('agency_group_id')
        user_id = form.cleaned_data.get('user_id')
        # convert the text string to a json object
        try:
            data = json.loads(form.cleaned_data.get('payload'))
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload: %s <br />Try using jsonlint.com to fix it!' % json_error)
        else:    
            # take submitted values and call API - raw version
            result = ''
            try:
                result = buyer_api.send_order_raw(agency_id=agency_id, agency_group_id=agency_group_id, user_id=user_id, data=data)
            except PATSException as error:
                messages.error(self.request, 'Submit Order failed: %s' % error)
            else:
                if result['status'] == u'SUCCESSFUL':
                    messages.success(self.request, 'Order sent successfully! ID %s, version %s' % (result[u'publicId'], result[u'version']))
                else:
                    messages.error(self.request, 'Submit Order failed: %s' % error)
        return super(Buyer_CreateOrderRawView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateOrderRawView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_group_id'] = self.get_agency_group_id()
        context_data['user_id'] = self.get_agency_user_id()
        return context_data

class Buyer_CreateOrderFromRevisionView(PATSAPIMixin, FormView):
    form_class = Buyer_CreateOrderRawForm
    success_url = reverse_lazy('buyer_orders_create_from_revision')
    campaign_id = None
    order_id = None
    version = None
    revision = None

    def get(self, *args, **kwargs):
        # self.clear_curl_history()
        if 'campaign_id' in self.kwargs:
            self.campaign_id = self.kwargs.get('campaign_id', None)
        if 'order_id' in self.kwargs:
            self.order_id = self.kwargs.get('order_id', None)
        if 'version' in self.kwargs:
            self.version = self.kwargs.get('version', None)
        if 'revision' in self.kwargs:
            self.revision = self.kwargs.get('revision', None)
        return super(Buyer_CreateOrderFromRevisionView, self).get(*args, **kwargs)

    def get_initial(self):
        payload = {
            "blah": "mypayload to be filled in"
        }
        return {
            'seller_email': self.get_publisher_user(),
            'agency_id': self.get_agency_id(),
            'agency_group_id': self.get_agency_group_id(),
            'user_id': self.get_agency_user_id(),
            'payload': payload
        }

    def form_valid(self, form):
        buyer_api = self.get_buyer_api_handle()
        agency_group_id = form.cleaned_data.get('agency_group_id')
        user_id = form.cleaned_data.get('user_id')
        # convert the text string to a json object
        try:
            data = json.loads(form.cleaned_data.get('payload'))
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload: %s <br />Try using jsonlint.com to fix it!' % json_error)
        else:    
            # take submitted values and call API - raw version
            result = ''
            try:
                result = buyer_api.send_order_raw(agency_id=agency_id, agency_group_id=agency_group_id, user_id=user_id, data=data)
            except PATSException as error:
                messages.error(self.request, 'Submit Order failed: %s' % error)
            else:
                if result['status'] == u'SUCCESSFUL':
                    messages.success(self.request, 'Order sent successfully! ID %s, version %s' % (result[u'publicId'], result[u'version']))
                else:
                    messages.error(self.request, 'Submit Order failed: %s' % error)
        return super(Buyer_CreateOrderFromRevisionView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateOrderFromRevisionView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_group_id'] = self.get_agency_group_id()
        context_data['user_id'] = self.get_agency_user_id()
        context_data['campaign_id'] = self.campaign_id or ''
        context_data['order_id'] = self.order_id or ''
        context_data['version'] = self.version or ''
        context_data['revision'] = self.revision or ''
        return context_data

class Buyer_CreateOrderWithCampaignView(PATSAPIMixin, FormView, TestOrdersMixin):
    form_class = Buyer_CreateOrderWithCampaignForm
    success_url = reverse_lazy('buyer_orders_create_with_campaign')

    def dispatch(self, *args, **kwargs):
        self.test_data_id = self.kwargs.get('test_data_id', self.request.GET.get('testfile', None))
        if self.test_data_id:
            self.test_data = self.load_test_file(self.test_data_id)
        self.test_files_list = self.get_test_files_list() # also saves to session
        return super(Buyer_CreateOrderWithCampaignView, self).dispatch(*args, **kwargs)
 
    def get_initial(self):
        initial = {
            'advertiser_code': self.get_example_advertiser_id(),
            'agency_id': self.get_agency_id(),
            'agency_group_id': self.get_agency_group_id(),
            'campaign_start_date':  self.get_example_campaign_start_date(),
            'campaign_end_date':  self.get_example_campaign_end_date(),
            'respond_by_date':  self.get_example_respond_by_date(),
            'print_flag': True,
            'digital_flag': True,
            'campaign_budget': self.get_example_budget(),
            'campaign_id': self.get_example_campaign_id(),
            'campaign_name': self.get_example_campaign_name(),
            'user_id': self.get_agency_user_id(),
            'publisher_id': self.get_publisher_id(),
            'publisher_email': self.get_publisher_user()
        }
        if self.test_data_id:
            if 'campaign_name' in self.test_data:
                initial['campaign_name'] = self.test_data['campaign_name'] + " " + self.get_example_campaign_id()
            if 'payload_1' in self.test_data:
                initial['payload_1'] = json.dumps(
                    self.test_data['payload_1'],
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            if 'payload_2' in self.test_data:
                initial['payload_2'] = json.dumps(
                    self.test_data['payload_2'],
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
        return initial

    def form_valid(self, form):
        organisation_id = form.cleaned_data.get('agency_id')
        agency_group_id = form.cleaned_data.get('agency_group_id')
        user_id = form.cleaned_data.get('user_id')
        publisher_id = form.cleaned_data.get('publisher_id')
        publisher_email = form.cleaned_data.get('publisher_email')
        campaign_id = form.cleaned_data.get('campaign_id')
        # because we use forms.DateField, the dates come through already formatted as datetime objects
        campaign_start_date = form.cleaned_data.get('campaign_start_date')
        campaign_end_date = form.cleaned_data.get('campaign_end_date')
        respond_by_date = form.cleaned_data.get('respond_by_date')
        try:
            campaign_details = CampaignDetails(
                organisation_id = organisation_id,
                agency_group_id = agency_group_id,
                user_id = user_id,
                campaign_name = form.cleaned_data['campaign_name'],
                start_date = campaign_start_date,
                end_date = campaign_end_date,
                advertiser_code = form.cleaned_data['advertiser_code'],
                print_campaign = form.cleaned_data['print_flag'],
                print_campaign_budget = form.cleaned_data['print_budget'],
                digital_campaign = form.cleaned_data['digital_flag'],
                digital_campaign_budget = form.cleaned_data['digital_budget'],
                campaign_budget = form.cleaned_data['campaign_budget'],
                external_id = campaign_id
            )
        except PATSException as error:
            messages.error(self.request, 'Create CampaignDetails object failed: %s' % error)
        # convert the text string to a json object - best to check that the JSON is valid before 
        original_payload_1 = form.cleaned_data.get('payload_1')
        original_payload_2 = form.cleaned_data.get('payload_2')
        replaced_payload_1 = self.replace_template_strings(payload=original_payload_1, publisher_id=publisher_id, publisher_email=publisher_email, user_id=user_id, campaign_id=campaign_id, campaign_start_date=campaign_start_date, campaign_end_date=campaign_end_date, respond_by_date=respond_by_date)
        if original_payload_2:
            replaced_payload_2 = self.replace_template_strings(payload=original_payload_2, publisher_id=publisher_id, publisher_email=publisher_email, user_id=user_id, campaign_id=campaign_id, campaign_start_date=campaign_start_date, campaign_end_date=campaign_end_date, respond_by_date=respond_by_date)
        try:
            data_1 = json.loads(replaced_payload_1)
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload 1: %s <br />Try using jsonlint.com to fix it!' % json_error)
        else:
            if original_payload_2:
                try:
                    data_2 = json.loads(replaced_payload_2)
                except ValueError as json_error:
                    messages.error(self.request, 'Problem with JSON payload 2: %s <br />Try using jsonlint.com to fix it!' % json_error)
            # payload(s) is/are valid JSON, so try to create campaign and order
            buyer_api = self.get_buyer_api_handle()
            response = ''
            try:
                pats_campaign_id = buyer_api.create_campaign(campaign_details)
            except PATSException as error:
                messages.error(self.request, 'Create Campaign failed: %s' % error)
            else:
                messages.success(self.request, 'Create Campaign succeeded: campaign ID is %s' % pats_campaign_id)
                result = ''
                try:
                    order_1_id = buyer_api.send_order_raw(agency_id=organisation_id, agency_group_id=agency_group_id, user_id=user_id, campaign_id=pats_campaign_id, data=data_1)
                except PATSException as error:
                    messages.error(self.request, 'Submit Order 1 failed: %s' % error)
                else:
                    messages.success(self.request, 'Order 1 sent successfully! ID %s' % order_1_id)
                    if original_payload_2:
                        try:
                            order_2_id = buyer_api.send_order_raw(agency_id=organisation_id, agency_group_id=agency_group_id, user_id=user_id, campaign_id=pats_campaign_id, data=data_2)
                        except PATSException as error:
                            messages.error(self.request, 'Submit Order 2 failed: %s' % error)
                        else:
                            messages.success(self.request, 'Order 2 sent successfully! ID %s' % order_2_id)
        return super(Buyer_CreateOrderWithCampaignView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateOrderWithCampaignView, self).get_context_data(*args, **kwargs)
        if self.test_data_id:
            context_data['test_data_id'] = self.test_data_id
            context_data['json_test_file_data'] = self.test_data
        context_data['test_files_list'] = self.test_files_list
        context_data['test_file_ids'] = sorted(self.test_files_list.keys())
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_group_id'] = self.get_agency_group_id()
        context_data['agency_user_id'] = self.get_agency_user_id()
        return context_data

class Buyer_CreateOrderView(PATSAPIMixin, FormView):
    form_class = Buyer_CreateOrderForm
    success_url = reverse_lazy('buyer_orders_create')

    def get(self, *args, **kwargs):
        self.clear_curl_history()
        return super(Buyer_CreateOrderView, self).get(*args, **kwargs)

    def get_initial(self):
        return {}

    def form_valid(self, form):
        messages.error(self.request, 'Not yet implemented!')
        return super(Buyer_CreateOrderView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_CreateOrderView, self).get_context_data(*args, **kwargs)
        return context_data

class Buyer_ListOrdersView(PATSAPIMixin, ListView):
    since_date = None

    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.since_date = self.request.GET.get('since_date', None)
        self.page_size = self.request.GET.get('page_size', 25)
        self.page = self.request.GET.get('page', 1)
        if not self.since_date:
            one_month_ago = datetime.datetime.today()-datetime.timedelta(7)
            self.since_date = one_month_ago.strftime("%Y-%m-%d")
        list_orders_response = None
        try:
            list_orders_response = buyer_api.list_orders(
                user_id = self.get_agency_user_id(),
                since_date=datetime.datetime.strptime(self.since_date, "%Y-%m-%d"),
                page_size=self.page_size, page=self.page
            )
        except PATSException as error:
            messages.error(self.request, "Can't get list of orders, error: %s" % error)
        return list_orders_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListOrdersView, self).get_context_data(*args, **kwargs)
        context_data['since_date'] = self.since_date
        context_data['page_size'] = self.page_size
        context_data['page'] = self.page
        return context_data

class Buyer_ListOrderRevisionsView(PATSAPIMixin, ListView):
    # Pre 2015.8, this would list *all* outstanding revisions.
    # Now it only lists revisions for a given order.
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.version = self.kwargs.get('version', None)
        user_id = self.get_agency_user_id()
        order_revisions_response = None
        try:
            order_revisions_response = buyer_api.list_order_revisions(
                user_id=user_id,
                campaign_id=self.campaign_id,
                order_id=self.order_id,
                version=self.version
            )
        except PATSException as error:
            messages.error(self.request, "List order revisions failed. Error: %s" % error)
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListOrderRevisionsView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        return context_data

class Buyer_OrderRevisionDetailView(PATSAPIMixin, DetailView):
    order_id = None

    def get_object(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.version = self.kwargs.get('version', None)
        self.revision = self.kwargs.get('revision', None)
        order_detail_response = None
        try:
            order_detail_response = buyer_api.view_order_revision_detail(user_id=self.get_agency_user_id(), campaign_id=self.campaign_id, order_id=self.order_id, version=self.version, revision=self.revision)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load order revision: %s' % error)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_OrderRevisionDetailView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        context_data['revision'] = self.revision
        return context_data

class Buyer_ListProposalsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        buyer_proposals_response = None
        try:
            buyer_proposals_response = buyer_api.list_proposals(rfp_id=self.rfp_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t get list of proposals for RFP %s: %s' % (self.rfp_id, error))
        return buyer_proposals_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListProposalsView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Buyer_ListPublisherProductsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        buyer_api = self.get_buyer_api_handle()
        self.vendor_id = self.kwargs.get('publisher_id', None)
        product_catalogue_response = {}
        try:
            product_catalogue_response = buyer_api.list_products(vendor_id=self.vendor_id, user_id=self.get_agency_user_id())
            return product_catalogue_response
        except PATSException as error:
            messages.error(self.request, "List products failed. Error: %s" % error)
        return

    def get_context_data(self, *args, **kwargs):
        context_data = super(Buyer_ListPublisherProductsView, self).get_context_data(*args, **kwargs)
        context_data['publisher_id'] = self.vendor_id
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
        # if no search params are set, the list can be very long, so limit it to just changes in the last week
        if not self.search_updated_date and not self.search_name and not self.agency_id:
            one_week_ago = datetime.datetime.today()-datetime.timedelta(7)
            self.search_updated_date = one_week_ago.strftime("%Y-%m-%d")
        self.user_id = self.get_publisher_user()
        agencies_response = ''
        try:
            agencies_response = seller_api.get_buyers(user_id=self.user_id, agency_id=self.agency_id, name=self.search_name, last_updated_date=self.search_updated_date)
        except PATSException as error:
            messages.error(self.request, "Get agencies failed. Error: %s" % error)
        else:
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
    status = None
    status_choices = ("SENT","VENDOR_ACCESSED","OPENED","PAST_DUE","NEW","PROPOSAL_RECEIVED","RESPONDED")

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.start_date = self.request.GET.get('start_date', None)
        self.status = self.request.GET.get('status', None)
        if not self.start_date:
            one_month_ago = datetime.datetime.today()-datetime.timedelta(30)
            self.start_date = one_month_ago.strftime("%Y-%m-%d")
        self.end_date = self.request.GET.get('end_date', None)
        if not self.end_date:
            self.end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        seller_rfps_response = ''
        try:
            seller_rfps_response = seller_api.list_rfps(
                start_date=datetime.datetime.strptime(self.start_date, "%Y-%m-%d"),
                end_date=datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
            )
        except PATSException as error:
            messages.error(self.request, "List RFPs failed. Error: %s" % error)
        return seller_rfps_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListRFPsView, self).get_context_data(*args, **kwargs)
        context_data['start_date'] = self.start_date
        context_data['end_date'] = self.end_date
        context_data['status'] = self.status
        context_data['status_choices'] = self.status_choices
        return context_data

class Seller_RFPDetailView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        seller_api = self.get_buyer_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        rfp_detail_response = ''
        try:
            rfp_detail_response = seller_api.view_rfp_detail(rfp_id=self.rfp_id)
        except PATSException as error:
            messages.error(self.request, "Get RFP detail failed. Error: %s" % error)
        return rfp_detail_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_RFPDetailView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Seller_ListProposalsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        seller_proposals_response = None
        try:
            seller_proposals_response = seller_api.list_proposals(rfp_id=self.rfp_id)
        except PATSException as error:
            messages.error(self.request, 'List proposals failed. Error: %s' % error)
        return seller_proposals_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListProposalsView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Seller_ProposalDetailView(PATSAPIMixin, DetailView):
    proposal_id = None

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        proposal_detail_response = None
        try:
            proposal_detail_response = seller_api.view_proposal_detail(proposal_id=self.proposal_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load proposal: %s' % error)
        return proposal_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ProposalDetailView, self).get_context_data(*args, **kwargs)
        context_data['proposal_id'] = self.proposal_id
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Seller_CreateProposalRawView(PATSAPIMixin, FormView):
    form_class = Seller_CreateProposalRawForm

    def get(self, *args, **kwargs):
        if 'rfp_id' in self.kwargs:
            self.rfp_id = self.kwargs.get('rfp_id', None)
        return super(Seller_CreateProposalRawView, self).get(*args, **kwargs)
        
    def get_success_url(self):
        return reverse_lazy('seller_rfps_proposals_create_raw', kwargs={'rfp_id':self.rfp_id})

    def get_initial(self):
        if 'rfp_id' in self.kwargs:
            self.rfp_id = self.kwargs.get('rfp_id', None)
        return {
            'rfp_id': self.rfp_id,
            'vendor_id': self.get_publisher_id()
        }

    def form_valid(self, form):
        seller_api = self.get_seller_api_handle()
        # convert the text string to a json object
        try:
            data = json.loads(form.cleaned_data.get('payload'))
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload: %s <br />Try using jsonlint.com to fix it!' % json_error)
        else:    
            # take submitted values and call API - raw version
            result = ''
            try:
                result = seller_api.send_proposal_raw(vendor_id=self.get_publisher_id(), data=data)
            except PATSException as error:
                messages.error(self.request, 'Submit Proposal failed: %s' % error)
            else:
                if result['status'] == u'SUCCESSFUL':
                    messages.success(self.request, 'Proposal sent successfully! result is %s' % result)
                else:
                    messages.error(self.request, 'Submit Proposal failed: %s' % result)
        return super(Seller_CreateProposalRawView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_CreateProposalRawView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        return context_data

class Seller_DownloadRFPAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.agency_id = self.kwargs.get('agency_id', None)
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        attachment_response = ''
        try:
            attachment_response = seller_api.get_rfp_attachment(agency_id=self.agency_id, rfp_id=self.rfp_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Can't get attachment, error: %s" % error)
        return attachment_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_DownloadRFPAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['agency_id'] = self.agency_id
        context_data['rfp_id'] = self.rfp_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Seller_ListOrdersView(PATSAPIMixin, ListView):
    since_date = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.since_date = self.request.GET.get('since_date', None)
        self.page_size = self.request.GET.get('page_size', 25)
        self.page = self.request.GET.get('page', 1)
        if not self.since_date:
            one_week_ago = datetime.datetime.today()-datetime.timedelta(7)
            self.since_date = one_week_ago.strftime("%Y-%m-%d")
        order_revisions_response = None
        try:
            order_revisions_response = seller_api.list_orders(
                since_date=datetime.datetime.strptime(self.since_date, "%Y-%m-%d"),
                page_size=self.page_size, page=self.page
            )
        except PATSException as error:
            messages.error(self.request, "Can't get orders list, error: %s" % error)
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListOrdersView, self).get_context_data(*args, **kwargs)
        context_data['since_date'] = self.since_date
        return context_data

class Seller_ListOrderVersionsView(PATSAPIMixin, ListView):
    start_date = None
    end_date = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.since_date = self.request.GET.get('since_date', None)
        if not self.since_date:
            one_week_ago = datetime.datetime.today()-datetime.timedelta(7)
            self.since_date = one_week_ago.strftime("%Y-%m-%d")
        order_revisions_response = None
        try:
            order_revisions_response = seller_api.list_orders(
                since_date=datetime.datetime.strptime(self.since_date, "%Y-%m-%d")
            )
        except PATSException as error:
            messages.error(self.request, "Can't get orders list, error: %s" % error)
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListOrderVersionsView, self).get_context_data(*args, **kwargs)
        context_data['since_date'] = self.since_date
        return context_data

class Seller_OrderVersionsView(PATSAPIMixin, ListView):
    campaign_id = None
    order_id = None

    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.user_id = self.get_publisher_user()
        order_versions_response = None
        try:
            order_versions_response = seller_api.list_order_versions(user_id=self.user_id, campaign_id=self.campaign_id, order_id=self.order_id)
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load order versions: %s' % error)
        return order_versions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderVersionsView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        return context_data

class Seller_OrderVersionDetailView(PATSAPIMixin, DetailView):
    campaign_id = None
    order_id = None
    version = None

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        # version defaults to 0
        self.version = self.kwargs.get('version', 0)
        order_detail_response = None
        try:
            order_detail_response = seller_api.view_order_version_detail(campaign_id=self.campaign_id, order_id=self.order_id, version=self.version)
        except PATSException as error:
            messages.error(self.request, "Can't get order detail, error: %s" % error)
        return order_detail_response
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderVersionDetailView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        return context_data

class Seller_ListOrderEventsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        seller_events_response = None
        try:
            seller_events_response = seller_api.list_order_events(order_id=self.order_id)
        except PATSException as error:
            messages.error(self.request, 'Cannot list events: %s' % error)
        return seller_events_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListOrderEventsView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        return context_data

class Seller_ViewOrderAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            order_attachment_response = seller_api.get_order_attachment(user_id=self.get_publisher_user(), order_id=self.order_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get order attachment failed. Error: %s" % error)
        return order_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ViewOrderAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Seller_DownloadOrderAttachmentView(PATSAPIMixin, DetailView):
    def get(self, *args, **kwargs):
        old_response = super(Seller_DownloadOrderAttachmentView, self).get(*args, **kwargs)
        # file_contents = self.order_attachment['contents']
        file_contents = base64.b64decode(self.order_attachment['contents'])
        http_response = HttpResponse(content_type=self.order_attachment['mimeType'])
        # the "attachment" version pops up a "do you wish to download?" window
        # http_response['Content-Disposition'] = 'attachment; filename="'+self.order_attachment['name']+'"'
        http_response['Content-Disposition'] = 'filename="'+self.order_attachment['name']+'"'
        # http_response['Content-Length'] = len(file_contents)
        http_response.write(file_contents)
        return http_response

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            order_attachment_response = seller_api.get_order_attachment(user_id=self.get_publisher_user(), order_id=self.order_id, attachment_id=self.attachment_id)
            self.order_attachment = order_attachment_response
        except PATSException as error:
            messages.error(self.request, "Get order attachment failed. Error: %s" % error)
        return order_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_DownloadOrderAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Seller_ViewProposalAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        order_attachment_response = ''
        try:
            proposal_attachment_response = seller_api.get_proposal_attachment(user_id=self.get_publisher_user(), proposal_id=self.proposal_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get proposal attachment failed. Error: %s" % error)
        return proposal_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ViewProposalAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        context_data['proposal_id'] = self.proposal_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Seller_DownloadProposalAttachmentView(PATSAPIMixin, DetailView):
    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.rfp_id = self.kwargs.get('rfp_id', None)
        self.proposal_id = self.kwargs.get('proposal_id', None)
        self.attachment_id = self.kwargs.get('attachment_id', None)
        try:
            proposal_attachment_response = buyer_api.get_proposal_attachment(user_id=self.get_publisher_user(), proposal_id=self.proposal_id, attachment_id=self.attachment_id)
        except PATSException as error:
            messages.error(self.request, "Get proposal attachment failed. Error: %s" % error)
        return proposal_attachment_response
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_DownloadProposalAttachmentView, self).get_context_data(*args, **kwargs)
        context_data['rfp_id'] = self.rfp_id
        context_data['proposal_id'] = self.proposal_id
        context_data['attachment_id'] = self.attachment_id
        return context_data

class Seller_ListOrderRevisionsView(PATSAPIMixin, ListView):
    def get_queryset(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.campaign_id = self.kwargs.get('campaign_id', None)
        self.order_id = self.kwargs.get('order_id', None)
        self.version = self.kwargs.get('version', None)
        user_id = self.get_agency_user_id()
        order_revisions_response = None
        try:
            order_revisions_response = seller_api.list_order_revisions(
                user_id=user_id,
                campaign_id=self.campaign_id,
                order_id=self.order_id,
                version=self.version
            )
        except PATSException as error:
            messages.error(self.request, "List order revisions failed. Error: %s" % error)
        return order_revisions_response

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListOrderRevisionsView, self).get_context_data(*args, **kwargs)
        context_data['campaign_id'] = self.campaign_id
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        return context_data

class Seller_OrderRevisionDetailView(PATSAPIMixin, DetailView):
    order_id = None
    version = None
    revision = None

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.order_id = self.kwargs.get('order_id', None)
        self.version = self.kwargs.get('version', None)
        self.revision = self.kwargs.get('revision', None)
        order_revision_detail = None
        try:
            order_revision_detail = seller_api.view_order_revision_detail(order_id=self.order_id, version=self.version, revision=self.revision)
        except PATSException as error:
            messages.error(self.request, "Can't get revision detail, error: %s" % error)
        return order_revision_detail

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderRevisionDetailView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        context_data['revision'] = self.revision
        return context_data

class Seller_OrderRespondView(PATSAPIMixin, FormView):
    order_id = None
    version = None
    order_detail = None
    form_class = Seller_OrderRespondForm

    def get_success_url(self):
        return reverse_lazy('seller_orders_respond', kwargs={'order_id':self.order_id, 'version':self.version})
    
    def get(self, *args, **kwargs):
        if 'order_id' in self.kwargs:
            seller_api = self.get_seller_api_handle()
            self.order_id = self.kwargs.get('order_id', None)
            self.user_id = self.get_publisher_user()
            # version defaults to 0
            self.version = self.kwargs.get('version', 0)
            # get rid of minor version component in case it's there
            self.version = int(float(self.version))
            order_detail_response = None
            try:
                order_detail_response = seller_api.view_order_version_detail(campaign_id=self.campaign_id, order_id=self.order_id, version=self.version)
            except PATSException as error:
                messages.error(self.request, "Get order detail failed. Error: %s" % error)
            self.order_detail = order_detail_response
        return super(Seller_OrderRespondView, self).get(*args, **kwargs)

    def get_initial(self):
        initial_values = {
            'order_id': self.order_id
        }
        if hasattr(self, 'user_id'):
            initial_values.update({
                'user_id': self.user_id,
            })
        return initial_values

    def form_valid(self, form):
        # fill in order id and version in case we need to display errors
        self.order_id = self.kwargs.get('order_id', None)
        # version defaults to 0
        self.version = self.kwargs.get('version', 0)
        # get rid of minor version component in case it's there
        self.version = int(float(self.version))

        seller_api = self.get_seller_api_handle()
        self.user_id = form.cleaned_data.get('user_id')
        self.order_id = form.cleaned_data.get('order_id')
        status = form.cleaned_data.get('status')
        comments = form.cleaned_data.get('comments')
        response = ''
        try:
            response = seller_api.respond_to_order(user_id=self.user_id, order_id=self.order_id, status=status, comments=comments)
        except PATSException as error:
            messages.error(self.request, 'Respond to Order failed: %s' % error)
        else:
            # response is blank for successful responses
            messages.success(self.request, 'Response sent successfully')
        return super(Seller_OrderRespondView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderRespondView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        context_data['object'] = self.order_detail
        return context_data

class Seller_OrderReviseView(PATSAPIMixin, FormView):
    order_id = None
    version = None
    order_detail = None
    form_class = Seller_OrderReviseForm

    def get_success_url(self):
        return reverse_lazy('seller_orders_revise', kwargs={'order_id':self.order_id, 'version':self.version})
    
    def get(self, *args, **kwargs):
        if 'order_id' in self.kwargs:
            seller_api = self.get_seller_api_handle()
            self.order_id = self.kwargs.get('order_id', None)
            # version defaults to 0
            self.version = self.kwargs.get('version', 0)
            # get rid of minor version component in case it's there
            self.version = int(float(self.version))
        return super(Seller_OrderReviseView, self).get(*args, **kwargs)

    def get_initial(self):
        return {
            'order_id': self.order_id
        }

    def form_valid(self, form):
        # fill in order id and version in case we need to display errors
        self.order_id = self.kwargs.get('order_id', None)
        # version defaults to 0
        self.version = self.kwargs.get('version', 0)
        # get rid of minor version component in case it's there
        self.version = int(float(self.version))

        seller_api = self.get_seller_api_handle()
        user_id = form.cleaned_data.get('user_id')
        self.order_id = form.cleaned_data.get('order_id')
        status = form.cleaned_data.get('status')
        # convert the text string to a json object
        try:
            data = json.loads(form.cleaned_data.get('payload'))
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload: %s <br />Try using jsonlint.com to fix it!' % json_error)
        else:    
            # take submitted values and call API - raw version
            result = ''
            try:
                result = seller_api.send_order_revision_raw(user_id=user_id, order_id=self.order_id, data=data)
            except PATSException as error:
                messages.error(self.request, 'Submit Order Revision failed: %s' % error)
            else:
                if result['status'] == u'SUCCESSFUL':
                    messages.success(self.request, 'Order revision sent successfully! ID %s, version %s' % (result[u'publicId'], result[u'version']))
                else:
                    messages.error(self.request, 'Submit Order Revision failed: %s' % error)
        return super(Seller_OrderReviseView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_OrderReviseView, self).get_context_data(*args, **kwargs)
        context_data['order_id'] = self.order_id
        context_data['version'] = self.version
        context_data['object'] = self.order_detail
        return context_data

class Seller_GetMediaPropertiesView(PATSAPIMixin, TemplateView):
    media_property_details = None

    def get(self, *args, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.publisher_id = self.get_publisher_id()
        self.media_property_details = seller_api.get_media_property_details(organisation_id=self.publisher_id)
        return super(Seller_GetMediaPropertiesView, self).get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_GetMediaPropertiesView, self).get_context_data(*args, **kwargs)
        context_data['media_properties'] = self.media_property_details
        context_data['publisher_id'] = self.publisher_id
        return context_data

class Seller_ListProductsView(PATSAPIMixin, TemplateView):
    products = None

    def get(self, *args, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.publisher_id = self.get_publisher_id()
        self.products = seller_api.list_products(organisation_id=self.publisher_id)
        return super(Seller_ListProductsView, self).get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_ListProductsView, self).get_context_data(*args, **kwargs)
        context_data['products'] = self.products
        context_data['publisher_id'] = self.publisher_id
        return context_data

class Seller_CreateProductView(PATSAPIMixin, FormView):
    product_id = None
    form_class = Seller_ProductForm

    def form_valid(self, form, **kwargs):
        seller_api = self.get_seller_api_handle()
        product = Product(
            productId = form.cleaned_data['external_product_id'],
            status = form.cleaned_data['status'],
            mediaType = form.cleaned_data['media_type'],
            name = form.cleaned_data['name'],
            mediaPropertyId = form.cleaned_data['media_property_id'],
            currencyCode = form.cleaned_data['currency_code'],
            agencyEnabled = form.cleaned_data['agency_enabled'],
            clientId = form.cleaned_data['client_id'],
            buyType = form.cleaned_data['buy_type'],
            buyCategory = form.cleaned_data['buy_category'],
            size = form.cleaned_data['size'],
            position = form.cleaned_data['position'],
            dimensions = form.cleaned_data['dimensions'],
            costMethod = form.cleaned_data['cost_method'],
            unitType = form.cleaned_data['unit_type'],
            rate = form.cleaned_data['rate'],
            units = form.cleaned_data['units'],
            cost = form.cleaned_data['cost'],
            section = form.cleaned_data['section'],
            subsection = form.cleaned_data['subsection'],
            positionGuaranteed = form.cleaned_data['position_guaranteed'],
            comments = form.cleaned_data['comments']
        )
        result = ''
        try:
            response = seller_api.create_product(product=product)
        except PATSException as error:
            messages.error(self.request, 'Create product failed: %s' % error)
        else:
            messages.success(self.request, 'Product Created!')
        return super(Seller_CreateProductView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('seller_metadata_products_update', kwargs={'product_id':self.product_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_CreateProductView, self).get_context_data(*args, **kwargs)
        context_data['product_id'] = self.product_id
        return context_data

class Seller_UpdateMediaPropertiesView(PATSAPIMixin, FormView):
    form_class = Seller_MediaPropertyForm
    def form_valid(self, form, **kwargs):
        seller_api = self.get_seller_api_handle()
        payload = form.cleaned_data.get('payload', '')
        user_id = form.cleaned_data.get('user_id', '')
        vendor_id = form.cleaned_data.get('vendor_id', '')
        media_property_id = form.cleaned_data.get('media_property_id', '')
        field_id = form.cleaned_data.get('field_id', '')
        try:
            data = json.loads(form.cleaned_data.get('payload'))
        except ValueError as json_error:
            messages.error(self.request, 'Problem with JSON payload: %s <br />Try using jsonlint.com to fix it!' % json_error)
        try:
            response = seller_api.update_media_property_fields(user_id=user_id, organisation_id=vendor_id, media_property_id=media_property_id, field_family=field_id, payload=data)
        except PATSException as error:
            messages.error(self.request, 'Update media property fields failed: %s' % error)
        else:
            messages.success(self.request, 'Media property fields updated!')
        return super(Seller_UpdateMediaPropertiesView, self).form_valid(form)

    def get_initial(self):
        object = self.get_object()
        self.media_property_id = self.kwargs.get('media_property_id', None)
        self.field_id = self.kwargs.get('field_id', None)

        return {
            'media_property_id': self.media_property_id,
            'user_id': self.get_publisher_user(),
            'vendor_id': self.get_publisher_id(),
            'field_id': self.field_id,
            'payload': ''
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('seller_metadata_mediaproperties_update', kwargs={'media_property_id':self.media_property_id, 'field_id':self.field_id})

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        #self.product_id = self.kwargs.get('product_id', None)
        #products_list = None
        #try:
        #    products_list = seller_api.list_products(user_id=self.get_publisher_user(), organisation_id=self.get_publisher_id())
        #except PATSException as error:
        #    messages.error(self.request, 'Couldn''t load products: %s' % error)
        ## now find the one we want, or return nothing
        #for product in products_list:
        #    if product['id'] == self.product_id:
        #        return product
        return None
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_UpdateMediaPropertiesView, self).get_context_data(*args, **kwargs)
        context_data['media_property_id'] = self.media_property_id
        context_data['field_id'] = self.field_id
        return context_data

class Seller_UpdateProductView(PATSAPIMixin, FormView):
    product_id = None
    form_class = Seller_ProductForm

    def form_valid(self, form, **kwargs):
        seller_api = self.get_seller_api_handle()
        product = Product(
            productId = form.cleaned_data['external_product_id'],
            status = form.cleaned_data['status'],
            mediaType = form.cleaned_data['media_type'],
            name = form.cleaned_data['name'],
            mediaPropertyId = form.cleaned_data['media_property_id'],
            currencyCode = form.cleaned_data['currency_code'],
            agencyEnabled = form.cleaned_data['agency_enabled'],
            clientId = form.cleaned_data['client_id'],
            buyType = form.cleaned_data['buy_type'],
            buyCategory = form.cleaned_data['buy_category'],
            size = form.cleaned_data['size'],
            position = form.cleaned_data['position'],
            dimensions = form.cleaned_data['dimensions'],
            costMethod = form.cleaned_data['cost_method'],
            unitType = form.cleaned_data['unit_type'],
            rate = form.cleaned_data['rate'],
            units = form.cleaned_data['units'],
            cost = form.cleaned_data['cost'],
            section = form.cleaned_data['section'],
            subsection = form.cleaned_data['subsection'],
            positionGuaranteed = form.cleaned_data['position_guaranteed'],
            comments = form.cleaned_data['comments']
        )
        result = ''
        try:
            response = seller_api.update_product(product_id=self.product_id, product=product)
        except PATSException as error:
            messages.error(self.request, 'Update product failed: %s' % error)
        else:
            messages.success(self.request, 'Product updated!')
        return super(Seller_UpdateProductView, self).form_valid(form)

    def get_initial(self):
        object = self.get_object()
        print_flag = False; digital_flag = False
        print_budget = 0; digital_budget = 0

        return {
            # "id": "3465316d-1b09-4b0c-b171-f453693ced9b",
            'external_product_id': object.get('productId', None),
            'status': object.get('status', None),
            'name': object.get('name', None),
            'media_property_id': object.get('mediaPropertyId', None),
            'product_id': object.get('productId', None),
            'agency_enabled': object.get('agencyEnabled', None),
            'media_type': object.get('mediaType', None),
            'currency_code': object.get('currencyCode', None),
            'buy_type': object['attributes'].get('buyType', None),
            'buy_category': object['attributes'].get('buyCategory', None),
            'rate': object['attributes'].get('rate', None),
            'units': object['attributes'].get('units', None),
            'cost': object['attributes'].get('cost', None),
            'cost_method': object['attributes'].get('costMethod', None),
            'unit_type': object['attributes'].get('unitType', None),
            'size': object['attributes'].get('size', None),
            'position': object['attributes'].get('position', None),
            'dimensions': object['attributes'].get('dimensions', None),
            'section': object['attributes'].get('section', None),
            'subsection': object['attributes'].get('subsection', None),
            'position_guaranteed': object['attributes'].get('positionGuaranteed', None),
            'comments': object['attributes'].get('comments', None)
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('seller_metadata_products_update', kwargs={'product_id':self.product_id})

    def get_object(self, **kwargs):
        seller_api = self.get_seller_api_handle()
        self.product_id = self.kwargs.get('product_id', None)
        products_list = None
        try:
            products_list = seller_api.list_products(user_id=self.get_publisher_user(), organisation_id=self.get_publisher_id())
        except PATSException as error:
            messages.error(self.request, 'Couldn''t load products: %s' % error)
        # now find the one we want, or return nothing
        for product in products_list:
            if product['id'] == self.product_id:
                return product
        return None
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(Seller_UpdateProductView, self).get_context_data(*args, **kwargs)
        context_data['product_id'] = self.product_id
        return context_data

class ConfigurationView(PATSAPIMixin, FormView):
    form_class = ConfigurationForm
    success_url = reverse_lazy('configuration')

    def get(self, *args, **kwargs):
        if 'defaults' in self.request.GET:
            defaults = self.request.GET.get('defaults')
            self.set_config_defaults(defaults)
            messages.success(self.request, 'Configuration values updated to the %s set.' % defaults)
        return super(ConfigurationView, self).get(*args, **kwargs)

    def get_initial(self):
        return {
            'agency_api_key' : self.get_agency_api_key(),
            'agency_id' : self.get_agency_id(),
            'agency_group_id' : self.get_agency_group_id(),
            'agency_user_id' : self.get_agency_user_id(),
            'publisher_id' : self.get_publisher_id(),
            'publisher_api_key' : self.get_publisher_api_key(),
            'publisher_user' : self.get_publisher_user(),
        }

    def form_valid(self, form):
        self.set_agency_api_key(form.cleaned_data['agency_api_key'])
        self.set_agency_id(form.cleaned_data['agency_id'])
        self.set_agency_group_id(form.cleaned_data['agency_group_id'])
        self.set_agency_user_id(form.cleaned_data['agency_user_id'])
        self.set_publisher_id(form.cleaned_data['publisher_id'])
        self.set_publisher_api_key(form.cleaned_data['publisher_api_key'])
        self.set_publisher_user(form.cleaned_data['publisher_user'])
        self.set_defaults_key('Custom')
        messages.success(self.request, 'Configuration values updated.')
        return super(ConfigurationView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(ConfigurationView, self).get_context_data(*args, **kwargs)
        context_data['agency_api_key'] = self.get_agency_api_key()
        context_data['agency_id'] = self.get_agency_id()
        context_data['agency_group_id'] = self.get_agency_group_id()
        context_data['agency_user_id'] = self.get_agency_user_id()
        context_data['publisher_id'] = self.get_publisher_id()
        context_data['publisher_api_key'] = self.get_publisher_api_key()
        context_data['publisher_user'] = self.get_publisher_user()
        context_data['config_defaults_list'] = sorted(CONFIG_DEFAULTS.keys())
        context_data['defaults_key'] = self.get_defaults_key()
        return context_data
