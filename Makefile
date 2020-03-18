freeze:
	pip freeze | grep -v "pkg-resources" | grep -v "authtools" > requirements.txt

fixtures:
	# static data
	python3 /app/web/manage.py dumpdata core.biocarburant > /app/web/fixtures/biocarburants.json
	python3 /app/web/manage.py dumpdata core.matierepremiere > /app/web/fixtures/matierespremieres.json
	python3 /app/web/manage.py dumpdata core.pays > /app/web/fixtures/countries.json
	# test data
	python3 /app/web/manage.py dumpdata authtools.user > /app/web/fixtures/authtools_user.json
	python3 /app/web/manage.py dumpdata core.entity > /app/web/fixtures/entities.json
	python3 /app/web/manage.py dumpdata core.userpreferences > /app/web/fixtures/userpreferences.json
	python3 /app/web/manage.py dumpdata core.userrights > /app/web/fixtures/userrights.json

	python3 /app/web/manage.py dumpdata producers.productionsite > /app/web/fixtures/productionsites.json
	python3 /app/web/manage.py dumpdata producers.productionsiteinput > /app/web/fixtures/productionsiteinputs.json
	python3 /app/web/manage.py dumpdata producers.productionsiteoutput > /app/web/fixtures/productionsiteoutputs.json
	python3 /app/web/manage.py dumpdata producers.producercertificate > /app/web/fixtures/producercertificates.json

