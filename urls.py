from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^db/api/clear/$', 'dbapi.views.clear'),
    url(r'^db/api/forum/create/$', 'dbapi.views.forum_create'),
    url(r'^db/api/forum/details/$', 'dbapi.views.forum_details'),
    url(r'^db/api/forum/listPosts/$', 'dbapi.views.forum_listPosts'),
    url(r'^db/api/forum/listThreads/$', 'dbapi.views.forum_listThreads'),
    url(r'^db/api/forum/listUsers/$', 'dbapi.views.forum_listUsers'),

    url(r'^db/api/post/create/$', 'dbapi.views.post_create'),
    url(r'^db/api/post/details/$', 'dbapi.views.post_details'),
    url(r'^db/api/post/list/$', 'dbapi.views.post_list'),
    url(r'^db/api/post/remove/$', 'dbapi.views.post_remove'),
    url(r'^db/api/post/restore/$', 'dbapi.views.post_restore'),
    url(r'^db/api/post/update/$', 'dbapi.views.post_update'),
    url(r'^db/api/post/vote/$', 'dbapi.views.post_vote'),

    url(r'^db/api/user/create/$', 'dbapi.views.user_create'),
    url(r'^db/api/user/details/$', 'dbapi.views.user_details'),
    url(r'^db/api/user/follow/$', 'dbapi.views.user_follow'),
    url(r'^db/api/user/listFollowers/$', 'dbapi.views.user_listFollowers'),
    url(r'^db/api/user/listFollowing/$', 'dbapi.views.user_listFollowing'),
    url(r'^db/api/user/listPosts/$', 'dbapi.views.user_listPosts'),
    url(r'^db/api/user/unfollow/$', 'dbapi.views.user_unfollow'),
    url(r'^db/api/user/updateProfile/$', 'dbapi.views.user_updateProfile'),

    url(r'^db/api/thread/close/$', 'dbapi.views.thread_close'),
    url(r'^db/api/thread/create/$', 'dbapi.views.thread_create'),
    url(r'^db/api/thread/details/$', 'dbapi.views.thread_details'),
    url(r'^db/api/thread/list/$', 'dbapi.views.thread_list'),
    url(r'^db/api/thread/listPosts/$', 'dbapi.views.thread_listPosts'),
    url(r'^db/api/thread/open/$', 'dbapi.views.thread_open'),
    url(r'^db/api/thread/remove/$', 'dbapi.views.thread_remove'),
    url(r'^db/api/thread/restore/$', 'dbapi.views.thread_restore'),
    url(r'^db/api/thread/subscribe/$', 'dbapi.views.thread_subscribe'),
    url(r'^db/api/thread/unsubscribe/$', 'dbapi.views.thread_unsubscribe'),
    url(r'^db/api/thread/update/$', 'dbapi.views.thread_update'),
    url(r'^db/api/thread/vote/$', 'dbapi.views.thread_vote'),

)
