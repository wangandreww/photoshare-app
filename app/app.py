######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################
from datetime import date
from django.forms import NullBooleanField
from django.test import tag
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Huyphan007!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT user_password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT user_password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		print(password)
		first = request.form.get('firstname')
		last = request.form.get('lastname')
		dob = request.form.get('DOB')
		if (dob == ''):
			dob = '1000-01-01'
		gender = request.form.get('gender')
		hometown = request.form.get('hometown')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, user_password,first_name,last_name,DOB,gender,hometown) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}','{6}' )".format(email, password,first,last,dob,gender,hometown)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserFriends(uid):
	return 1

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_list = getUserPhotos(uid)
	album_list = getUserAlbums(uid)
	return render_template('profile.html',photos = photo_list, albums = album_list, base64=base64)

def getUserAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name,album_id FROM Album WHERE user_id ='{0}'".format(uid))
	return cursor.fetchall() 

@app.route('/deletePhoto', methods=['POST'])
@flask_login.login_required
def deletePhoto():
	pid = request.args.get('pid')
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(pid))
	conn.commit()
	return render_template('hello.html', message="Photo deleted")

@app.route('/deleteAlbum', methods=['POST'])
@flask_login.login_required
def deleteAlbum():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	aid = request.args.get('aid')
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Album WHERE album_id = '{0}'".format(aid))
	conn.commit()
	return render_template('hello.html', message="Album deleted")

def myFunc(tuple):
    return tuple[1]

def getEmailFromId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0]

@app.route('/friendRecs', methods = ['GET'])
def friendRecs():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id2 FROM Friends WHERE user_id1 = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	current_friendlist = cursor.fetchall()
	masterList = []
	for x in current_friendlist:
		cursor = conn.cursor()
		cursor.execute("SELECT user_id2 FROM Friends WHERE user_id1 = '{0}'".format(x[0])) #gets each of your friend's friendlist
		friendlist = cursor.fetchall()
		masterList.append(friendlist)
	mydict = {}
	print(masterList)
	for i in range(len(masterList)):
		for j in range(len(masterList[i])):
			name = masterList[i][j][0]
			if name in mydict:
				mydict.update({name:(mydict.get(masterList[i][j][0]) + 1)})
			else:
				mydict[name] = 1
	print(mydict)
	mutual = []
	for key in mydict:
		if mydict.get(key) >= 2:
			mutual.append([key,mydict.get(key)])
	mutual.sort(key=myFunc)
	mutual.reverse()
	for x in mutual:
		if((x[0],) in current_friendlist):
			mutual.remove(x)
	for x in mutual:
		x[0] = getEmailFromId(x[0])
	return render_template('friendRecs.html', mutual_list = mutual, message = 'Here are your friend recommendations')

def userScores():
	''' score = comments + posts '''
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, COUNT(user_id) FROM Comments GROUP BY user_id")
	commentScores = cursor.fetchall()
	scores = []

	for i in commentScores:
		scores.append((i[0], i[1]))

	cursor.execute("SELECT user_id, COUNT(user_id) FROM Pictures GROUP BY user_id")
	photoScores = cursor.fetchall()

	print(commentScores)
	print(photoScores)

	finalscore = {}

	for i in photoScores:
		if getEmailFromId(i[0]) not in finalscore:
			finalscore[getEmailFromId(i[0])] = i[1]
		else:
			finalscore[getEmailFromId(i[0])] += i[1]
	for i in commentScores:
		if i[0] == None:
			continue
		elif getEmailFromId(i[0]) not in finalscore:
			finalscore[getEmailFromId(i[0])] = i[1]
		else:
			finalscore[getEmailFromId(i[0])] += i[1]

	return finalscore

@app.route('/ranks', methods=['GET'])
def ranks():
	scoreDict = userScores()
	print(scoreDict)
	tempUsers = sorted(scoreDict, key=scoreDict.get, reverse=True)
	userList = []

	for i in tempUsers:
		userList.append((i, scoreDict[i]))
	
	if(len(userList) <= 10):
    		return render_template('getRanks.html', message= 'Here are the rankings', ranked = userList)
	else:
		newranks = []
		for x in range(10):
			newranks.append(userlist[x])
		return render_template('getRanks.html', message = 'Here are the rankings', ranked = newranks)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST']) 
