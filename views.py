from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from django.db import connection
from django.core.files.storage import FileSystemStorage
from time import gmtime, strftime, time
from django.core.mail import send_mail
import bleach
import re
import base64

from blog.forms import loginForm, signupForm, editForm, passwordForm
from blog.models import Article, User, Friend, Comment, Reply, Like, Tag

######################### views #########################
def home(request, page = 1):
	# the number of items in one page
	limit = 10
	account_id = request.session['account']['id'] if 'account' in request.session else 0
	sql = """select a.*, count(distinct c.id) as comment_nb, count(distinct l1.id)  as like_nb, count(distinct l2.id) as liked
			from article as a
			left join comment as c on a.id = c.article_id
			left join `like` as l1 on a.id = l1.article_id
			left join `like` as l2 on a.id = l2.article_id and l2.user_id = """ + str(account_id) + """
			group by a.id order by a.modified_time desc"""
	articles = RunSQL(sql)
	for article in articles:
		author = User.objects.get(pk = article["user_id"])
		article['author'] = author
	paginator = Paginator(articles, limit)

	try:
		articles = paginator.page(page)
	# if page is not an int number
	except PageNotAnInteger:
		articles = paginator.page(1)
	# if page is too large
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)
	return render(request, 'home.html', {'articles': articles})


def login(request):
	originalform = loginForm()
	if request.method == 'POST':
		form = loginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = User.objects.filter(username=username)
			if len(user) == 1:
				if check_password(password, user[0].password):
					request.session['account'] = {'id':user[0].id, 'username':user[0].username, 'activatied':user[0].activatied}
					return redirect('blog:home', page = 1)
				else:
					error = "Incorrect password!"
					return render(request, 'login.html', {'form': originalform, 'error': error}) 
			else:
				error = "Account does not exist!"
				return render(request, 'login.html', {'form': originalform, 'error': error})
	else:
		return render(request, 'login.html', {'form': originalform})


def logout(request):
	try:
		del request.session['account']
	except:
		pass
	return redirect('blog:login')

def signup(request):
	originalform = signupForm()
	if request.method == 'POST':
		form = signupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			password1 = form.cleaned_data['password1']
			password2 = form.cleaned_data['password2']
			if password1 != password2:
				error = "Passwords don't match!"
				return render(request, 'signup.html', {'form': originalform, 'error': error})
			elif len(password1) < 6:
				error = "Please make sure the length of your password is not shorter than 6!"
				return render(request, 'signup.html', {'form': originalform, 'error': error})
			else:
				emailSet = User.objects.filter(email = email)
				usernameSet = User.objects.filter(username=username)
				if len(emailSet) == 1 and len(usernameSet) == 0:
					error = "This email has been used!"
					return render(request, 'signup.html', {'form': originalform, 'error': error})
				elif len(emailSet) == 0 and len(usernameSet) == 1:
					error = "This username has been used!"
					return render(request, 'signup.html', {'form': originalform, 'error': error})
				elif len(emailSet) == 1 and len(usernameSet) == 1:
					error = "The username and email have been used!"
					return render(request, 'signup.html', {'form': originalform, 'error': error})
				else:
					password = make_password(password1, None, 'pbkdf2_sha256')
					user = User(username = username, email = email, password = password)
					user.save()
					user = User.objects.get(username=username)
					request.session['account'] = {'id':user.id, 'username':user.username, 'activatied':user.activatied}
					message = "Please check your email to activate the email address!"
					encrypted = str(user.id) + "theidofthisuseris" + str(user.id)
					encrypted = encode("mrtuesday1020", encrypted)
					host = request.get_host()
					emailbody = """Dear """ + username + """ :

Welcome to MrTuesday! Please activate your email address by click the link : """ + host + """/blog/confirm/""" + encrypted + """

Thank you!"""
					SendEmail("Activate Email.", emailbody, email)
					return render(request, 'blank.html', {'message':message})
	else:
		return render(request, 'signup.html', {'form': originalform})

def confirm(request, encrypted):
	try:
		decrypted = decode("mrtuesday1020", encrypted)
		decrypted_nb = re.sub("theidofthisuseris", "", decrypted)
		index = int(len(decrypted_nb)/2)
		userid = int(decrypted_nb[0:index])
		user = User.objects.get(pk=userid)
		user.activatied = True
		user.save()
		request.session['account'] = {'id':user.id, 'username':user.username, 'activatied':user.activatied}
		message = "Congratulations! You have activatied your email address!"
		return render(request, 'blank.html', {'message':message})
	except:
		message = "Sorry! Fail in activating!"
		return render(request, 'blank.html', {'message':message})
	
	

def post(request):
	account_id = request.session['account']['id']	
	title = request.POST.get("title",False)
	content = request.POST.get("content",False)
	tags = ['p', 'a', 'em', 'strong','code', 'pre', 'span']
	attrs = {
		'p':['style'],
		'a':['href', 'rel', 'target', 'title'],
		'code':['class'],
		'pre':['class'],
		'span':['class', 'style']
	}
	styles = ['text-align', 'text-decoration']
	content = bleach.clean(content, tags, attrs, styles)
	if request.method == "POST":
		article = Article(title = title, user_id = account_id, content = content)
		article.save()
		return redirect('blog:article', article_id = article.id)
	else:
		return render(request, 'post.html')

