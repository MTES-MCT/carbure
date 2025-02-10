from django.test import TestCase as DjangoTestCase

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from core.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory
from transactions.models import Depot
from tiruert.models.operation import create_tiruert_operations_from_lots



class TestCase(DjangoTestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )
        
        CarbureLot.objects.all().delete()
        
        feedstock1 = MatierePremiere.objects.filter(category="CONV").first()
        biofuel1 = Biocarburant.objects.get(code="ETH")
        
        feedstock2 = MatierePremiere.objects.filter(category="ANN-IX-A").first()
        biofuel2 = Biocarburant.objects.get(code="EMAG")
        
        depot1 = Depot.objects.first()
        
        # LOTS OK
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock1,
            biofuel=biofuel1,
            lot_status="FROZEN",
            delivery_type="BLENDING",
            volume=1000,
            ghg_total = 1.3,
            carbure_delivery_site=depot1,
        )
        
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock1,
            biofuel=biofuel1,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=2000,
            ghg_total = 2.5,
            carbure_delivery_site=depot1,
        )
        
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock1,
            biofuel=biofuel1,
            lot_status="ACCEPTED",
            delivery_type="DIRECT",
            volume=3000,      
            ghg_total=3.4,
            carbure_delivery_site=depot1,
        )
        
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock1,
            biofuel=biofuel1,
            lot_status="ACCEPTED",
            delivery_type="RFC",    
            volume=4000,
            ghg_total = 4.8,
            carbure_delivery_site=depot1, 
        )
        
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock2,
            biofuel=biofuel2,
            lot_status="ACCEPTED",
            delivery_type="RFC",     
            volume=5000,
            ghg_total = 5.6,
            carbure_delivery_site=depot1,
        )
        
        # LOTS NOK
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock1,
            biofuel=biofuel1,
            lot_status="DRAFT",
            delivery_type="BLENDING", 
            volume=1000,
            carbure_delivery_site=depot1,
        )
        
        CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=feedstock2,
            biofuel=biofuel2,
            lot_status="ACCEPTED",
            delivery_type="EXPORT",    
            volume=1000,
            carbure_delivery_site=depot1,
        )
        
        lots = CarbureLot.objects.filter(carbure_client=self.entity)
        create_tiruert_operations_from_lots(lots)
        
        
        
        
        
        
    
    

        
        