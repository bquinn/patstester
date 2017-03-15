from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from .views import (
    Buyer_GetPublishersView, Buyer_GetPublisherUsersView,
    Buyer_GetPublisherMediaPropertiesView, Buyer_ListPublisherProductsView,
    Buyer_GetAgenciesView, 
    Buyer_CreateCampaignView, Buyer_CampaignDetailView, Buyer_UpdateCampaignDetailView,
    Buyer_CreateRFPView, Buyer_CreateRFPWithCampaignView, Buyer_RFPDetailView, Buyer_RFPSearchView, Buyer_DownloadProposalAttachmentView,
    Buyer_ListEventsView, Buyer_ReprocessEventsView,
    Buyer_RFPsForCampaignView, Buyer_ListProposalsView, Buyer_ProposalDetailView,
    Buyer_ReturnProposalView, Buyer_ReturnOrderRevisionView, Buyer_RequestOrderRevisionView,
    Buyer_LinkProposalView,
    Buyer_CreateOrderView, Buyer_CreateOrderRawView, Buyer_OrderVersionDetailView,
    Buyer_ViewOrderAttachmentView, Buyer_DownloadOrderAttachmentView,
    Buyer_ViewProposalAttachmentView, Buyer_DownloadProposalAttachmentView,
    Buyer_ViewRFPAttachmentView, Buyer_DownloadRFPAttachmentView,
    Buyer_ListOrdersView, Buyer_ListOrderRevisionsView, Buyer_OrderStatusView, Buyer_OrderVersionsView,
    Buyer_CreateOrderWithCampaignView, Buyer_CreateOrderFromRevisionView,
    Buyer_OrderRevisionDetailView,
    Buyer_CallbackView, Buyer_DataCallbackView,
    Seller_ListRFPsView, Seller_RFPDetailView,
    Seller_ListProposalsView, Seller_ProposalDetailView, 
    Seller_CreateProposalRawView, Seller_DownloadRFPAttachmentView,
    Seller_ListOrdersView, Seller_ListOrderVersionsView, Seller_OrderVersionDetailView, Seller_OrderRevisionDetailView,
    Seller_ListOrderRevisionsView, Seller_ListOrderEventsView,
    Seller_OrderRespondView, Seller_OrderReviseView,
    Seller_ViewOrderAttachmentView, Seller_DownloadOrderAttachmentView,
    Seller_ViewProposalAttachmentView, Seller_DownloadProposalAttachmentView,
    Seller_OrderVersionsView,
    Seller_GetAgenciesView, Seller_GetMediaPropertiesView, Seller_UpdateMediaPropertiesView,
    Seller_ListProductsView, Seller_UpdateProductView, Seller_CreateProductView,
    ConfigurationView
)

