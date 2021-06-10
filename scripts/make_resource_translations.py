import json
import django
import os
from django.db.models import F

import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    TEST=(bool, False)
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()
from core.models import MatierePremiere, Biocarburant, Pays


queries = {
    'feedstocks.json': MatierePremiere.objects.all().annotate(value=F('code'), label=F('name')).values('value', 'label'),
    'biofuels.json': Biocarburant.objects.all().annotate(value=F('code'), label=F('name')).values('value', 'label'),
    'countries.json': Pays.objects.all().annotate(value=F('code_pays'), label=F('name')).values('value', 'label')
}


def make_translation_file(filename, query, lang):
    translation = {}

    for result in query:
        translation[result['value']] = result['label']

    file_path = os.path.join(env('CARBURE_HOME'), 'front/public/locales', lang, filename)
    file = open(file_path, "w+")
    serialized = json.dumps(translation, indent=2, ensure_ascii=False)

    file.write(serialized)
    file.close()


for filename, query in queries.items():
    for lang in ('fr', 'en'):
        make_translation_file(filename, query, lang)
