from django import forms 
from django.forms import widgets

# hacky widget used by file upload forms below
class BootstrapFileInput(widgets.ClearableFileInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrapFileInput, self).render(name, value, attrs)
        return '<span class="input-group"><span class="btn btn-default btn-file">Browse '+html+'</span>'+'<input name="text" type="text" class="form-control" readonly></span>'

class Buyer_CampaignForm(forms.Form):
    # aka "organisation ID"
    agency_group_id = forms.CharField(label='Buyer Agency Group ID', max_length=100)
    organisation_id = forms.CharField(label='Buyer Organisation ID', max_length=100)
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    advertiser_code = forms.CharField(label='Advertiser Code', max_length=5)
    external_campaign_id = forms.CharField(label='External campaign ID', max_length=100)
    campaign_name = forms.CharField(label='Campaign Name', max_length=200)
    start_date = forms.DateField(label='Campaign Start Date', widget=forms.DateInput(attrs={'type':'date'}))
    end_date = forms.DateField(label='Campaign End Date', widget=forms.DateInput(attrs={'type':'date'}))
    print_flag = forms.BooleanField(label='Print component', required=False)
    print_budget = forms.CharField(label='Print budget', max_length=10, required=False)
    digital_flag = forms.BooleanField(label='Digital component', required=False)
    digital_budget = forms.CharField(label='Digital budget', max_length=10, required=False)
    campaign_budget = forms.CharField(label='Overall campaign budget', max_length=10, required=False)

class Buyer_CreateRFPForm(forms.Form):
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    campaign_id = forms.CharField(label='Campaign ID', max_length=100)
    budget_amount = forms.CharField(label='Budget amount', max_length=100)
    start_date = forms.DateField(label='RFP start date', widget=forms.DateInput(attrs={'type':'date'}))
    end_date = forms.DateField(label='RFP end date', widget=forms.DateInput(attrs={'type':'date'}))
    respond_by_date = forms.DateField(label='Respond by date', widget=forms.DateInput(attrs={'type':'date'}))
    comments = forms.CharField(label='Comments', max_length=5000, widget=forms.Textarea)
    publisher_id = forms.CharField(label='Publisher ID', max_length=100)
    publisher_emails = forms.CharField(label='Publisher email(s)', max_length=100)
    media_print = forms.BooleanField(label='Print component', required=False)
    media_online = forms.BooleanField(label='Online (digital) component', required=False)
    strategy = forms.CharField(label='Strategy', max_length=100)
    requested_products = forms.CharField(label='Requested products', max_length=100, required=False)
    attachment = forms.FileField(max_length=100, widget=BootstrapFileInput, required=False)

class Buyer_CreateRFPWithCampaignForm(forms.Form):
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    campaign_id = forms.CharField(label='Campaign ID', max_length=50)
    campaign_name = forms.CharField(label='Campaign Name', max_length=200)
    campaign_start_date = forms.DateField(label='Campaign start date', widget=forms.DateInput(attrs={'type':'date'}))
    campaign_end_date = forms.DateField(label='Campaign end date', widget=forms.DateInput(attrs={'type':'date'}))
    advertiser_code = forms.CharField(label='Advertiser Code', max_length=5)
    print_flag = forms.BooleanField(label='Print component', required=False)
    print_budget = forms.CharField(label='Campaign print budget', max_length=10, required=False)
    digital_flag = forms.BooleanField(label='Digital component', required=False)
    digital_budget = forms.CharField(label='Campaign digital budget', max_length=10, required=False)
    campaign_budget = forms.CharField(label='Campaign overall budget', max_length=10, required=False)
    rfp_budget_amount = forms.CharField(label='RFP budget amount', max_length=100)
    rfp_start_date = forms.DateField(label='RFP start date', widget=forms.DateInput(attrs={'type':'date'}))
    rfp_end_date = forms.DateField(label='RFP end date', widget=forms.DateInput(attrs={'type':'date'}))
    rfp_respond_by_date = forms.DateField(label='RFP respond by date', widget=forms.DateInput(attrs={'type':'date'}))
    rfp_comments = forms.CharField(label='RFP Comments', max_length=5000, widget=forms.Textarea)
    publisher_id = forms.CharField(label='RFP recipient publisher ID', max_length=100)
    publisher_email = forms.CharField(label='RFP recipient publisher email', max_length=100)
    strategy = forms.CharField(label='RFP strategy', max_length=100)
    requested_products = forms.CharField(label='RFP requested products', max_length=100, required=False)
    attachment = forms.FileField(label='RFP attachment', max_length=100, widget=BootstrapFileInput, required=False)