def article(request, article_id):
	account_id = request.session['account']['id'] if 'account' in request.session else 0
	# article
	sql = """select * from article as article,
			(select count(id) as comment_nb from comment where article_id = """ + str(article_id) + """) as comment_nb,
			(select count(*) as like_nb from `like` where article_id = """ + str(article_id) + """) as like_nb,
			(select count(*) as liked from `like` where article_id = """ + str(article_id) + """ and user_id = """ + str(account_id) + """) as liked
			where id = """ + str(article_id) + """ and is_shown = 'Y'"""
	article = RunSQL(sql)[0]
	# user
	author = User.objects.get(pk=article['user_id'])
	# comments
	comments = Comment.objects.filter(article_id = article_id).values()
	for comment in comments:
		com_user = User.objects.get(pk = comment['user_id'])
		comment['com_user'] = com_user
		replies = Reply.objects.filter(comment_id = comment['id']).values()
		for reply in replies:
			rep_user = User.objects.get(pk = reply['user_id'])
			reply['rep_user'] = rep_user
		comment['replies'] = replies
	return render(request, 'article.html', locals())

def profile(request, user_id):
	account_id = request.session['account']['id'] if 'account' in request.session else 0
	#user
	user = User.objects.get(pk = user_id)
	is_followed = Friend.objects.filter(user_id1 = account_id, user_id2 = user_id).count()
	#article
	article_sql = """select a.*, count(distinct c.id) as comment_nb, count(distinct l1.id)  as like_nb, count(distinct l2.id) as liked
			from article as a
			left join comment as c on a.id = c.article_id
			left join `like` as l1 on a.id = l1.article_id
			left join `like` as l2 on a.id = l2.article_id and l2.user_id = """ + str(account_id) + """
			where a.user_id = """ + str(user_id) + """
			group by a.id order by a.modified_time desc"""
	articles = RunSQL(article_sql)
	#follower
	follower_sql = """select f1.user_id1, count(distinct f2.id) as is_followed from friend f1 
					left join friend f2
					on f2.user_id2 = f1.user_id1 and f2.user_id1 = """ + str(account_id) + """
					where f1.user_id2 = """ + str(user_id) + """
					group by f1.id order by f1.time_stamp desc"""
	followers = RunSQL(follower_sql)
	for follower in followers:
		temp = User.objects.get(pk = follower['user_id1'])
		follower['user'] = temp
	#followiing
	following_sql = """select f1.user_id2, count(distinct f2.id) as is_followed from friend f1 
					left join friend f2
					on f2.user_id2 = f1.user_id2 and f2.user_id1 = """ + str(account_id) + """
					where f1.user_id1 = """ + str(user_id) + """
					group by f1.id order by f1.time_stamp desc"""
	followings = RunSQL(following_sql)
	for following in followings:
		temp = User.objects.get(pk=following['user_id2'])
		following['user'] = temp
	return render(request, 'profile.html', locals())

def edit(request):
	account_id = request.session['account']['id']
	user = User.objects.get(pk = account_id)

	if request.method == 'POST':
		# if the request is to upload image
		if 'imageUpload' in request.POST:
			# store the new image
			image = request.FILES['image']
			timestamp = re.sub("\.", "", str(time()))
			fss = FileSystemStorage(location='media/images')
			newImage = fss.save(timestamp + image.name, image)
			# delete the old image
			oldImage = re.sub("images/", "", user.image.name)
			if oldImage != 'default.png':
				fss.delete(oldImage)
			# save the name of new image to database
			user.image = "images/" + newImage
			user.save()
			return redirect('blog:profile', user_id = account_id)
		# if the request is to update information
		else:
			form = editForm(request.POST)
			if form.is_valid():
				user.username = form.cleaned_data['username']
				user.email = form.cleaned_data['email']
				user.profile = form.cleaned_data['profile']
				user.save()
				return redirect('blog:profile', user_id = account_id)
	else:
		form = editForm(initial = {'username': user.username, 'email':user.email, 'profile':user.profile})
		return render(request, 'edit.html', locals())

