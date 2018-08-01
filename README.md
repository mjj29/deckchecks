To use this you will need:

* Apache, python2 and mysql
* Add a mysql\_passwords.py containing 3 variables:

	database='databasename'
	user='username'
	password='password'

* create a database + user and password with the above details in your mysql
* update .htaccess to match your apache config
* run create.py - after removing the early exit which is there to stop you accidentally overwriting your DB
* either run addevent.py, or browse to the web interface and import an event from the CFB pairings site
