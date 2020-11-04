from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('', views.get_lots, name='api-v3-lots-get'),
    path('details', views.get_details, name='api-v3-lots-get-details'),
    path('snapshot', views.get_snapshot, name='api-v3-lots-get-snapshot'),
    path('summary-in', views.get_summary_in, name='api-v3-lots-get-summary-in'),
    path('summary-out', views.get_summary_out, name='api-v3-lots-get-summary-out'),

    # POST
    path('add', views.add_lot, name='api-v3-add-lot'),
    path('update', views.update_lot, name='api-v3-update-lot'),
    path('delete', views.delete_lot, name='api-v3-delete-lot'),
    path('duplicate', views.duplicate_lot, name='api-v3-duplicate-lot'),
    path('validate', views.validate_lot, name='api-v3-validate-lot'),
    path('accept', views.accept_lot, name='api-v3-accept-lot'),
    path('accept-with-reserves', views.accept_with_reserves, name='api-v3-accept-lot-with-reserves'),
    path('reject', views.reject_lot, name='api-v3-reject-lot'),
    path('comment', views.comment_lot, name='api-v3-comment-lot'),
    path('sanity-check', views.check_lot, name='api-v3-check-lot'),

    # SPECIAL
    path('delete-all-drafts', views.delete_all_drafts, name='api-v3-delete-all-drafts'),
    path('validate-all-drafts', views.validate_all_drafts, name='api-v3-validate-all-drafts'),
    path('accept-all', views.accept_all, name='api-v3-accept-all'),
    path('reject-all', views.reject_all, name='api-v3-reject-all'),

    # IMPORT/FILES
    path('upload', views.upload, name='api-v3-upload'),
    path('upload-mass-balance', views.upload_mass_balance, name='api-v3-upload-mass-balance'),
    path('download-template-simple', views.template_simple, name='api-v3-template-simple'),
    path('download-template-advanced', views.template_advanced, name='api-v3-template-advanced'),
    path('download-template-mass-balance', views.template_mass_balance, name='api-v3-template-mass-balance'),
]
