#encoding: utf-8
import json, MySQLdb
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def file_get_contents(filename):
	with open(filename) as a_file:
		return a_file.read()

def date_handler(obj):
	x = obj.isoformat() if hasattr(obj, 'isoformat') else obj
	return x.replace('T', ' ')

def mysql_connect():
	return MySQLdb.connect('localhost', 'root', '1234', 'dbapi')

def mysql_set_cursor(db):
	db.set_character_set('utf8')
	cursor = db.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection = utf8;')
	return cursor

def mysql_close(db, cursor):
	cursor.close()
	db.close()

def mysql_close_error(db, cursor):
	db.rollback()
	mysql_close(db, cursor)
	return {'code': 0, 'message': 'blah blah blah'}

def empty_list(db, cursor):
	mysql_close(db, cursor)
	return {'code': 0, 'response': []}

def get_user_by_id(id, cursor):
	query_source = "SELECT * FROM dbapi_user WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return {'id': row[0], 'isAnonymous': row[1], 'username': row[2], 'about': row[3], 'name': row[4], 'email': row[5], 'followers': get_followers(id, cursor), 'following': get_following(id, cursor), 'subscriptions': get_subscriptions(id, cursor)}

def get_email_by_id(id, cursor):
	query_source = "SELECT email FROM dbapi_user WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return row[0]

def get_followers(id, cursor):
	query_source = "SELECT follower_id FROM dbapi_follow WHERE user_id = %s"
	cursor.execute(query_source, id)
	rows = cursor.fetchall()
	if not rows:
		return []
	answer = []
	for row in rows:
		answer.append(get_email_by_id(row[0], cursor))
	return answer

def get_following(id, cursor):
	query_source = "SELECT user_id FROM dbapi_follow WHERE follower_id = %s"
	cursor.execute(query_source, id)
	rows = cursor.fetchall()
	if not rows:
		return []
	answer = []
	for row in rows:
		answer.append(get_email_by_id(row[0], cursor))
	return answer

def get_slug_by_id(id, cursor):
	query_source = "SELECT slug FROM dbapi_thread WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return row[0]

def get_subscriptions(id, cursor):
	query_source = "SELECT thread_id FROM dbapi_subscription WHERE user_id = %s"
	cursor.execute(query_source, id)
	rows = cursor.fetchall()
	if not rows:
		return []
	answer = []
	for row in rows:
		answer.append(row[0])
	return answer

def get_forum_by_id(id, cursor):
	query_source = "SELECT * FROM dbapi_forum WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return {'id': row[0], 'name': row[1], 'short_name': row[2], 'user': get_email_by_id(row[3], cursor)}


def get_short_name_by_id(id, cursor):
	query_source = "SELECT short_name FROM dbapi_forum WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return row[0]

def get_id_by_short_name(short_name, cursor):
	query_source = "SELECT id FROM dbapi_forum WHERE short_name = %s"
	cursor.execute(query_source, short_name)
	row = cursor.fetchone()
	return row[0]

def get_thread_by_id(id, cursor):
	query_source = "SELECT * FROM dbapi_thread WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return {'id': row[0], 'isDeleted': row[1], 'forum': get_short_name_by_id(row[2], cursor), 'title': row[3], 'isClosed': row[4], 'user': get_email_by_id(row[5], cursor), 'date': row[6], 'message': row[7], 'slug': row[8], 'likes': row[9], 'dislikes': row[10], 'points': row[11], 'posts': row[12]}

def get_id_by_email(email, cursor):
	query_source = "SELECT id FROM dbapi_user WHERE email = %s"
	cursor.execute(query_source, email)
	row = cursor.fetchone()
	return row[0]

def get_post_by_id(id, cursor):
	query_source = "SELECT * FROM dbapi_post WHERE id = %s"
	cursor.execute(query_source, id)
	row = cursor.fetchone()
	return {'id': row[0], 'parent': row[1], 'isApproved': row[2], 'isHighlighted': row[3], 'isEdited': row[4], 'isSpam': row[5], 'isDeleted': row[6], 'date': row[7], 'thread': row[8], 'message': row[9], 'user': get_email_by_id(row[10], cursor), 'forum': get_short_name_by_id(row[11], cursor), 'likes': row[12], 'dislikes': row[13], 'points': row[14]}

@csrf_exempt
def clear(request):
	query_source = file_get_contents('/home/nap/askpupkin/dbapi.sql')
	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	cursor.execute(query_source)
	# db.commit()
	mysql_close(db, cursor)
	return HttpResponse('Cleared!')

