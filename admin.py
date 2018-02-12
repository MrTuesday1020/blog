from django.contrib import admin

from blog.models import Article, User, Friend, Comment, Reply, Like, Tag

# Register your models here.

class  ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'user_id', 'modified_time', 'is_shown')
	list_filter = ('modified_time', 'is_shown')

class  UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'activatied')
	list_filter = ('activatied', )

class  FriendAdmin(admin.ModelAdmin):
	list_display = ('user_id1', 'user_id2', 'time_stamp')
	list_filter = ('user_id1', 'user_id2', 'time_stamp' )

class  CommentAdmin(admin.ModelAdmin):
	list_display = ('article_id', 'user_id', 'time_stamp')
	list_filter = ('article_id', 'user_id', 'time_stamp')

class  ReplyAdmin(admin.ModelAdmin):
	list_display = ('comment_id', 'user_id', 'time_stamp')
	list_filter = ('comment_id', 'user_id', 'time_stamp')

class  LikeAdmin(admin.ModelAdmin):
	list_display = ('article_id', 'user_id', 'time_stamp')
	list_filter = ('article_id', 'user_id', 'time_stamp')

class  TagAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_time')
	list_filter = ('name', 'created_time')
		
admin.site.register(Article, ArticleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Tag, TagAdmin)