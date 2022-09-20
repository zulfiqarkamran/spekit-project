# spekit-project

Documentation
=============
	url: https://spekit-project.herokuapp.com

Admin Credentials
=================
	admin url: https://spekit-project.herokuapp.com/admin
	admin user: u15371
	admin password: 123


Setup Virtual Environment To Run Tests
======================================
	- download code
	- run: python3 -m venv /path/to/new/virtual/environment
	- create new folder inside the new virtual environment and move the downloaded code there
	- go inside the newly created folder using terminal
	- run: Scripts\activate.bat
	- run: pip install -r requirements.txt
	- navigate to dms/settings.py and uncomment the line starting with "SECRET_KEY"
	- run: python3 manage.py runserver
	- in a separate terminal, activate the virtual environment
	- run: python3 manage.py test
	
Location of tests file: dmsapi/tests.py