urlpatterns = [
    url(r'^api/callback',
        Buyer_CallbackView.as_view(),
        name='api_callback'),
    url(r'^api/datacallback',
        Buyer_DataCallbackView.as_view(),
        name='api_data_callback'),
    url(r'^buyer/metadata/publishers/(?P<publisher_id>[\w\-]+)/users',
        Buyer_GetPublisherUsersView.as_view(template_name='buyer_metadata_publisher_users.html'),
        name='buyer_metadata_publisher_users'),
    url(r'^buyer/metadata/publishers/(?P<publisher_id>[\w\-]+)/mediaproperties',
        Buyer_GetPublisherMediaPropertiesView.as_view(template_name='buyer_metadata_publisher_mediaproperties.html'),
        name='buyer_metadata_publisher_mediaproperties'),
    url(r'^buyer/metadata/publishers/(?P<publisher_id>[\w\-]+)/products',
        Buyer_ListPublisherProductsView.as_view(template_name='buyer_metadata_publisher_products.html'),
        name='buyer_metadata_publisher_products'),
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
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)/download',
        Buyer_DownloadOrderAttachmentView.as_view(template_name='buyer_orders_attachment_download.html'),
        name='buyer_order_attachment_download'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)',
        Buyer_ViewOrderAttachmentView.as_view(template_name='buyer_orders_attachment_download.html'),
        name='buyer_order_attachment_view'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)/requestrevision',
        Buyer_RequestOrderRevisionView.as_view(template_name='buyer_orders_requestrevision.html'),
        name='buyer_orders_requestrevision'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)/revisions/(?P<revision>[\d]+)/return',
        Buyer_ReturnOrderRevisionView.as_view(template_name='buyer_orders_revisions_return.html'),
        name='buyer_orders_revisions_return'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)/revisions/(?P<revision>[\d]+)/createorder',
        Buyer_CreateOrderFromRevisionView.as_view(template_name='buyer_orders_create_from_revision.html'),
        name='buyer_orders_create_from_revision'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)/revisions/(?P<revision>[\d]+)',
        Buyer_OrderRevisionDetailView.as_view(template_name='buyer_orders_revisions_view.html'),
        name='buyer_orders_revisions_view'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)/revisions',
        Buyer_ListOrderRevisionsView.as_view(template_name='buyer_orders_revisions_list.html'),
        name='buyer_orders_revisions_list'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)',
        Buyer_OrderVersionDetailView.as_view(template_name='buyer_orders_version_view.html'),
        name='buyer_order_version_view'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)',
        Buyer_OrderVersionsView.as_view(template_name='buyer_orders_versions_list.html'),
        name='buyer_order_versions_list'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\ \-\.]+)/rfps',
        Buyer_RFPsForCampaignView.as_view(template_name='buyer_campaigns_rfps_list.html'),
        name='buyer_campaigns_rfps_list'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\-]+)/update',
        Buyer_UpdateCampaignDetailView.as_view(template_name='buyer_campaigns_update.html'),
        name='buyer_campaigns_update'),
    url(r'^buyer/campaigns/(?P<campaign_id>[\w\-]+)',
        Buyer_CampaignDetailView.as_view(template_name='buyer_campaigns_view.html'),
        name='buyer_campaigns_view'),
    url(r'^buyer/campaigns',
        TemplateView.as_view(template_name='buyer_campaigns.html'),
        name='buyer_campaigns'),
    url(r'^buyer/events/list',
        Buyer_ListEventsView.as_view(template_name='buyer_events_list.html'),
        name='buyer_events_list'),
    url(r'^buyer/events/reprocess',
        Buyer_ReprocessEventsView.as_view(template_name='buyer_events_reprocess.html'),
        name='buyer_events_reprocess'),
    url(r'^buyer/events',
        TemplateView.as_view(template_name='buyer_events.html'),
        name='buyer_events'),
    url(r'^buyer/rfps/search/(?P<searchquery>[\w]+)?',
        Buyer_RFPSearchView.as_view(template_name='buyer_rfps_search.html'),
        name='buyer_rfps_search'),
    url(r'^buyer/rfps/create-with-campaign',
        Buyer_CreateRFPWithCampaignView.as_view(template_name='buyer_rfps_create_with_campaign.html'),
        name='buyer_rfps_create_with_campaign'),
    url(r'^buyer/rfps/create',
        Buyer_CreateRFPView.as_view(template_name='buyer_rfps_create.html'),
        name='buyer_rfps_create'),
    # this has lots of params but they're all in the query string
    url(r'^buyer/rfps/list',
        Buyer_RFPSearchView.as_view(template_name='buyer_rfps_list.html'),
        name='buyer_rfps_list'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)/download',
        Buyer_DownloadRFPAttachmentView.as_view(template_name='buyer_rfps_attachment_download.html'),
        name='buyer_rfps_attachment_download'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)',
        Buyer_ViewRFPAttachmentView.as_view(template_name='buyer_rfps_attachment_view.html'),
        name='buyer_rfps_attachment_view'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/return',
        Buyer_ReturnProposalView.as_view(template_name='buyer_rfps_proposals_return.html'),
        name='buyer_rfps_proposals_return'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)/download',
        Buyer_DownloadProposalAttachmentView.as_view(template_name='buyer_rfps_proposals_attachment_download.html'),
        name='buyer_rfps_proposals_attachment_download'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)',
        Buyer_ViewProposalAttachmentView.as_view(template_name='buyer_rfps_proposals_attachment_view.html'),
        name='buyer_rfps_proposals_attachment_view'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w]+)/proposals/(?P<proposal_id>[\w]+)',
        Buyer_ProposalDetailView.as_view(template_name='buyer_rfps_proposals_view.html'),
        name='buyer_rfps_proposals_view'),
    url(r'^buyer/proposals/(?P<proposal_id>[\w]+)/link',
        Buyer_LinkProposalView.as_view(template_name='buyer_rfps_proposals_link.html'),
        name='buyer_rfps_proposals_link'),
    url(r'^buyer/proposals/(?P<proposal_id>[\w]+)',
        Buyer_ProposalDetailView.as_view(template_name='buyer_rfps_proposals_view.html'),
        name='buyer_rfps_proposals_view'),
    url(r'^buyer/rfps/(?P<rfp_id>[\w]+)/proposals',
        Buyer_ListProposalsView.as_view(template_name='buyer_rfps_proposals_list.html'),
        name='buyer_rfps_proposals_list'),
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
    url(r'^buyer/orders/list',
        Buyer_ListOrdersView.as_view(template_name='buyer_orders_list.html'),
        name='buyer_orders_list'),
    url(r'^buyer/orders',
        TemplateView.as_view(template_name='buyer_orders.html'),
        name='buyer_orders'),
    url(r'^seller/metadata/agencies/(?P<agency_id>[\w\-\.]+)?',
        Seller_GetAgenciesView.as_view(template_name='seller_metadata_agencies.html'),
        name='seller_metadata_agencies'),
    url(r'^seller/metadata/mediaproperties/(?P<media_property_id>[\w\-]+)/update/(?P<field_id>[\w\-]+)?',
        Seller_UpdateMediaPropertiesView.as_view(template_name='seller_metadata_mediaproperties_update.html'),
        name='seller_metadata_mediaproperties_update'),
    url(r'^seller/metadata/mediaproperties/update/(?P<field_id>[\w\-]+)?',
        Seller_UpdateMediaPropertiesView.as_view(template_name='seller_metadata_mediaproperties_update.html'),
        name='seller_metadata_mediaproperties_update_generic'),
    url(r'^seller/metadata/mediaproperties',
        Seller_GetMediaPropertiesView.as_view(template_name='seller_metadata_mediaproperties.html'),
        name='seller_metadata_mediaproperties'),
    url(r'^seller/metadata/products/create',
        Seller_CreateProductView.as_view(template_name='seller_metadata_products_create.html'),
        name='seller_metadata_products_create'),
    url(r'^seller/metadata/products/(?P<product_id>[\w\-\.]+)/update',
        Seller_UpdateProductView.as_view(template_name='seller_metadata_products_update.html'),
        name='seller_metadata_products_update'),
    url(r'^seller/metadata/products',
        Seller_ListProductsView.as_view(template_name='seller_metadata_products.html'),
        name='seller_metadata_products'),
    url(r'^seller/metadata',
        TemplateView.as_view(template_name='seller_metadata.html'),
        name='seller_metadata'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)/download',
        Seller_DownloadProposalAttachmentView.as_view(template_name='seller_rfps_proposals_attachment_download.html'),
        name='seller_rfps_proposals_attachment_download'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals/(?P<proposal_id>[\w\-]+)/attachments/(?P<attachment_id>[\w\-]+)',
        Seller_ViewProposalAttachmentView.as_view(template_name='seller_rfps_proposals_attachment_view.html'),
        name='seller_rfps_proposals_attachment_view'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals/create-raw',
        Seller_CreateProposalRawView.as_view(template_name='seller_rfps_proposals_create_raw.html'),
        name='seller_rfps_proposals_create_raw'),
    url(r'^seller/rfps/(?P<rfp_id>[\w]+)/proposals/(?P<proposal_id>[\w]+)',
        Seller_ProposalDetailView.as_view(template_name='seller_rfps_proposals_view.html'),
        name='seller_rfps_proposals_view'),
    url(r'^seller/rfps/(?P<rfp_id>[\w]+)/proposals',
        Seller_ListProposalsView.as_view(template_name='seller_rfps_proposals_list.html'),
        name='seller_rfps_proposals_list'),
    url(r'^seller/rfps/list',
        Seller_ListRFPsView.as_view(template_name='seller_rfps_list.html'),
        name='seller_rfps_list'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)',
        Seller_RFPDetailView.as_view(template_name='seller_rfps_view.html'),
        name='seller_rfps_view'),
    url(r'^seller/rfps',
        TemplateView.as_view(template_name='seller_rfps.html'),
        name='seller_rfps'),
    url(r'^seller/proposals',
        TemplateView.as_view(template_name='seller_proposals.html'),
        name='seller_proposals'),
    url(r'^seller/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)/versions/(?P<version>[\d]+)',
        Seller_OrderVersionDetailView.as_view(template_name='seller_orders_version_view.html'),
        name='seller_orders_version_view'),
    url(r'^seller/campaigns/(?P<campaign_id>[\w\ \-\.]+)/orders/(?P<order_id>[\w\ \-\.]+)',
        Seller_OrderVersionsView.as_view(template_name='seller_orders_versions_list.html'),
        name='seller_orders_versions_list'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d\.]+)/revise',
        Seller_OrderReviseView.as_view(template_name='seller_orders_revise.html'),
        name='seller_orders_revise'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d\.]+)/respond',
        Seller_OrderRespondView.as_view(template_name='seller_orders_respond.html'),
        name='seller_orders_respond'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/events',
        Seller_ListOrderEventsView.as_view(template_name='seller_orders_events_list.html'),
        name='seller_orders_events_list'),
    url(r'^seller/campaigns/(?P<campaign_id>[\w\-]+)/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>\d+)?',
        Seller_OrderVersionDetailView.as_view(template_name='seller_orders_view.html'),
        name='seller_order_version_view'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d]+)/revisions/(?P<revision>[\d]+)',
        Seller_OrderRevisionDetailView.as_view(template_name='seller_orders_revisions_view.html'),
        name='seller_orders_revisions_view'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions/(?P<version>[\d]+)/revisions',
        Seller_ListOrderRevisionsView.as_view(template_name='seller_orders_revisions_list.html'),
        name='seller_orders_revisions_list'),
    url(r'^seller/orders/(?P<order_id>[\w\-]+)/versions',
        Seller_ListOrderVersionsView.as_view(template_name='seller_orders_versions.html'),
        name='seller_orders_versions'),
    url(r'^seller/orders/list',
        Seller_ListOrdersView.as_view(template_name='seller_orders_list.html'),
        name='seller_orders_list'),
    url(r'^seller/orders/(?P<order_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)/download',
        Seller_DownloadOrderAttachmentView.as_view(template_name='seller_orders_attachments_download.html'),
        name='seller_order_attachment_download'),
    url(r'^seller/orders/(?P<order_id>[\w\ \-\.]+)/attachments/(?P<attachment_id>[\w\ \-\.]+)',
        Seller_ViewOrderAttachmentView.as_view(template_name='seller_orders_attachments_view.html'),
        name='seller_order_attachment_view'),
    url(r'^seller/orders',
        TemplateView.as_view(template_name='seller_orders.html'),
        name='seller_orders'),
    url(r'^seller/product-catalogue',
        TemplateView.as_view(template_name='seller_product_catalogue.html'),
        name='seller_product_catalogue'),
    url(r'^configuration',
        ConfigurationView.as_view(template_name='configuration.html'),
        name='configuration'),
    url(r'^lineitemtester',
        TemplateView.as_view(template_name='lineitemtester.html'),
        name='line_item_tester'),
    url(r'^$',
        TemplateView.as_view(template_name='home.html'),
        name='home')
]
