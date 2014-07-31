Todoist-Toggl-Sync
==================

This little python script allows to synchronize the task manager 
https://todoist.com and the time tracker app https://www.toggl.com.

The sync works by creating a Toggl project for each Todoist project,
and by creating a time entry with 0 seconds in Toggl for each Todoist task,
so the Toggl autocompletion for time entries works fine.

To use this, all you have to do is run tts.py regularily like this:

`python tts.py TODOIST_EMAIL TODOIST_PW TOGGL_EMAIL TOGGL_PW`


Authors
-------

Christoph Herzog - chris@theduke.at


License
-------

Code is under the MIT license (see LICENSE.txt). 