def notification(request):
	account_id = request.session['account']['id']
	# comments
	comment_sql = """select a.title, c.article_id, c.user_id, c.content, c.time_stamp from article a, comment c 
					where a.user_id = """ + str(account_id) + """
					and c.article_id = a.id
					order by c.time_stamp desc"""
	comments = RunSQL(comment_sql)
	for comment in comments:
		temp = User.objects.get(pk = comment['user_id'])
		comment['user'] = temp
	# replies
	reply_sql = """select c.content as comment, c.article_id, r.content, r.user_id , r.time_stamp from comment c, reply r
			where c.user_id = """ + str(account_id) + """
			and r.comment_id = c.id
			order by r.time_stamp  desc"""
	replies = RunSQL(reply_sql)
	for reply in replies:
		temp = User.objects.get(pk = reply['user_id'])
		reply['user'] = temp
	# likes
	like_sql = """select l.user_id, l.time_stamp, a.title, a.id as article_id from `like` l, article a
				where a.user_id = """ + str(account_id) + """
				and a.id = l.article_id
				order by l.time_stamp desc"""
	likes = RunSQL(like_sql)
	for like in likes:
		temp = User.objects.get(pk = like['user_id'])
		like['user'] = temp
	# friends
	friend_sql = """select f1.*, count(f2.id) as is_friend from friend f1
				left join friend f2
				on f2.user_id1 = f1.user_id2
				and f2.user_id2 = f1.user_id1
				where f1.user_id2 = """ + str(account_id) + """
				group by f1.id
				order by f1.time_stamp desc"""
	friends = RunSQL(friend_sql)
	for friend in friends:
		temp = User.objects.get(pk = friend['user_id1'])
		friend['user'] = temp
	return render(request, 'notification.html', locals())

def changepassword(request):
	account_id = request.session['account']['id']
	originalform = passwordForm()
	if request.method == 'POST':
		form = passwordForm(request.POST)
		if form.is_valid():
			password1 = form.cleaned_data['password1']
			password2 = form.cleaned_data['password2']
			if password1 != password2:
				error = "Passwords don't match!"
				return render(request, 'changepassword.html', {'form': originalform, 'error': error})
			elif len(password1) < 6:
				error = "Please make sure the length of your password is not shorter than 6!"
				return render(request, 'changepassword.html', {'form': originalform, 'error': error})
			else:
				password = make_password(password1, None, 'pbkdf2_sha256')
				user = User.objects.get(pk = account_id)
				user.password = password
				user.save()
				return redirect('blog:profile', user_id = account_id)
	else:
		return render(request, 'changepassword.html', {'form': originalform})

def search(request):
	if request.method == 'POST':
		page = request.POST.get("page", "page")
		keyword = request.POST.get("keyword", "keyword")
		selection = request.POST.get("selection", "selection")
		if selection == "user":
			results = User.objects.filter(username__icontains=keyword)
		else:
			results = Article.objects.filter(title__icontains=keyword) | Article.objects.filter(content__icontains=keyword)

		lenOfresults = len(results)

		# the number of items in one page
		limit = 3
		paginator = Paginator(results, limit)

		try:
			results = paginator.page(page)
		# if page is not an int number
		except PageNotAnInteger:
			results = paginator.page(1)
		# if page is too large
		except EmptyPage:
			results = paginator.page(paginator.num_pages)

		return render(request, 'result.html', locals())


def like(request):
	account_id = request.session['account']['id']
	article_id = request.GET.get("article_id")
	result = Like.objects.filter(article_id=article_id, user_id=account_id)
	# like
	if len(result) == 0:
		Like.objects.create(article_id=article_id, user_id=account_id)
		is_liked = 1
	# dislike
	else:
		Like.objects.get(article_id=article_id, user_id=account_id).delete()
		is_liked = 0
	count = Like.objects.filter(article_id=article_id).count()
	data = {"count":count,"is_liked":is_liked}
	return JsonResponse(data)

def comment(request):
	if request.method == "POST":
		account_id = request.session['account']['id']
		article_id = request.POST.get("article_id")
		comment_content = request.POST.get("comment_content")
		comment = Comment(article_id=article_id, user_id=account_id, content=comment_content)
		comment.save()
		user = User.objects.get(pk=account_id)
		data = {
			"comment":comment.content,
			"username":user.username,
			"user_id":user.id,
			"image":user.image.url,
		}
		return JsonResponse(data)


def reply(request):
	if request.method == "POST":
		account_id = request.session['account']['id']
		comment_id = request.POST.get("comment_id")
		reply_content = request.POST.get("reply_content")
		reply = Reply(comment_id=comment_id, user_id=account_id, content=reply_content)
		reply.save()
		user = User.objects.get(pk=account_id)
		data = {
			"reply":reply.content,
			"username":user.username,
			"user_id":user.id,
			"image":user.image.url,
		}
		return JsonResponse(data)

def follow(request):
	account_id = request.session['account']['id']
	user_id = request.GET.get("user_id")
	result = Friend.objects.filter(user_id1=account_id, user_id2=user_id)
	# follow
	if len(result) == 0:
		Friend.objects.create(user_id1=account_id, user_id2=user_id)
		followed = 1
	# unfollow
	else:
		Friend.objects.get(user_id1=account_id, user_id2=user_id).delete()
		followed = 0
	data = {"followed":followed}
	return JsonResponse(data)

######################### functions #########################
def RunSQL(sql):
	with connection.cursor() as cursor:
		cursor.execute(sql)
		rows = cursor.fetchall()
		fieldnames = [name[0] for name in cursor.description]
		results = []
		for row in rows:
			result = {}
			for i in range(len(row)):
				result[fieldnames[i]] = row[i]
			results.append(result)
	return results

def SendEmail(subject, message, receiver):
	sender = "MrTuesday"
	send_mail(
		subject,
		message,
		sender,
		[receiver],
		fail_silently=False,
		)

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)