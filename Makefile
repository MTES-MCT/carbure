 freeze:
	pip freeze | grep -v "pkg-resources" | grep -v "authtools" > requirements.txt

