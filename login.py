
from deck_mysql import DeckDB

def check_login(output, event, password, redirect):
	with DeckDB() as db:
		id = db.getEventId(event)
		evPass = db.getEventPassword(id)
		if evPass == password:
			return True
		else:
			print """
<h2>Login required</h2>
<form method='post' action='%s'>
Password: <input type='text' name='password'/><br/>
<input type='submit' />
</form>
""" % redirect
			return False
