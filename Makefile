 freeze:
	pip freeze | grep -v "pkg-resources" | grep -v "authtools" > requirements.txt && echo "git+git://github.com/mplanes/django-authtools" >> requirements.txt


