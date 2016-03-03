from bottle import route, run, template, request, response, static_file
from BeautifulSoup import BeautifulSoup
import urllib, re, json

date_pattern_basic = re.compile('[0-9][0-9]/[0-9][0-9]/20[0-9][0-9]')
date_pattern_full = re.compile('[0-9][0-9]/[0-9][0-9]/20[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
host = 'https://decide.madrid.es'

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@route('/fonts/<filename>')
def server_static(filename):
    return static_file(filename, root='./fonts')


@route('/thread/')
def index():

	#Get the HTML
	thread_url = host+'/'+request.query.type+'/'+request.query.id + '&order=oldest'
	thread_html = urllib.urlopen(thread_url).read()
	parsed_html = BeautifulSoup(thread_html)
	thread_json = parse_thread(thread_url,parsed_html)
 
	next_page_exists = True
	# Parse the next page of comments if it exists
	while next_page_exists:
		next_page_exists = False
		pagination = parsed_html.find('div', { 'class' : 'pagination-centered' })
		if str(pagination) != 'None':
			if str(pagination.find('a', { 'rel' : 'next' })) != 'None':
				next_page_exists = True
				next_url = str(host + pagination.find('a', { 'rel' : 'next' })['href'])
				print 'Fetching ' + next_url
				f = urllib.urlopen(next_url+ '&order=oldest')
				parsed_html = BeautifulSoup(f.read())
				comments_next_page = parse_thread(next_url,parsed_html)['children']
				for comment in comments_next_page:
					thread_json['children'].append(comment)

	# Dump data into data.json
	f=open('./static/data.json','w')
	f.write(json.dumps(thread_json , sort_keys=False, indent=4, separators=(',', ': ')) )
	f.close()

	# Return index.html
	f = open('./static/index.html')
	a = f.read()
	f.close()
	return template(a)


#### PARSING METHODS ####


# Parse thread
def parse_thread(thread_url, parsed_html):

	depth = 0
	if 'debates' in thread_url:
		id = thread_url.split('debates/')[1]
		type = 'debate'
	elif 'proposals' in thread_url:
		id = thread_url.split('proposals/')[1]
		type = 'proposal'
        if '?' in id:
                id = id.split('?')[0]

	# Check that the thread exists (some have been deleted)
	title = str(parsed_html.find('h1').getText().encode('utf8'))
	if title != '404':

		# Get general metadata
		paragraphs = parsed_html.find('section', { 'class' : type+'-show' }).findAll('p')
                post_html = parsed_html.find('section', { 'class' : type+'-show'})
		message = ''
		for paragraph in paragraphs:
				message = message + str(paragraph) 
		user = str(post_html.find('span', { 'class' : 'author' }).getText().encode('utf8'))
		if len(user)>50:
			user = user[:50]
		ts = str(date_pattern_basic.findall(str(post_html))[0])
		ts = ts[6:10] + '-' + ts[3:5] + '-' + ts[0:2]

		# Dump general metadata
		data = {}
		data['title'] = title
		data['message'] = message
		data['depth'] = depth
		data['user'] = user
		data['ts'] = ts
		
		# Get and dump debate metadata
		if type == 'debate':
			votes_total_count = str(parsed_html.find('div', { 'class' : 'votes' }).find('span', { 'class' : 'total-votes' }).getText().encode('utf8').split(' ')[0])
			if votes_total_count == 'Sin':
				votes_total_count = '0';
			votes_against_percentage = str(parsed_html.find('div', { 'class' : 'against inline-block' }).find('span').getText().encode('utf8').split('%')[0])
			votes_favor_percentage = 100 - int(votes_against_percentage)
			votes_against_count = int (votes_total_count) * int (votes_against_percentage) / 100
			votes_favor_count = int (votes_total_count) - votes_against_count
			data['votes_favor_count'] = votes_favor_count
			data['votes_against_count'] = votes_against_count
			data['size'] = int(votes_total_count)

		# Get and dump proposal metadata			
		elif type == 'proposal':
			supports = parsed_html.find('div', { 'class' : 'supports' })
			supports_total_count = supports.find('span', { 'class' : 'total-supports' }).getText().encode('utf8').split(' ')[0].replace(',', '.')
			if supports_total_count == 'Sin':
				supports_total_count = '0';
			data['votes_favor_count'] = supports_total_count
			data['votes_against_count'] = 0
			data['size'] = int(supports_total_count)

			
		# Parse the comments if they exist
		comments_html = parsed_html.find('div', { 'id' : 'comments'})
		comments = comments_html.findAll('div', { 'class' : 'row'},recursive=False)
		array = '[]'
		comments_json  = json.loads(array)
		for comment in comments:	
			comment_json = parse_comment(comment,host+'/'+type+'s/'+ id,'d'+id,user,depth+1)			
			if comment_json != None: comments_json.append(comment_json)
		if len(comments_json) >0: data['children'] = comments_json
			
		return data




# Parse a comment
def parse_comment(comment_html, thread_id, in_reply_to_id, in_reply_to_user,depth):

	# Get metadata
	comment_html = comment_html.find('div', { 'class' : 'comment small-12 column'},recursive=False)
	id = str(comment_html['id'].split('_')[1])
	if '?' in id:
		id = id.split('?')[0]
        message = ''
        if str(comment_html.find('div', { 'class' : re.compile(r'\bcomment-user\b') })) != 'None':
				message =  str(comment_html.find('div', { 'class' : re.compile(r'\bcomment-user\b') }))

	# Ignore empty messages (bug)
	if message != '':
		ts = str(date_pattern_full.findall(str(comment_html))[0])
		ts = ts[6:10] + '-' + ts[3:5] + '-' + ts[0:2] + ' ' + ts[11:]
		user = ''
		if str(comment_html.find('span', { 'class' : 'user-user' })) != 'NoneType':
			user = str(comment_html.find('span', { 'class' : 'user-name' }).getText().encode('utf8'))
			if len(user)>50:
				user = user[:50]
		# Ignore wrong users (bug)
		if not '' in user:
			votes_favor_count = str(comment_html.find('span', { 'class' : 'in_favor' }).getText().encode('utf8'))
			votes_against_count = str(comment_html.find('span', { 'class' : 'against' }).getText().encode('utf8'))
			comments_html = comment_html.find('div', { 'class' : 'comment-children'},recursive=False)
			comments = comments_html.findAll('div', { 'class' : 'row'},recursive=False)
			comments_count = len(comments)
			type = thread_id.split('/')[3]
			type = type[:len(type)-1]

			# Parse the comments of the comment if they exist
			array = '[]'
			comments_json  = json.loads(array)
			for comment in comments:
				comment_json = parse_comment(comment,host+'/'+type+'s/'+ id,'d'+id,user,depth+1)			
				if comment_json != None: comments_json.append(comment_json)

			# Dump metadata
			data = {}
			data['message'] = message
			data['user'] = user
			data['ts'] = ts
			data['votes_favor_count'] = votes_favor_count
			data['votes_against_count'] = votes_against_count
			data['size'] = int(votes_favor_count) + int(votes_against_count)
			if len(comments_json) >0: data['children'] = comments_json
			return data

run(host='localhost', server='paste', port=8080, debug=True)
