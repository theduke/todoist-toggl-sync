#! /usr/bin/env python

import requests
import datetime
import sys, os
import json
from pprint import pprint

class TodoistApi(object):

	base_url = 'https://api.todoist.com/'
	api_url = base_url + 'API/'
	sync_url = base_url + 'TodoistSync/v5.3/get'

	def __init__(self):
		self.email = None
		self.password = None
		self.token = None

	def login(self, email, password):
		self.email = email
		self.password = password

		r = requests.post(self.api_url + 'login', data={
			'email': email,
			'password': password,
		})

		data = r.json()

		if data == "LOGIN_ERROR":
			raise Exception("Invalid credentials: {}//{}".format(
				email, password))

		self.token = data['api_token']


	def get_data(self):
		data = {
			'projects': []
		}

		r = requests.post(self.sync_url, data={
			'api_token': self.token, 
			'seq_no': 0
		})
		todo_data = r.json()

		# Map needed for adding tasks to the project.
		project_id_map = {}

		# Find all projects.

		# Map needed for properly reflecting the hierarchy.
		last_project_by_indent = {}

		# Sort projects by item_order, since hierarchy can not be inferred
		# otherwise.
		projects = sorted(todo_data['Projects'], key=lambda x: x['item_order'])
		for project in projects:
			# Skip inbox.
			if project['name'] == 'Inbox':
				continue

			project['children'] = []
			project['tasks'] = []
			project_id_map[project['id']] = project

			if project['indent'] > 1:
				last = last_project_by_indent[project['indent'] - 1]
				last['children'].append(project)
			else:
				data['projects'].append(project)

			last_project_by_indent[project['indent']] = project

		# Find tasks and add them to the projects.
		tasks = sorted(todo_data['Items'], 
			key=lambda x: str(x['project_id']) + str(x['item_order']))

		# Map needed for properly reflecting the hierarchy.
		last_task_by_indent = {}
		for task in tasks:
			task['children'] = []

			if task['indent'] > 1:
				last = last_task_by_indent[task['indent'] - 1]
				last['children'].append(task)
			else:
				project_id_map[task['project_id']]['tasks'].append(task)

			last_task_by_indent[task['indent']] = task

		return data


class TogglApi(object):

	base_url = "https://www.toggl.com/api/v8/"

	def __init__(self):
		self.email = None
		self.password = None

	def get(self, path, data={}):
		return requests.get(self.base_url + path, data=data, 
			auth=(self.email, self.password)).json()

	def post(self, path, data={}):
		return requests.post(self.base_url + path, data=data, 
			auth=(self.email, self.password)).json()

	def login(self, email, password):
		self.email = email
		self.password = password

	def get_data(self):
		data = {
			'projects': {}
		}

		raw = self.get('me?with_related_data=true', data={})['data']

		# Handle case if no projects or no time entries exist.

		projects = raw['projects'] if 'projects' in raw else []
		for proj in projects:
			proj['time_entries'] = []
			data['projects'][proj['id']] = proj

		entries = raw['time_entries'] if 'time_entries' in raw else []
		for entry in entries:
			data['projects'][entry['pid']]['time_entries'].append(entry)

		return data

	def create_project(self, name):
		print("Creating new project {}".format(name))

		data = {
			'project': {
				'name': name,
			}
		}
		data = self.post('projects', data=json.dumps(data))

		proj = data['data']
		proj['time_entries'] = []

		return proj

	def create_time_entry(self, description, duration, pid, start=None):
		start = start or datetime.datetime.now().isoformat() + 'Z'

		data = {
			'time_entry': {
				'description': description,
				'duration': duration,
				'start': start,
				'pid': pid,
			}
		}
		data = self.post('time_entries', data=json.dumps(data))

		entry = data['data']

		return entry

	def sync_todoist_data(self, todo_data):
		print("Syncing toggle with todoist data.")

		# First get own data for comparison.
		data = self.get_data()

		for todo_project in todo_data['projects']:
			self.sync_project(todo_project, data)

	def sync_project(self, todo_project, data):
		print("Syncing project " + todo_project['name'])

		# Try to find project.
		# If it does not exist, create it.
		toggle_projects = [p for p in data['projects'].values() 
							if p['name'] == todo_project['name']]

		project = toggle_projects[0] if len(toggle_projects)\
							else self.create_project(todo_project['name'])

		# For each todoist task, check if a time entry already exists.
		# Otherwise create time entry with 0 seconds.
		self.sync_tasks(project, data, todo_project['tasks'])

		# Handle child projects.
		for child in todo_project['children']:
			self.sync_project(child, data)

	def sync_tasks(self, project, data, tasks):
		for task in tasks:
			entries = [e for e in project['time_entries'] if e['description'] == task['content']]
			if not len(entries):
				print("Creating time entry '{}' for project '{}'".format(
					task['content'], project['name']))
				self.create_time_entry(task['content'], 0, project['id'])

			# Handle child tasks.
			if task['children']:
				self.sync_tasks(project, data, task['children'])


class Syncer(object):

	def __init__(self):
		self.todoist = TodoistApi()
		self.toggl = TogglApi()

	def set_credentials(self, todoist_email, todoist_pw, toggl_email, toggl_pw):
		self.todoist.login(todoist_email, todoist_pw)
		self.toggl.login(toggl_email, toggl_pw)

	def sync(self):
		print("Syncing bettwen {} (ToDoist) and {} (Toggl)".format(
			self.todoist.email, self.toggl.email))

		todoist_data = self.todoist.get_data()
		self.toggl.sync_todoist_data(todoist_data)

def run_sync(todoist_email, todoist_pw, toggl_email, toggl_pw):
	s = Syncer()
	s.set_credentials(todoist_email, todoist_pw, toggl_email, toggl_pw)
	s.sync()

if __name__ == '__main__':
	args = sys.argv[1:]
	
	if not len(args):
		print("Usage: tts CMD")	
		print("    sync email-todoist pw-todoist [email-toggl pw-toggl]")
		sys.exit(1)

	cmd = args.pop(0)

	if cmd == 'sync':
		email_todoist = email_toggl = args.pop(0)
		pw_todoist = pw_toggl = args.pop(0)

		if len(args) == 2:
			email_toggl = args.pop(0)
			pw_toggl = args.pop(0)

		run_sync(email_todoist, pw_todoist, email_toggl, pw_toggl)
