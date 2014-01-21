from django.conf.urls import patterns, url, include
from vcb import views

touchstone = patterns('',
    url(r'^$', 
        views.touchstone, 
        name='index'),
    url(r'^dashboard/$', 
        views.dashboard, 
        name='dashboard'),
    url(r'^dashboard/(?P<tag_id>.+)/record_view/$',
        views.record_view,
        name='record_view'),
    url(r'^success/$', 
        views.success, 
        name='success'),
    url(r'class_management/$',
        views.class_management,
        name='class_management'),
    url(r'class_metadata/$', 
        views.class_metadata, 
        name='class_metadata'),
    url(r'classes_picked/$', 
        views.classes_picked, 
        name='classes_picked'),
    url(r'clickLog/$',
        views.clickLog,
        name='clickLog'),
    url(r'create_class/$', 
        views.create_class, 
        name='create_class'),
    url(r'create_transcoder_job/$', 
        views.create_transcoder_job, 
        name='create_transcoder_job'),
    url(r'drawtree/$',
        views.draw_tree,
        name='draw_tree'),
    url(r'get_children/$', 
        views.get_children, 
        name='get_children'),
    url(r'get_classes/$', 
        views.get_classes, 
        name='get_classes'),
    url(r'get_class_sessions/$', 
        views.get_class_sessions, 
        name='get_class_sessions'),
    url(r'get_s3_size/$',
        views.get_s3_size,
        name='get_s3_size'),
    url(r'login_page/$', 
        views.login_page, 
        name='login_page'),
    url(r'logout_page/$', 
        views.logout_page, 
        name='logout_page'),
    url(r'pick_classes/$', 
        views.pick_classes, 
        name='pick_classes'),
    url(r'privacy/$',     
        views.privacy, 
        name='privacy'),
    url(r'profile/$', 
        views.profile, 
        name='profile'),
    url(r'recent/$', 
        views.recent, 
        name='recent'),
    url(r'register/$', 
        views.register, 
        name='register'),
    url(r'save_class_management_data/$',
        views.save_class_management,
        name='save_class_management'),
    url(r'search_videos/$', 
        views.search_videos, 
        name='search_videos'),
    url(r'signS3put/$', 
        views.signS3put, 
        name='signS3put'),
    url(r'tos/$', 
        views.tos, 
        name='tos'),
    url(r'update_map/$', 
        views.update_map, 
        name='update_map'),
    url(r'user_classes/$',
        views.user_classes,
        name='user_classes'),
)



urlpatterns = patterns('',
    url(r'^$',
        views.index, 
        name='index'),
    url(r'^dashboard/$', 
        views.dashboard, 
        name='dashboard'),
    url(r'^dashboard/(?P<tag_id>.+)/record_view/$',
        views.record_view,
        name='record_view'),
    url(r'^success/$', 
        views.success, 
        name='success'),
    url(r'class_management/$',
        views.class_management,
        name='class_management'),
    url(r'class_metadata/$', 
        views.class_metadata, 
        name='class_metadata'),
    url(r'classes_picked/$', 
        views.classes_picked, 
        name='classes_picked'),
    url(r'clickLog/$',
        views.clickLog,
        name='clickLog'),
    url(r'create_class/$', 
        views.create_class, 
        name='create_class'),
    url(r'create_transcoder_job/$', 
        views.create_transcoder_job, 
        name='create_transcoder_job'),
    url(r'drawtree/$',
        views.draw_tree,
        name='draw_tree'),
    url(r'get_children/$', 
        views.get_children, 
        name='get_children'),
    url(r'get_classes/$', 
        views.get_classes, 
        name='get_classes'),
    url(r'get_class_sessions/$', 
        views.get_class_sessions, 
        name='get_class_sessions'),
    url(r'get_s3_size/$',
        views.get_s3_size,
        name='get_s3_size'),
    url(r'login_page/$', 
        views.login_page, 
        name='login_page'),
    url(r'logout_page/$', 
        views.logout_page, 
        name='logout_page'),
    url(r'pick_classes/$', 
        views.pick_classes, 
        name='pick_classes'),
    url(r'privacy/$',     
        views.privacy, 
        name='privacy'),
    url(r'profile/$', 
        views.profile, 
        name='profile'),
    url(r'recent/$', 
        views.recent, 
        name='recent'),
    url(r'register/$', 
        views.register, 
        name='register'),
    url(r'save_class_management_data/$',
        views.save_class_management,
        name='save_class_management'),
    url(r'search_videos/$', 
        views.search_videos, 
        name='search_videos'),
    url(r'signS3put/$', 
        views.signS3put, 
        name='signS3put'),
    url(r'tos/$', 
        views.tos, 
        name='tos'),
    url(r'update_map/$', 
        views.update_map, 
        name='update_map'),
    url(r'user_classes/$',
        views.user_classes,
        name='user_classes'),
    url(r'^touchstone/', 
        include(touchstone, namespace="touchstone")),
)
