Todoist-Toggl-Sync
==================

This little python script allows to synchronize the task manager 
https://todoist.com and the time tracker app https://www.toggl.com.

The sync works by creating a Toggl project for each Todoist project,
and by creating a time entry with 0 seconds in Toggl for each Todoist task,
so the Toggl autocompletion for time entries works fine.

The only requirement is python and the python requests library.

To use this, all you have to do is run tts.py regularily like this:

`python tts.py TODOIST_EMAIL TODOIST_PW TOGGL_EMAIL TOGGL_PW`


Setup
-----

* Install python requests library:
  `pip install requests`
* Get the code:
  Download and unpack https://github.com/theduke/todoist-toggl-sync/archive/master.zip
  or do `git clone https://github.com/theduke/todoist-toggl-sync.git`
* Run for testing: 
  `python tts.py TODOIST_EMAIL TODOIST_PW TOGGL_EMAIL TOGGL_PW`
* Set up a cronjob to run the sync every 10 minutes on a Linux server:
  `crontab -e`
  Add the line
  `*/10 * * * * /PATH/TO/TTS/tts.py TODOIST_EMAIL TODOIST_PW TOGGL_EMAIL TOGGL_PW`
  Save the file
* Done, your new Todoist tasks will automatically show up in Toggl.

Authors
-------

Christoph Herzog - chris@theduke.at


License
-------

Code is under the MIT license (see LICENSE.txt). 
