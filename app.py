from bottle import route, run, template, request, response, static_file
import urllib2, json

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@route('/fonts/<filename>')
def server_static(filename):
    return static_file(filename, root='./fonts')


@route('/thread/')
def index():

	id = request.query.id
	type = request.query.type

	thread_json = json.loads(fetch_url('https://decidim.barcelona/api/'+type+'s/'+id+'.json'))[type]
	thread_json['depth'] = 0
	thread_json['children'] = []

	page = 1
	while page!=None:
		comments_page = json.loads(fetch_url('https://decidim.barcelona/api/comments.json?commentable[id]='+id+'&commentable[type]='+type.title()+'&page='+str(page)))
		for comment in comments_page['comments']:
			comment['children'] = []
			if comment['ancestry'] == None:
				comment['depth'] = 1
				thread_json['children'].append(comment)
			else:
				comment['depth'] = 2+comment['ancestry'].count('/')
				ancestry_ids = comment['ancestry'].split('/')
				base = thread_json['children']
				for ancestry_id in ancestry_ids:
					for child in base:
						if str(child['id'])==ancestry_id:
							new_base = child['children']
					base = new_base
				base.append(comment)

		page = comments_page['meta']['next_page']


	# Dump data into data.json
	f=open('./static/data.json','w')
	f.write(json.dumps(thread_json , sort_keys=False, indent=4, separators=(',', ': ')) )
	f.close()

	# Return index.html
	f = open('./static/index.html')
	a = f.read()
	f.close()
	return template(a)

def fetch_url(query):
	req = urllib2.Request(query)
	response = urllib2.urlopen(req)
	return response.read()


run(host='localhost', port=8080, debug=True)
