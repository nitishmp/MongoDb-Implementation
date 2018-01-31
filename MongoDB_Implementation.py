from pymongo import MongoClient
import sys
import os
import psutil
import subprocess
from tkinter import filedialog, messagebox
from tkinter import *
from PIL import Image, ImageTk
import datetime
import re
import ast
from PIL import Image, ImageTk

# path to mongod.exe
MONGOD_DIR = r'"C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe"'

'''
Check mongod before running this script...
'''

print('checking if mongodb is running...')

processes_names = []

for p in psutil.process_iter():
	try:
		processes_names.append(p.name())
	except psutil.NoSuchProcess:
		pass

mongodb_running = 'mongod.exe' in processes_names

if mongodb_running:
	print('mongodb is running. will proceed to interact with the database')
else:
	print('mongodb was not running.')
	print('***********************')
	print('running mongod.exe now')
	print('***********************')
	subprocess.Popen(MONGOD_DIR, shell=True)

try:
	client = MongoClient()
except pymongo.errors.ConnectionFailure as e:
	print('Could not connect to MongoDB', e)
	sys.exit(1)

try:
	print('databases:', client.database_names())
except pymongo.erros.ServerSelectionTimeoutError as e:
	print('Run mongod command before running this script')
	raise e
	sys.exit(1)

collection = client.BlogCollection
db = collection.blogposts

class Window(Tk):
	def __init__(self, parent=None, title='my blog posts'):
		Tk.__init__(self, parent)
		self.parent = parent
		self.title(title)
		self.geometry('600x600')
		self.initialize()

	def initialize(self):
		label0 = Label(self, text='My blog', font=('TkDefaultFont', 14))
		label0.pack()

		img = Image.open('typewriter.jpg')
		img = img.resize((400, 250), Image.ANTIALIAS)
		photo = ImageTk.PhotoImage(img)
		foreground = Label(image=photo, width=400, height=250)
		foreground.image = photo
		foreground.pack()

		Label(self, text='Number of blogs: {}'.format(db.count())).pack()

		button0 = Button(self, text='write a new post', command=self.newpost)
		button1 = Button(self, text='search archive', command=self.search)
		button2 = Button(self, text='upload posts', command=self.loadfile)

		for button in (button0, button1, button2):
			button.config(width=30, pady=5)
			button.pack(pady=20)
		
		frame = Frame()
		frame.pack()
		
		self.mainloop()
	
	def newpost(self):
		npost = NewPost()

	def search(self):
		archive = PostArchive()

	def loadfile(self):
		openfiletypes = [('text files','.txt')]
		# not specifying initialdir opens current working directory
		fname = filedialog.askopenfilename(filetypes=openfiletypes)
		
		if not fname:
			return

		with open(fname, 'r') as file:
			for line in file:
				data = line.strip('\n')
				blogpost = ast.literal_eval(data)
				# literal_eval does not support datetime
				blogpost['last edit time'] = datetime.datetime.now()
				db.insert_one(blogpost)
			

class PostArchive(Toplevel):
	def __init__(self):
		Toplevel.__init__(self)
		self.title('Archive')
		self.results_limit = 20
		self.initUI()

	def initUI(self):
		self.geometry('400x600')

		Label(self, text='fill in blanks to search relevant posts').pack()

		self.fields = ('author', 'title', 'tags', 'content', 'year', 'month')
		self.widgets = dict()

		for field in self.fields:
			self.widgets[field] = dict()
			row = self.widgets[field]['frame'] = Frame(self)
			self.widgets[field]['label'] = Label(row, text=field, width=15)
			self.widgets[field]['entry'] = Entry(row)
			row.pack(side=TOP, fill=X, padx=5, pady=5)
			self.widgets[field]['label'].pack(side=LEFT)
			self.widgets[field]['entry'].pack(side=RIGHT, expand=YES, fill=X)

		self.widgets[self.fields[0]]['entry'].focus()

		search = Button(self, text='search', command=self.search)
		search.pack()

		Label(self, text='query results up to {}'.format(self.results_limit)).pack()
		self.results_list = Listbox(self)
		self.results_list.pack()

		select = Button(self, text='select post', command=self.select)
		select.pack()

	def search(self):
		query = dict()
		for field in self.fields:
			f = self.widgets[field]['entry'].get()
			if f:
				query[field] = f
		self.results = [post for post in db.find(query)]

		self.results_list.delete(0, END)
		for title in (post['title'] for post in self.results[:self.results_limit]):
			self.results_list.insert(END, title)

		if not self.results:
			messagebox.showinfo(message='no blog post found')

	def select(self):
		try:
			choice = self.results_list.curselection()[0]
			print('choice', choice)
			blogpost = self.results[choice]
			showpost = UpdatePost(blogpost)
		except IndexError:
			messagebox.showerror(message='you have not selected a post')

