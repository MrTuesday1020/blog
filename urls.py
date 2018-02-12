from django.urls import path, re_path
from django.views.generic.base import TemplateView

from . import views


app_name = 'blog'

urlpatterns = [
	path('', views.home, name='home'),
	path('home/<int:page>', views.home, name='home'),
	path('login/', views.login, name='login'),
	path('logout/', views.logout, name='logout'),
	path('signup/', views.signup, name='signup'),
	path('confirm/<path:encrypted>', views.confirm, name='confirm'),
	path('post/', views.post, name='post'),
	path('article/<int:article_id>', views.article, name='article'),
	path('profile/<int:user_id>', views.profile, name='profile'),
	path('edit/', views.edit, name='edit'),
	path('changepassword/', views.changepassword, name='changepassword'),
	path('notification/', views.notification, name='notification'),
	path('search/', views.search, name='search'),
	path('topost/', TemplateView.as_view(template_name='post.html'), name='topost'),
	path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
	path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
	path('like/', views.like, name='like'),
	path('follow/', views.follow, name='follow'),
	path('comment/', views.comment, name='comment'),
	path('reply/', views.reply, name='reply'),
]