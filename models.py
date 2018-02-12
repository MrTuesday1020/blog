from django.db import models

# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=64, null=False)
	password = models.CharField(max_length=256, null=False)
	email = models.EmailField(null=False)
	profile = models.TextField(null=True, blank=False)
	activatied = models.BooleanField(default=False)
	time_stamp = models.DateTimeField(auto_now_add = True)
	image = models.ImageField(upload_to='images',default='images/default.png',blank=True)
	tag = models.CharField(max_length =64, null=True, blank=True)

	class Meta:
		db_table = "user"

	def __str__(self):
		return self.username


class Article(models.Model):
	is_shown_choices = (('Y', 'Yes'),('N', 'No'),)
	title = models.CharField(max_length=64, null=False)
	user_id = models.IntegerField(null=False)
	created_time = models.DateTimeField(auto_now_add = True)
	modified_time = models.DateTimeField(auto_now = True)
	content = models.TextField(null=False)
	is_shown = models.CharField(max_length=1, choices=is_shown_choices, default='Y')
	tag = models.CharField(max_length =64, null=True, blank=True)

	class Meta:
		db_table = "article"
		ordering = ['-modified_time']

	def __str__(self):
		return self.title

class Friend(models.Model):
	user_id1 = models.IntegerField(null=False)
	user_id2 = models.IntegerField(null=False)
	time_stamp = models.DateTimeField(auto_now_add=True)
						
	class Meta:
		db_table = "friend"

	def __str__(self):
		return "User " + str(self.user_id1) + " follows User " + str(self.user_id2)

class Comment(models.Model):
	article_id = models.IntegerField(null=False)
	user_id = models.IntegerField(null=False)
	content = models.TextField(null=False)
	time_stamp = models.DateTimeField(auto_now_add=True)
						
	class Meta:
		db_table = "comment"
		ordering = ['-time_stamp']

	def __str__(self):
		return "User " + str(self.user_id) + " comments on the article " + str(self.article_id)

class Reply(models.Model):
	comment_id = models.IntegerField(null=False)
	user_id = models.IntegerField(null=False)
	content = models.TextField(null=False)
	time_stamp = models.DateTimeField(auto_now_add=True)
						
	class Meta:
		db_table = "reply"
		ordering = ['-time_stamp']

	def __str__(self):
		return "User " + str(self.user_id) + " replies the comment " + str(self.comment_id)

class Like(models.Model):
	article_id = models.IntegerField(null=False)
	user_id = models.IntegerField(null=False)
	time_stamp = models.DateTimeField(auto_now_add=True)
						
	class Meta:
		db_table = "like"

	def __str__(self):
		return "User " + str(self.user_id) + " likes the article " + str(self.article_id)

class Tag(models.Model):
	name =  models.CharField(max_length=32, null=False)
	created_time = models.DateTimeField(auto_now_add=True)
						
	class Meta:
		db_table = "tag"

	def __str__(self):
		return self.name