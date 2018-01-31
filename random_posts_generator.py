import random
import datetime

# blogpost = {
#	'year': 2017,
#	'month': 1,
#	'day': 12,
#	'time': '30'
#	'title': 'Untitled',
# 	'author': 'Guksung An',
# 	'content': '...',
# 	'tags': ['personal', 'hockey'],
# }

NAMES = ['Guksung An', 'Vikramaditya Pagadala', 'Nitish Makam Prashanth', 'Tomas Mchale', 'Gema Cavitt', 'Scott Voth', 'Jeanice Niemi', 'Brynn Island', 'Dorian Vanbeek', 'Sebrina Edsall', 'Charlyn Orwig', 'Yuri Daigre', 'Lurline Koerner', 'Hettie Mueller', 'Noelia Elledge']

TAGS = ['personal', 'random', 'hockey', 'fishing', 'sports', 'life', 'education', 'database', 'computer', 'business', 'food', 'politics', 'miscellaneous', 'music', 'art', 'language', 'philosophy']

YEARS = range(1978, 2017)
MONTHS = range(1, 13)
DAYS = range(1, 29)

TITLE_TEMPLATE = 'Random Article #{}'

CONTENT_TEMPLATE = 'This is random article #{}. For this post I will ramble on and maybe later on this post will be edited to have more details.'

randompost = dict()

with open('blogpost_list.txt', 'w') as file:
	for i in range(1, 1001):
		random.shuffle(TAGS)
		randompost['author'] = random.choice(NAMES)
		randompost['title'] = TITLE_TEMPLATE.format(i)
		randompost['tags'] = TAGS[:random.randrange(1,4)]
		randompost['content'] = CONTENT_TEMPLATE.format(i)
		randompost['year'] = random.choice(YEARS)
		randompost['month'] = random.choice(MONTHS)
		randompost['day'] = random.choice(DAYS)
		randompost['time'] = str(datetime.datetime.now().time())
		# literal eval does not support datetime
		# randompost['last edit time'] = datetime.datetime.now()
		
		file.write(str(randompost)+'\n')