class Buyer_ReturnProposalForm(forms.Form):
    proposal_id = forms.CharField(label='Proposal Public ID', max_length=50)
    user_id = forms.CharField(label='Sender User ID', max_length=50)
    email = forms.CharField(label='Seller email', max_length=100)
    due_date = forms.DateField(label='Response due date', widget=forms.DateInput(attrs={'type':'date'}))
    comments = forms.CharField(label='Comments', max_length=5000, widget=forms.Textarea)
    # TODO - attachments

class Buyer_LinkProposalForm(forms.Form):
    proposal_id = forms.CharField(label='Proposal Public ID', max_length=50)
    campaign_id = forms.CharField(label='Campaign Public ID', max_length=50)
    
class Buyer_RequestOrderRevisionForm(forms.Form):
    order_id = forms.CharField(label='Order Public ID', max_length=50)
    user_id = forms.CharField(label='Sender User ID', max_length=50)
    seller_email = forms.CharField(label='Seller Email', max_length=50)
    due_date = forms.DateField(label='Response due date', widget=forms.DateInput(attrs={'type':'date'}))
    comments = forms.CharField(label='Comments', max_length=5000, widget=forms.Textarea)
    # TODO - attachments

class Buyer_ReturnOrderRevisionForm(forms.Form):
    #order_id = forms.CharField(label='Order Public ID', max_length=50)
    #order_major_version = forms.CharField(label='Order major version', max_length=5)
    #order_minor_version = forms.CharField(label='Order minor version', max_length=5)
    #user_id = forms.CharField(label='Buyer User ID', max_length=50)
    seller_email = forms.CharField(label='Seller Email', max_length=50)
    due_date = forms.DateField(label='Response due date', widget=forms.DateInput(attrs={'type':'date'}))
    comments = forms.CharField(label='Comments', max_length=5000, widget=forms.Textarea)

class Buyer_CreateOrderForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    agency_group_id = forms.CharField(label='Buyer Agency Group ID', max_length=100)
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=999999, widget=forms.Textarea)

class Buyer_CreateOrderRawForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    agency_group_id = forms.CharField(label='Buyer Agency Group ID', max_length=100)
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=999999, widget=forms.Textarea)

class Buyer_CreateOrderWithCampaignForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    agency_group_id = forms.CharField(label='Buyer Agency Group ID', max_length=100)
    user_id = forms.CharField(label='Buyer User ID', max_length=100)
    advertiser_code = forms.CharField(label='Advertiser Code', max_length=5)
    campaign_id = forms.CharField(label='Campaign ID', max_length=50)
    campaign_name = forms.CharField(label='Campaign Name', max_length=200)
    campaign_start_date = forms.DateField(label='Campaign start date', widget=forms.DateInput(attrs={'type':'date'}))
    campaign_end_date = forms.DateField(label='Campaign end date', widget=forms.DateInput(attrs={'type':'date'}))
    respond_by_date = forms.DateField(label='Respond-by date', widget=forms.DateInput(attrs={'type':'date'}))
    print_flag = forms.BooleanField(label='Print component', required=False)
    print_budget = forms.CharField(label='Print budget', max_length=10, required=False)
    digital_flag = forms.BooleanField(label='Digital component', required=False)
    digital_budget = forms.CharField(label='Digital budget', max_length=10, required=False)
    campaign_budget = forms.CharField(label='Overall campaign budget', max_length=10, required=False)
    publisher_id = forms.CharField(label='Publisher ID', max_length=100)
    publisher_email = forms.CharField(label='Publisher (Recipient) Email', max_length=100)
    payload_1 = forms.CharField(label='Payload 1', max_length=999999, widget=forms.Textarea)
    payload_2 = forms.CharField(label='Payload 2', max_length=999999, widget=forms.Textarea, required=False)