@csrf_exempt
def user_create(request):
	data_source = json.loads(request.body)
	try:
		data_source['isAnonymous']
	except KeyError:
		data_source['isAnonymous'] = 0
	query_source = "INSERT INTO dbapi_user (isAnonymous, username, about, name, email) VALUES (%s, %s, %s, %s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['isAnonymous'], data_source['username'], data_source['about'], data_source['name'], data_source['email']])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	query_answer = "SELECT max(id) FROM dbapi_user"
	cursor.execute(query_answer)
	row = cursor.fetchone()

	data_answer = {'id': row[0], 'isAnonymous': data_source['isAnonymous'], 'username': data_source['username'], 'about': data_source['about'], 'name': data_source['name'], 'email': data_source['email']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def forum_create(request):
	data_source = json.loads(request.body)
	query_source = "INSERT INTO dbapi_forum (name, short_name, user_id) VALUES (%s, %s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['name'], data_source['short_name'], get_id_by_email(data_source['user'], cursor)])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	query_max_id = "SELECT max(id) FROM dbapi_forum"
	cursor.execute(query_max_id)
	row = cursor.fetchone()

	try:
		data_answer = get_forum_by_id(row[0], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

def forum_details(request):
	data_source = request.GET.copy()
	try:
		data_source['related']
	except KeyError:
		data_source['related'] = []
	query_source = "SELECT * FROM dbapi_forum WHERE short_name = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	cursor.execute(query_source, data_source['forum'])
	row = cursor.fetchone()

	if not row:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	if 'user' in data_source['related']:
		data_answer['user'] = get_user_by_id(row[3], cursor)
	else:
		if not data_source['related']:
			data_answer['user'] = get_email_by_id(row[3], cursor)

	data_answer = {'id': row[0], 'name': row[1], 'short_name': row[2], 'user': data_answer['user']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

def forum_listUsers(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since_id']
	except KeyError:
		data_source['since_id'] = 1
	query_source = "SELECT user_id FROM dbapi_post WHERE forum_id = %s and user_id >= %s ORDER BY user_id " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	cursor.execute(query_source, [get_id_by_short_name(data_source['forum'], cursor), data_source['since_id'], int(data_source['limit'])])
	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_user_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_create(request):
	data_source = json.loads(request.body)
	try:
		data_source['isDeleted']
	except KeyError:
		data_source['isDeleted'] = 0
	query_source = "INSERT INTO dbapi_thread (isDeleted, forum_id, title, isClosed, user_id, date, message, slug) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['isDeleted'], get_id_by_short_name(data_source['forum'], cursor), data_source['title'], data_source['isClosed'], get_id_by_email(data_source['user'], cursor), data_source['date'], data_source['message'], data_source['slug']])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	query_max_id = "SELECT max(id) FROM dbapi_thread"
	cursor.execute(query_max_id)
	row = cursor.fetchone()

	data_answer = {'date': data_source['date'], 'forum': data_source['forum'], 'id': row[0], 'isClosed': data_source['isClosed'], 'isDeleted': data_source['isDeleted'], 'message': data_source['message'], 'slug': data_source['slug'], 'title': data_source['title'], 'user': data_source['user']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

@csrf_exempt
def thread_close(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_thread SET isClosed = 1 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_open(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_thread SET isClosed = 0 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_remove(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_thread SET isDeleted = 1 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_restore(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_thread SET isDeleted = 0 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_update(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_thread SET message = %s, slug = %s WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['message'], data_source['slug'], data_source['thread']])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_thread_by_id(data_source['thread'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

@csrf_exempt
def thread_subscribe(request):
	data_source = json.loads(request.body)
	query_source = "INSERT INTO dbapi_subscription (thread_id, user_id) VALUES (%s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['thread'], get_id_by_email(data_source['user'], cursor)])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread'], 'user': data_source['user']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def thread_unsubscribe(request):
	data_source = json.loads(request.body)
	query_source = "DELETE FROM dbapi_subscription WHERE thread_id = %s AND user_id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['thread'], get_id_by_email(data_source['user'], cursor)])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'thread': data_source['thread'], 'user': data_source['user']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def user_follow(request):
	data_source = json.loads(request.body)
	query_source = "INSERT INTO dbapi_follow (user_id, follower_id) VALUES (%s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [get_id_by_email(data_source['followee'], cursor), get_id_by_email(data_source['follower'], cursor)])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_user_by_id(get_id_by_email(data_source['follower'], cursor), cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def user_unfollow(request):
	data_source = json.loads(request.body)
	query_source = "DELETE FROM dbapi_follow WHERE user_id = %s AND follower_id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [get_id_by_email(data_source['followee'], cursor), get_id_by_email(data_source['follower'], cursor)])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_user_by_id(get_id_by_email(data_source['follower'], cursor), cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def user_updateProfile(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_user SET about = %s, name = %s WHERE email = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['about'], data_source['name'], data_source['user']])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_user_by_id(get_id_by_email(data_source['user'], cursor), cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def post_create(request):
	data_source = json.loads(request.body)
	try:
		data_source['parent']
	except KeyError:
		data_source['parent'] = None
	try:
		data_source['isApproved']
	except KeyError:
		data_source['isApproved'] = 0
	try:
		data_source['isHighlighted']
	except KeyError:
		data_source['isHighlighted'] = 0
	try:
		data_source['isEdited']
	except KeyError:
		data_source['isEdited'] = 0
	try:
		data_source['isSpam']
	except KeyError:
		data_source['isSpam'] = 0
	try:
		data_source['isDeleted']
	except KeyError:
		data_source['isDeleted'] = 0
	query_source = "INSERT INTO dbapi_post (parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted, date, thread_id, message, user_id, forum_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['parent'], data_source['isApproved'], data_source['isHighlighted'], data_source['isEdited'], data_source['isSpam'], data_source['isDeleted'], data_source['date'], data_source['thread'], data_source['message'], get_id_by_email(data_source['user'], cursor), get_id_by_short_name(data_source['forum'], cursor)])
		cursor.execute("UPDATE dbapi_thread SET posts = posts + 1 WHERE id = %s", data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	query_max_id = "SELECT max(id) FROM dbapi_post"
	cursor.execute(query_max_id)
	row = cursor.fetchone()

	data_answer = {'date': data_source['date'], 'forum': data_source['forum'], 'id': row[0], 'isApproved': data_source['isApproved'], 'isDeleted': data_source['isDeleted'], 'isEdited': data_source['isEdited'], 'isHighlighted': data_source['isHighlighted'], 'isSpam': data_source['isSpam'], 'message': data_source['message'], 'thread': data_source['thread'], 'user': data_source['user']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}

	return HttpResponse(json.dumps(answer, default=date_handler))

def post_details(request):
	data_source = request.GET.copy()
	try:
		data_source['related']
	except KeyError:
		data_source['related'] = []

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		data_answer = get_post_by_id(data_source['post'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	if 'user' in data_source['related']:
		data_answer['user'] = get_user_by_id(get_id_by_email(data_answer['user'], cursor), cursor)
	if 'forum' in data_source['related']:
			data_answer['forum'] = get_forum_by_id(get_id_by_short_name(data_answer['forum'], cursor), cursor)
	if 'thread' in data_source['related']:
		data_answer['thread'] = get_thread_by_id(data_answer['thread'], cursor)

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def thread_details(request):
	data_source = request.GET.copy()
	try:
		data_source['related']
	except KeyError:
		data_source['related'] = []

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		data_answer = get_thread_by_id(data_source['thread'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	if 'user' in data_source['related']:
		data_answer['user'] = get_user_by_id(get_id_by_email(data_answer['user'], cursor), cursor)
	if 'forum' in data_source['related']:
		data_answer['forum'] = get_forum_by_id(get_id_by_short_name(data_answer['forum'], cursor), cursor)

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def forum_listPosts(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'
	try:
		data_source['related']
	except KeyError:
		data_source['related'] = []
	query_source = "SELECT id FROM dbapi_post WHERE forum_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [get_id_by_short_name(data_source['forum'], cursor), data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_post_by_id(row[0], cursor))
		if 'user' in data_source['related']:
			data_answer[-1]['user'] = get_user_by_id(get_id_by_email(data_answer[-1]['user'], cursor), cursor)
		if 'forum' in data_source['related']:
				data_answer[-1]['forum'] = get_forum_by_id(get_id_by_short_name(data_answer[-1]['forum'], cursor), cursor)
		if 'thread' in data_source['related']:
			data_answer[-1]['thread'] = get_thread_by_id(data_answer[-1]['thread'], cursor)

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}

	return HttpResponse(json.dumps(answer, default=date_handler))

def forum_listThreads(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'
	try:
		data_source['related']
	except KeyError:
		data_source['related'] = []
	query_source = "SELECT id FROM dbapi_thread WHERE forum_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [get_id_by_short_name(data_source['forum'], cursor), data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_thread_by_id(row[0], cursor))
		if 'user' in data_source['related']:
			data_answer[-1]['user'] = get_user_by_id(get_id_by_email(data_answer[-1]['user'], cursor), cursor)
		if 'forum' in data_source['related']:
				data_answer[-1]['forum'] = get_forum_by_id(get_id_by_short_name(data_answer[-1]['forum'], cursor), cursor)

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def user_listPosts(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'
	query_source = "SELECT id FROM dbapi_post WHERE user_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [get_id_by_email(data_source['user'], cursor), data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_post_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def thread_listPosts(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'
	query_source = "SELECT id FROM dbapi_post WHERE thread_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [data_source['thread'], data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_post_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

@csrf_exempt
def post_remove(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_post SET isDeleted = 1 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['post'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'post': data_source['post']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def post_restore(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_post SET isDeleted = 0 WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['post'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	data_answer = {'post': data_source['post']}

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

@csrf_exempt
def post_update(request):
	data_source = json.loads(request.body)
	query_source = "UPDATE dbapi_post SET message = %s WHERE id = %s"

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, [data_source['message'], data_source['post']])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_post_by_id(data_source['post'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

@csrf_exempt
def thread_vote(request):
	data_source = json.loads(request.body)
	if data_source['vote'] == -1:
		query_source = "UPDATE dbapi_thread SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s"
	else:
		if data_source['vote'] == 1:
			query_source = "UPDATE dbapi_thread SET likes = likes + 1, points = points + 1 WHERE id = %s"
		else:
			return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['thread'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_thread_by_id(data_source['thread'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

@csrf_exempt
def post_vote(request):
	data_source = json.loads(request.body)
	if data_source['vote'] == -1:
		query_source = "UPDATE dbapi_post SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s"
	else:
		if data_source['vote'] == 1:
			query_source = "UPDATE dbapi_post SET likes = likes + 1, points = points + 1 WHERE id = %s"
		else:
			return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)
	try:
		cursor.execute(query_source, data_source['post'])
		db.commit()
	except MySQLdb.IntegrityError:
		answer = mysql_close_error(db, cursor)
		return HttpResponse(json.dumps(answer))

	try:
		data_answer = get_post_by_id(data_source['post'], cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def post_list(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		data_source['forum']
		query_source = "SELECT id FROM dbapi_post WHERE forum_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"
		forum_or_thread = get_id_by_short_name(data_source['forum'], cursor)
	except KeyError:
		query_source = "SELECT id FROM dbapi_post WHERE thread_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"
		forum_or_thread = data_source['thread']
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	data_answer = []

	try:
		cursor.execute(query_source, [forum_or_thread, data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_post_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def thread_list(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since']
	except KeyError:
		data_source['since'] = '1970-01-01 00:00:01'

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		data_source['forum']
		query_source = "SELECT id FROM dbapi_thread WHERE forum_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"
		forum_or_user = get_id_by_short_name(data_source['forum'], cursor)
	except KeyError:
		query_source = "SELECT id FROM dbapi_thread WHERE user_id = %s and date >= %s ORDER BY date " + data_source['order'] + " LIMIT %s"
		try:
			forum_or_user = get_id_by_email(data_source['user'], cursor)
		except TypeError:
			return HttpResponse(json.dumps(mysql_close_error(db, cursor)))
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	data_answer = []

	try:
		cursor.execute(query_source, [forum_or_user, data_source['since'], int(data_source['limit'])])
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_thread_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))

def user_listFollowers(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since_id']
	except KeyError:
		data_source['since_id'] = 1
	query_source = "SELECT id FROM dbapi_user WHERE id IN (SELECT follower_id FROM dbapi_follow WHERE user_id = %s and follower_id >= %s) ORDER BY name " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [get_id_by_email(data_source['user'], cursor), data_source['since_id'], int(data_source['limit'])])
	except TypeError:
		return mysql_close_error(db, cursor)

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_user_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

def user_listFollowing(request):
	data_source = request.GET.copy()
	try:
		data_source['limit']
	except KeyError:
		data_source['limit'] = 18446744073709551615
	try:
		data_source['order']
	except KeyError:
		data_source['order'] = 'DESC'
	try:
		data_source['since_id']
	except KeyError:
		data_source['since_id'] = 1
	query_source = "SELECT id FROM dbapi_user WHERE id IN (SELECT user_id FROM dbapi_follow WHERE follower_id = %s and user_id >= %s) ORDER BY name " + data_source['order'] + " LIMIT %s"

	data_answer = []

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		cursor.execute(query_source, [get_id_by_email(data_source['user'], cursor), data_source['since_id'], int(data_source['limit'])])
	except TypeError:
		return mysql_close_error(db, cursor)

	rows = cursor.fetchall()

	if not rows:
		return HttpResponse(json.dumps(empty_list(db, cursor)))

	for row in rows:
		data_answer.append(get_user_by_id(row[0], cursor))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer))

def user_details(request):
	data_source = request.GET.copy()

	data_answer = {}

	db = mysql_connect()
	cursor = mysql_set_cursor(db)

	try:
		data_answer = get_user_by_id(get_id_by_email(data_source['user'], cursor), cursor)
	except TypeError:
		return HttpResponse(json.dumps(mysql_close_error(db, cursor)))

	mysql_close(db, cursor)

	answer = {'code': 0, 'response': data_answer}
	return HttpResponse(json.dumps(answer, default=date_handler))
