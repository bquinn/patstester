from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from .views import (
    Buyer_GetPublishersView, Buyer_GetPublisherUsersView, Buyer_SendOrderView, Buyer_ListOrderRevisionsView,
    Seller_ListRFPsView, Seller_ListProposalsView
)

urlpatterns = [
    url(r'^buyer/metadata/publishers/(?P<publisher_id>[\w\-]+)/users',
        Buyer_GetPublisherUsersView.as_view(template_name='buyer_metadata_get_publisher_users.html'),
        name='buyer_metadata_get_publisher_users'),
    url(r'^buyer/metadata/publishers',
        Buyer_GetPublishersView.as_view(template_name='buyer_metadata_get_publishers.html'),
        name='buyer_metadata_get_publishers'),
    url(r'^buyer/metadata',
        TemplateView.as_view(template_name='buyer_metadata.html'),
        name='buyer_metadata'),
    url(r'^buyer/campaigns',
        TemplateView.as_view(template_name='buyer_campaigns.html'),
        name='buyer_campaigns'),
    url(r'^buyer/rfps',
        TemplateView.as_view(template_name='buyer_rfps.html'),
        name='buyer_rfps'),
    url(r'^buyer/orders/create',
        Buyer_SendOrderView.as_view(template_name='buyer_orders_create.html'),
        name='buyer_orders_create'),
    url(r'^buyer/orders/revisions',
        Buyer_ListOrderRevisionsView.as_view(template_name='buyer_order_revisions_list.html'),
        name='buyer_order_revisions_list'),
    url(r'^buyer/orders',
        TemplateView.as_view(template_name='buyer_orders.html'),
        name='buyer_orders'),
    url(r'^buyer/product-catalogue',
        TemplateView.as_view(template_name='buyer_product_catalogue.html'),
        name='buyer_product_catalogue'),
    url(r'^seller/rfps/(?P<rfp_id>[\w\-]+)/proposals',
        Seller_ListProposalsView.as_view(template_name='seller_rfps_proposals_list.html'),
        name='seller_rfps_proposals_list'),
    url(r'^seller/rfps/list',
        Seller_ListRFPsView.as_view(template_name='seller_rfps_list.html'),
        name='seller_rfps_list'),
    url(r'^seller/rfps',
        TemplateView.as_view(template_name='seller_rfps.html'),
        name='seller_rfps'),
    url(r'^seller/proposals',
        TemplateView.as_view(template_name='seller_proposals.html'),
        name='seller_proposals'),
    url(r'^seller/orders',
        TemplateView.as_view(template_name='seller_orders.html'),
        name='seller_orders'),
    url(r'^seller/product-catalogue',
        TemplateView.as_view(template_name='seller_product_catalogue.html'),
        name='seller_product_catalogue'),
    url(r'^',
        TemplateView.as_view(template_name='home.html'),
        name='home')
]
