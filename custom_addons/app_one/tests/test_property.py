from odoo import fields
from odoo.tests.common import TransactionCase


class TestProperty(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestProperty, self).setUp()

        # Store today's date to ensure consistent testing
        self.today_date = fields.Date.today()

        self.property_01_record = self.env["property"].create(
            {
                "ref": "PRT1000",
                "name": "Property 1000",
                "description": "des",
                "postcode": "23234",
                "date_availability": self.today_date,
                "bedrooms": 10,
                "expected_price": 20000,
            }
        )

    def test_01_property_values(self):
        # Get the property record
        property_id = self.property_01_record
        # Manually assert each field value
        self.assertEqual(property_id.ref, "PRT1000")
        self.assertEqual(property_id.name, "Property 1000")
        self.assertEqual(property_id.description, "des")
        self.assertEqual(property_id.postcode, "23234")
        self.assertEqual(property_id.date_availability, self.today_date)
        self.assertEqual(property_id.bedrooms, 10)
        self.assertEqual(property_id.expected_price, 20000)