@flask_login.login_required 
def upload_file(): 
	if request.method == 'POST': 
		tags = request.form.get('tags') 
		tag_list = tags.split(' ')
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		album_id = getAlbumID(request.form.get('album'),uid)
		if (album_id == ()):
			return render_template('hello.html', message='The Album you have selected is not valid')
		cursor = conn.cursor()
		print(album_id)
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s )''', (photo_data, int(uid), caption,int(album_id)))
		conn.commit()
		
		pid = getPhotoId(caption, photo_data, album_id)
		cursor = conn.cursor() 
		for x in range(len(tag_list)):
			if tagCheck(tag_list[x]):
				cursor.execute("INSERT INTO Tag (tag_description) VALUES ('{0}')".format(tag_list[x]))
				cursor.execute("INSERT INTO CreatePictureTag (picture_id, tag_description) VALUES ('{0}', '{1}')".format(pid,tag_list[x]))
				
			else: 
				cursor.execute("INSERT INTO CreatePictureTag (picture_id, tag_description) VALUES ('{0}', '{1}')".format(pid,tag_list[x]))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

def tagCheck(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_description FROM Tag WHERE tag_description = '{0}'".format(tag))
	res = cursor.fetchall()
	if res == ():
		return True 
	else:
		return False 

def getPhotoId(caption, data, albums_id):
	cursor = conn.cursor()
	cursor.execute("""SELECT picture_id FROM Pictures WHERE caption = %s AND imgdata = %s AND album_id = %s""", (caption, data, int(albums_id)))
	return cursor.fetchone()[0]

def getAlbumID(albumname,uid):
	print(albumname)
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Album WHERE album_name = '{0}' AND user_id = '{1}'".format(albumname, uid))
	result = cursor.fetchone()[0]
	return result 

@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def add_friend():
	
	if request.method == 'POST':
		try:
			email=request.form.get('email')
			print(email)
		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('friends'))

		if ((email,) in getUserList()):
			curr_id = getUserIdFromEmail(flask_login.current_user.id)
			friend_id = getUserIdFromEmail(email)
			if (curr_id != friend_id):
				cursor = conn.cursor()
				print(cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(curr_id, friend_id)))
				conn.commit()
				return render_template('friends.html', message='Friend Added!')
			else:
				print("couldn't find all tokens")
				return flask.redirect(flask.url_for('add'))
		else:
			return render_template('friends.html', message='Friend does not exist')
	#The method is GET so we return a  HTML form to upload the a photo.	
	else:
		# cursor = conn.cursor()
		# cursor.execute("SELECT first_name, last_name, email FROM Users")
		# data = cursor.fetchall()
		# print(data)
		return render_template('friends.html')

@app.route('/listFriends', methods = ['GET'])
@flask_login.login_required
def listFriends():
	curr_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM Users AS U WHERE U.user_id IN (SELECT DISTINCT user_id2 FROM Friends as F2 WHERE F2.user_id1 = '{0}')".format(curr_id))
	friendsList = cursor.fetchall()
	return render_template('listFriends.html',friends = friendsList)

@app.route('/viewcomments/<photo_id>', methods = ['GET'])
def viewComments(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT comment_description,comment_timestamp,user_id,picture_id FROM Comments WHERE picture_id = '{0}'".format(photo_id)) 
	comment_list = cursor.fetchall()
	return render_template('viewcomments.html', message = 'Comments for this post', commentList = comment_list, photo = getPhotoById(photo_id), base64=base64)

def getPhotoById(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall()

@app.route('/searchComments', methods=['POST', 'GET'])
def searchComments():
	if flask.request.method == 'POST':
		comment = request.form.get('comment')
		print(comment)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*), U.user_id, U.first_name, U.last_name FROM Comments C JOIN Users U WHERE comment_description = '{0}' AND U.user_id = C.user_id GROUP BY user_id ORDER BY COUNT(*) DESC".format(comment))
		userList = cursor.fetchall()
		print(userList)
		return render_template('searchComments.html', userList = userList)
	else:
		return render_template('searchComments.html')
	
def getUserIdFromPhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures where picture_id = '{0}'".format(pid))
	result = cursor.fetchone() 
	print(result)
	return result

@app.route('/comments', methods=['POST'])  
def add_comment():
	pid = request.args.get('pid')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_list = getPhotos()
	album_list = getAlbums()

	if getUserIdFromPhoto(pid) != uid:
		comment = request.form.get('comment') 
		print(comment)
		uid = getUserIdFromEmail(flask_login.current_user.id)
		current_date = date.today()
		photo_id = request.args.get('pid')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Comments(comment_description, comment_timestamp, user_id, picture_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(comment, current_date, uid, photo_id))
		conn.commit()
		return render_template('browse.html',message = "Comment Added!",photos=photo_list,base64=base64,albums = album_list)
	else:
		return render_template('browse.html', message="You cannot comment on your own photo", photos=photo_list, base64=base64,albums=album_list)

def likeCheck(user_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, user_id FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(photo_id, user_id))
	res = cursor.fetchall()
	if res == ():
		return True 
	else:
		return False 

@app.route('/add_like', methods=['POST'])
@flask_login.login_required
def add_like(): 
	likes = 0
	photo_id = request.args.get('pid')
	user_id = getUserIdFromEmail(flask_login.current_user.id)

	if likeCheck(photo_id, user_id) == True: 
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Likes(like_counter, picture_id, user_id) VALUES ('{0}', '{1}', '{2}')".format(likes, photo_id, user_id))
		cursor.execute("UPDATE Likes SET like_counter = like_counter + 1")
		conn.commit()
		return render_template('browse.html', message = "Like added")
	else:
		return render_template('browse.html', message = "You have already liked this photo")

@app.route('/show_likes/<pid>', methods=['GET'])
def show_likes(pid): 
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(DISTINCT L.user_id), U.first_name, U.last_name FROM Likes L JOIN Users U  WHERE L.picture_id = '{0}' AND L.user_id = U.user_id GROUP BY L.user_id".format(pid))
	userList = cursor.fetchall()
	likes = len(userList)
	print(userList)
	photo_list = getPhotos()
	album_list = getAlbums()
	print(album_list)
	return render_template('likes.html', likes = likes, userList = userList, message = "Here are all the users who have liked this photo", photo = getPhotoById(pid), base64=base64)

# @app.route('tags', methods=["POST"])	

@app.route('/album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	
	if request.method == 'POST':
		try:
			album=request.form.get('album')
			

		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('friends'))

		current_date = date.today()
		curr_id = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Album (album_name,user_id,create_date) VALUES ('{0}', '{1}','{2}')".format(album,curr_id, current_date))
		conn.commit()

		
		return render_template('album.html', message='Album Created!')

	#The method is GET so we return a  HTML form to upload the a photo.	
	else:
		# cursor = conn.cursor()
		# cursor.execute("SELECT first_name, last_name, email FROM Users")
		# data = cursor.fetchall()
		# print(data)
		return render_template('album.html')

@app.route('/search', methods=['GET', 'POST'])
def searchFriends():
	if request.method == 'POST':
		try:
			first_name = request.form.get('firstname')
			last_name = request.form.get('lastname')
		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('friends'))

		cursor = conn.cursor()
		print(first_name)
		print(last_name)
		cursor.execute("SELECT email, first_name, last_name, hometown, gender FROM Users WHERE first_name = '{0}' AND last_name = '{1}'".format(first_name, last_name))
		results = cursor.fetchall()
		print (results)
		return render_template('search.html', name=flask_login.current_user.id, message='Search Result', result=results)
	#The method is GET so we return a  HTML form to upload the a photo.	
	else:
		# cursor = conn.cursor()
		# cursor.execute("SELECT first_name, last_name, email FROM Users")
		# data = cursor.fetchall()
		# print(data)
		return render_template('search.html')

@app.route('/browse', methods=['GET'])
def browse():
	photo_list = getPhotos()
	album_list = getAlbums()
	return render_template('browse.html',message = "Here are all photos!",photos=photo_list,base64=base64,albums = album_list)

@app.route('/browse/<album_id>', methods=['GET'])
def browseAlbum(album_id):
	photo_list = getAlbumPics(album_id)
	album_list = getAlbums()
	
	return render_template('browse.html', message = "Here are all photos in this Album!",photos=photo_list,base64=base64,albums = album_list)
 
def getAlbumPics(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall()

def getAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT album_name,album_id FROM Album")
	return cursor.fetchall()

def getPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures")
	return cursor.fetchall()

	

def getUserPhotos(id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id= '{0}'".format(id))
	return cursor.fetchall()


@app.route('/browseByTags', methods=['GET'])
@flask_login.login_required
def userTagList():
	curr_id = getUserIdFromEmail(flask_login.current_user.id)
	tag_list = getUserTags(curr_id)
	print(tag_list)
	return render_template('browseByTags.html',tags = tag_list)

@app.route('/userTagPhoto/<tag>', methods=['GET'])
def userTagPhoto(tag):
	curr_id = getUserIdFromEmail(flask_login.current_user.id)
	photo_list = getUserPhotoByTag(tag,curr_id)
	return render_template('userTagPhoto.html',photos = photo_list,base64=base64,tag_name= tag)

@app.route('/allTags', methods=['GET'])
@flask_login.login_required
def allTags():
	tag_list = getAllTags()
	print(tag_list)
	return render_template('browseByTags.html', alltags = tag_list)

@app.route('/allTagPhoto/<tag>', methods=['GET'])
@flask_login.login_required
def allTagsPhoto(tag):
	photo_list = getPhotosByTag(tag)
	return render_template('allTagPhoto.html',photos = photo_list,base64=base64,tag_name= tag)

@app.route('/popularTags', methods=['GET'])
def popularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT T.tag_description FROM CreatePictureTag AS T, Pictures AS P WHERE T.picture_id = P.picture_id GROUP BY T.tag_description order by count(P.picture_id) desc limit 5")
	result = cursor.fetchall()
	return render_template('popularTags.html', alltags = result)


def getPopularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT T.tag_description FROM CreatePictureTag AS T, Pictures AS P WHERE T.picture_id = P.picture_id GROUP BY T.tag_description order by count(P.picture_id) desc limit 5")
	return cursor.fetchall()


def allTags():
	tag_list = getAllTags()
	print(tag_list)
	return render_template('browseByTags.html', alltags = tag_list)

def getPhotosByTag(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT p.imgdata, p.picture_id, p.caption FROM CreatePictureTag c, Pictures p WHERE c.picture_id = p.picture_id AND c.tag_description = '{0}'".format(tag))
	return cursor.fetchall()

def getUserPhotoByTag(tag,id):
	cursor = conn.cursor()
	cursor.execute("SELECT p.imgdata, p.picture_id, p.caption FROM CreatePictureTag c, Pictures p WHERE c.picture_id = p.picture_id AND p.user_id= '{0}' AND c.tag_description = '{1}'".format(id,tag))
	return cursor.fetchall()

def getAllTags():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Tag")
	return cursor.fetchall()

def getUserTags(id):
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT c.tag_description FROM CreatePictureTag c, Pictures p WHERE c.picture_id = p.picture_id AND p.user_id= '{0}'".format(id))
	return cursor.fetchall()

@app.route('/photoRec', methods = ['GET'])
def photoRec():
	tags = getPopularTags()
	print(tags)
	tag_list = []
	# photo_list = getPhotos()
	mydict = {}
	for x in tags:
		tag_list.append(x[0])
	for y in tag_list:
		
		recList = getPhotosByTag(y)
		for photo in recList:
			if(photo[1] in mydict):
				mydict.update({photo[1]: (mydict[photo[1]] + 1)})
			else:
				mydict[photo[1]] = 1
	reclistfinal = sorted(mydict, key=mydict.get, reverse=True)
	listphoto = ()
	for x in reclistfinal:
		cursor = conn.cursor()
		cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(x))
		listphoto+=(cursor.fetchall())
	return render_template('photoRec.html', message = 'You may also like these photos', photos = listphoto, base64=base64)



@app.route('/searchTags', methods = ['GET','POST'])

def searchBy():
	if flask.request.method == 'GET':
		return render_template('searchTags.html')
	else:

		try:

			tags = request.form.get('tags')
			tag_list = tags.split(' ')

		except:

			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('searchTags'))
		resultList = []
		photo_id_by_tags = []
		for x in tag_list:
			try:
				tuplephotolist = getPhotosByTag(x)
				print('SUCESS')
			except:
				return render_template('searchTags.html', message='The Tag does not Exist')
			photo_id_per_tag = []
			for i in range(len(tuplephotolist)):
				photo_id_per_tag.append(tuplephotolist[i][1])
			photo_id_by_tags.append(photo_id_per_tag)
		
		first_tag_photos = photo_id_by_tags[0]
		rest_tag_photos = photo_id_by_tags[1:len(photo_id_by_tags)]
		for i in first_tag_photos:
			valid = True
			for j in rest_tag_photos:
				if(photoExistInList(i,j)):
					continue
				else:
					valid = False
					break
			if(valid == True):
				resultList.append(i)
			else:
				continue
		photoList = []
		for x in resultList:
			cursor = conn.cursor()
			cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(x))
			temp = cursor.fetchall()
			photoList.append(temp[0])
		return render_template('searchTags.html', message = 'Search Result', result = photoList, base64=base64)

def photoExistInList(photo_id, listOfPhotos):
	if(photo_id in listOfPhotos):
		return True
	else:
		return False

#default page
@app.route("/", methods=['GET'])
def hello():
	# if(getAlbumID("Memories",1) == () ):
	# 	print(1)
	
	return render_template('hello.html', message='Welecome to Photoshare')

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
#THINGS SKIPPED FOR NOW 

#user activity