class Seller_CreateProposalRawForm(forms.Form):
    rfp_id = forms.CharField(label='RFP ID', max_length=100)
    vendor_id = forms.CharField(label='Vendor (publisher) ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=999999, widget=forms.Textarea)

class Seller_OrderRespondForm(forms.Form):
    user_id = forms.CharField(label='Seller User ID', max_length=100)
    order_id = forms.CharField(label='Seller Order ID', max_length=100)
    status = forms.CharField(label='Acceptance Status', max_length=100)
    comments = forms.CharField(label='Comments', max_length=1000, widget=forms.Textarea)

class Seller_OrderReviseForm(forms.Form):
    user_id = forms.CharField(label='Seller User ID', max_length=100)
    order_id = forms.CharField(label='Seller Order ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=999999, widget=forms.Textarea)

class Seller_MediaPropertyForm(forms.Form):
    """
    Request looks like /vendors/35-EEBMG4J-4/mediaproperties/RXQKYC2-7/sections
    """
    FIELD_CHOICES = (
        ('sections', 'Sections'),
        ('inclsdigitaleditions', 'Include in Digital Edition'),
        ('servedbys', 'Served By'),
        ('positions', 'Position'),
        ('colors', 'Colours'),
        ('sizes', 'Sizes'),
        ('dimensions', 'Dimensions'),
        ('costmethods', 'Cost Methods'),
        ('guaranteed', 'Position Guaranteed'),
        ('buytypes', 'Buy Types'),
        ('regions', 'Regions')
    )
    user_id = forms.CharField(label='Seller User ID', max_length=100)
    vendor_id = forms.CharField(label='Vendor (publisher) ID', max_length=100)
    media_property_id = forms.CharField(label='Media Property ID', max_length=100)
    field_id = forms.ChoiceField(label='Field', choices=FIELD_CHOICES)
    payload = forms.CharField(label='Payload', max_length=999999, widget=forms.Textarea)

class Seller_ProductForm(forms.Form):
    external_product_id = forms.CharField(label='External Product ID', max_length=100, required=True)
    status = forms.CharField(label='Status', max_length=100, required=True)
    name = forms.CharField(label='Name', max_length=100, required=True)
    media_property_id = forms.CharField(label='Media Property Id', max_length=100, required=False)
    media_type = forms.CharField(label='Media Type', max_length=100, required=True)
    currency_code = forms.CharField(label='Currency Code', max_length=100)
    agency_enabled = forms.BooleanField(label='Agency Enabled', required=False)
    client_id = forms.CharField(label='Client ID', max_length=100, required=False)
    buy_type = forms.CharField(label='Buy Type', max_length=100, required=False)
    buy_category = forms.CharField(label='Buy Category', max_length=100, required=False)
    size = forms.CharField(label='Size (print)', max_length=100, required=False)
    position = forms.CharField(label='Position', max_length=100, required=False)
    dimensions = forms.CharField(label='Dimensions (digital)', max_length=100, required=False)
    cost_method = forms.CharField(label='Cost Method', max_length=100, required=False)
    unit_type = forms.CharField(label='Unit Type', max_length=100, required=False)
    rate = forms.CharField(label='Rate', max_length=100, required=False)
    units = forms.CharField(label='Units', max_length=100, required=False)
    cost = forms.CharField(label='Cost', max_length=100, required=False)
    section = forms.CharField(label='Section', max_length=100, required=False)
    subsection = forms.CharField(label='Subsection', max_length=100, required=False)
    position_guaranteed = forms.CharField(label='Position Guaranteed (Yes or No)', required=False)
    comments = forms.CharField(label='Comments', max_length=100, required=False)

class ConfigurationForm(forms.Form):
    agency_api_key = forms.CharField(label='Agency API Key', max_length=100)
    agency_id = forms.CharField(label='Agency ID', max_length=100)
    agency_group_id = forms.CharField(label='Agency Group ID', max_length=100)
    agency_user_id = forms.CharField(label='Agency User ID', max_length=100)
    publisher_id = forms.CharField(label='Publisher ID', max_length=100)
    publisher_user = forms.CharField(label='Publisher User Email', max_length=100)
    publisher_api_key = forms.CharField(label='Publisher API Key', max_length=100)
