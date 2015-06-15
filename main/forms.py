from django import forms 

class Buyer_CreateCampaignForm(forms.Form):
    # aka "organisation ID"
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    company_id = forms.CharField(label='Buyer Client ID', max_length=100)
    person_id = forms.CharField(label='Buyer Person ID', max_length=100)
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

class Buyer_CreateOrderForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    company_id = forms.CharField(label='Buyer Client ID', max_length=100)
    person_id = forms.CharField(label='Buyer Person ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=5000, widget=forms.Textarea)

class Buyer_CreateOrderRawForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    company_id = forms.CharField(label='Buyer Client ID', max_length=100)
    person_id = forms.CharField(label='Buyer Person ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=5000, widget=forms.Textarea)

class ConfigurationForm(forms.Form):
    agency_id = forms.CharField(label='Agency ID', max_length=100)
    agency_api_key = forms.CharField(label='Agency API Key', max_length=100)
    agency_user_id = forms.CharField(label='Agency User ID', max_length=100)
    agency_company_id = forms.CharField(label='Agency Company ID', max_length=100)
    agency_person_id = forms.CharField(label='Agency Person ID', max_length=100)
    publisher_id = forms.CharField(label='Publisher ID', max_length=100)
    publisher_api_key = forms.CharField(label='Publisher API Key', max_length=100)
