from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from .views import (
    Buyer_GetPublishersView, Buyer_GetPublisherUsersView, Buyer_GetAgenciesView,
    Buyer_CreateCampaignView, Buyer_CampaignDetailView,
    Buyer_CreateRFPView, Buyer_RFPDetailView, Buyer_RFPSearchView, Buyer_DownloadProposalAttachmentView,
    Buyer_ReturnProposalView, Buyer_ReturnOrderRevisionView,
    Buyer_CreateOrderView, Buyer_CreateOrderRawView, Buyer_OrderDetailView, Buyer_ListOrderRevisionsView, Buyer_OrderStatusView,
    Buyer_CreateOrderWithCampaignView,
    Buyer_ListProductsView,
    Seller_GetAgenciesView,
    Seller_ListRFPsView, Seller_ListProposalsView, Seller_CreateProposalRawView, Seller_DownloadRFPAttachmentView,
    Seller_ListOrdersView, Seller_OrderDetailView, Seller_OrderHistoryView, Seller_OrderFullHistoryView,
    Seller_OrderRespondView, Seller_OrderReviseView,
    ConfigurationView
)

urlpatterns = [
    url(r'^buyer/metadata/publishers/(?P<publisher_id>[\w\-]+)/users',
        Buyer_GetPublisherUsersView.as_view(template_name='buyer_metadata_publisher_users.html'),
        name='buyer_metadata_publisher_users'),
    url(r'^buyer/metadata/publishers',
        Buyer_GetPublishersView.as_view(template_name='buyer_metadata_publishers.html'),
        name='buyer_metadata_publishers'),
    url(r'^buyer/metadata/agencies/(?P<agency_id>[\w\-]+)?',
        Buyer_GetAgenciesView.as_view(template_name='buyer_metadata_agencies.html'),
        name='buyer_metadata_agencies'),
    url(r'^buyer/metadata',
        TemplateView.as_view(template_name='buyer_metadata.html'),
        name='buyer_metadata'),
    url(r'^buyer/campaigns/create',
        Buyer_CreateCampaignView.as_view(template_name='buyer_campaigns_create.html'),
        name='buyer_campaigns_create'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/status',
        Buyer_OrderStatusView.as_view(template_name='buyer_orders_status_view.html'),
        name='buyer_order_status'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\-]+)',
        Buyer_CampaignDetailView.as_view(template_name='buyer_campaigns_view.html'),
        name='buyer_campaigns_view'),
    url(r'^buyer/campaigns',
        TemplateView.as_view(template_name='buyer_campaigns.html'),
        name='buyer_campaigns'),
    url(r'^buyer/rfps/search/(?P<searchquery>[\w]+)?',
        Buyer_RFPSearchView.as_view(template_name='buyer_rfps_search.html'),
        name='buyer_rfps_search'),
    url(r'^buyer/rfps/create',
        Buyer_CreateRFPView.as_view(template_name='buyer_rfps_create.html'),
        name='buyer_rfps_create'),
    # this has lots of params but they're all in the query string
    url(r'^buyer/rfps/list',
        Buyer_RFPSearchView.as_view(template_name='buyer_rfps_list.html'),
        name='buyer_rfps_list'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/return',
        Buyer_ReturnProposalView.as_view(template_name='buyer_rfps_proposals_return.html'),
        name='buyer_rfps_proposals_return'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)',
        Buyer_DownloadProposalAttachmentView.as_view(template_name='buyer_rfps_proposals_attachment_view.html'),
        name='buyer_rfps_proposals_attachment_download'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)',
        Buyer_RFPDetailView.as_view(template_name='buyer_rfps_view.html'),
        name='buyer_rfps_view'),
    url(r'^buyer/rfps',
        TemplateView.as_view(template_name='buyer_rfps.html'),
        name='buyer_rfps'),
    url(r'^buyer/orders/create-with-campaign',
        Buyer_CreateOrderWithCampaignView.as_view(template_name='buyer_orders_create_with_campaign.html'),
        name='buyer_orders_create_with_campaign'),
    url(r'^buyer/orders/create-raw',
        Buyer_CreateOrderRawView.as_view(template_name='buyer_orders_create_raw.html'),
        name='buyer_orders_create_raw'),
    url(r'^buyer/orders/create',
        Buyer_CreateOrderView.as_view(template_name='buyer_orders_create.html'),
        name='buyer_orders_create'),
    url(r'^buyer/orders/(?P<order_id>[\w\-]+)/return',
        Buyer_ReturnOrderRevisionView.as_view(template_name='buyer_orders_revisions_return.html'),
        name='buyer_orders_revisions_return'),
    url(r'^buyer/orders/revisions',
        Buyer_ListOrderRevisionsView.as_view(template_name='buyer_orders_revisions_list.html'),
        name='buyer_orders_revisions_list'),
    url(r'^buyer/orders/(?P<order_id>[\w\-]+)',
        Buyer_OrderDetailView.as_view(template_name='buyer_orders_view.html'),
        name='buyer_orders_view'),
    url(r'^buyer/orders',
        TemplateView.as_view(template_name='buyer_orders.html'),
        name='buyer_orders'),
    url(r'^buyer/product-catalogue/(?P<publisher_id>[\w\-]+)',
        Buyer_ListProductsView.as_view(template_name='buyer_product_catalogue_list.html'),
        name='buyer_product_catalogue_list'),
    url(r'^buyer/product-catalogue',
        TemplateView.as_view(template_name='buyer_product_catalogue.html'),
        name='buyer_product_catalogue'),
    url(r'^seller/metadata/agencies/(?P<agency_id>[\w\-]+)?',
        Seller_GetAgenciesView.as_view(template_name='seller_metadata_agencies.html'),
        name='seller_metadata_agencies'),
    url(r'^seller/metadata',
        TemplateView.as_view(template_name='seller_metadata.html'),
        name='seller_metadata'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals/create-raw',
        Seller_CreateProposalRawView.as_view(template_name='seller_rfps_proposals_create_raw.html'),
        name='seller_rfps_proposals_create_raw'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals',
        Seller_ListProposalsView.as_view(template_name='seller_rfps_proposals_list.html'),
        name='seller_rfps_proposals_list'),
    url(r'^seller/agencies/(?P<agency_id>[\w\-]+)/rfps/(?P<rfp_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)',
        Seller_DownloadRFPAttachmentView.as_view(template_name='seller_rfps_attachment_download.html'),
        name='seller_rfps_attachment_download'),
    url(r'^seller/rfps/list',
        Seller_ListRFPsView.as_view(template_name='seller_rfps_list.html'),
        name='seller_rfps_list'),
    url(r'^seller/rfps',
        TemplateView.as_view(template_name='seller_rfps.html'),
        name='seller_rfps'),
    url(r'^seller/proposals',
        TemplateView.as_view(template_name='seller_proposals.html'),
        name='seller_proposals'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d\.]+)/revise',
        Seller_OrderReviseView.as_view(template_name='seller_orders_revise.html'),
        name='seller_orders_revise'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d\.]+)/respond',
        Seller_OrderRespondView.as_view(template_name='seller_orders_respond.html'),
        name='seller_orders_respond'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/full',
        Seller_OrderFullHistoryView.as_view(template_name='seller_orders_full_history.html'),
        name='seller_orders_full_history'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>\d+)?',
        Seller_OrderDetailView.as_view(template_name='seller_orders_view.html'),
        name='seller_orders_view'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions',
        Seller_OrderHistoryView.as_view(template_name='seller_orders_versions.html'),
        name='seller_orders_versions'),
    url(r'^seller/orders/list',
        Seller_ListOrdersView.as_view(template_name='seller_orders_list.html'),
        name='seller_orders_list'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)',
        Seller_OrderDetailView.as_view(template_name='seller_orders_view.html'),
        name='seller_orders_view'),
    url(r'^seller/orders',
        TemplateView.as_view(template_name='seller_orders.html'),
        name='seller_orders'),
    url(r'^seller/product-catalogue',
        TemplateView.as_view(template_name='seller_product_catalogue.html'),
        name='seller_product_catalogue'),
    url(r'^configuration',
        ConfigurationView.as_view(template_name='configuration.html'),
        name='configuration'),
    url(r'^',
        TemplateView.as_view(template_name='home.html'),
        name='home')
]