class Post(Toplevel):
	def __init__(self):
		Toplevel.__init__(self)
		self.initUI()

	def initUI(self):
		self.geometry('400x600')

		self.fields = ('author', 'title', 'tags', 'content')
		self.widgets = dict()

		for field in self.fields:
			self.widgets[field] = dict()
			row = self.widgets[field]['frame'] = Frame(self)
			self.widgets[field]['label'] = Label(row, text=field, width=15)
			self.widgets[field]['entry'] = Entry(row)
			row.pack(side=TOP, fill=X, padx=5, pady=5)
			self.widgets[field]['label'].pack(side=LEFT)
			self.widgets[field]['entry'].pack(side=RIGHT, expand=YES, fill=X)

		self.widgets[self.fields[0]]['entry'].focus()
		
		scrollbar = Scrollbar(self.widgets['content']['frame'])
		scrollbar.pack(side=RIGHT, fill=Y)

		# replace entry with text
		self.widgets['content']['entry'].destroy()
		self.widgets['content']['entry'] = Text(self.widgets['content']['frame'], wrap=WORD, yscrollcommand=scrollbar.set)
		self.widgets['content']['entry'].pack()

		scrollbar.config(command=self.widgets['content']['entry'].yview)

	def getpost(self):
		blogpost = dict()
		for field in self.fields:
			if field == 'content':
				# content has text widget instead of entry
				blogpost[field] = self.widgets[field]['entry'].get(1.0, 'end-1c')
			else:
				blogpost[field] = self.widgets[field]['entry'].get()

		blogpost['tags'] = re.split(r', *', blogpost['tags'])
		
		time = datetime.datetime.now()
		blogpost['year'] = time.year
		blogpost['month'] = time.month
		blogpost['day'] = time.day
		blogpost['time'] = str(time.time())
		blogpost['last edit time'] = time

		return blogpost

	def setpost(self, blogpost):
		for field in self.fields:
			text = '' if field not in blogpost else blogpost[field]
			if field == 'tags':
				text = ', '.join(text)
			entry = self.widgets[field]['entry']

			if type(entry) == Entry:
				entry.delete(0, END)
				entry.insert(0, text)
			elif type(entry) == Text:
				entry.insert(1.0, text)

class NewPost(Post):
	def initUI(self):
		Post.initUI(self)

		save = Button(self, text='save post', command=self.savepost)
		save.pack()

	def savepost(self):
		blogpost = self.getpost()
		print('blogpost\n', blogpost)

		db.insert_one(blogpost)
		messagebox.showinfo(message='successfully saved')

class UpdatePost(Post):
	def __init__(self, blogpost):
		self.blogpost = blogpost
		Post.__init__(self)

	def initUI(self):
		Post.initUI(self)
		self.setpost(self.blogpost)

		bottom = Frame(self)
		bottom.pack()

		update = Button(bottom, text='update post', command=self.updatepost)
		update.pack(side=LEFT)

		remove = Button(bottom, text='remove post', command=self.removepost)
		remove.pack(side=LEFT)

	def _id(self):
		return {'_id': self.blogpost['_id']}

	def updatepost(self):
		# remove and insert because of http://stackoverflow.com/questions/25128974/cant-replace-mongo-document
		self.removepost()
		updated = self.getpost()
		for date in ('year', 'month', 'day', 'time'):
			updated[date] = self.blogpost[date]
		# updated['last edit time'] = datetime.datetime.now()
		db.insert_one(updated)
		messagebox.showinfo(message='successfully updated')

		# db.update_one(self._id(), self.getpost())

	def removepost(self):
		db.remove(self._id())
		messagebox.showinfo(message='successfully removed')
		# messagedialog


def main():
	app = Window()

if __name__ == '__main__':
	main()


'''
schema for the blog posts

blogpost = {
	'author': 'Guksung An',
	'title': 'Untitled',
	'tags': ['personal', 'hockey'],
	'content': '...',
	'year': 2017,
	'month': 1,
	'day': 12,
	'time': datetime.datetime.now().time()
	'last edit time': datetime.datetime.now()
}

'''

'''
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it
solved by following this link:
http://stackoverflow.com/questions/26585433/mongodb-failed-to-connect-to-127-0-0-127017-reason-errno10061
'''

'''
for shutting down mongod.exe, simply ctrl-c on the cmd prompt which
ran mongod
http://zqscm.qiniucdn.com/data/20110726173430/index.html
it will show something like
2017-03-30T12:52:48.766-0400 I NETWORK  [consoleTerminate] shutdown: going to cl
ose listening sockets...
2017-03-30T12:52:48.768-0400 I NETWORK  [consoleTerminate] closing listening soc
ket: 424
2017-03-30T12:52:48.772-0400 I NETWORK  [consoleTerminate] shutdown: going to fl
ush diaglog...
2017-03-30T12:52:48.774-0400 I FTDC     [consoleTerminate] Shutting down full-ti
me diagnostic data capture
2017-03-30T12:52:48.904-0400 I STORAGE  [consoleTerminate] WiredTigerKVEngine sh
utting down
2017-03-30T12:52:49.345-0400 I STORAGE  [consoleTerminate] shutdown: removing fs
 lock...
2017-03-30T12:52:49.354-0400 I CONTROL  [consoleTerminate] now exiting
2017-03-30T12:52:49.356-0400 I CONTROL  [consoleTerminate] shutting down with co
de:12
'''
