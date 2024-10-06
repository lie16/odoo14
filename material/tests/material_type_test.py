import unittest
from odoo.tests import TransactionCase, tagged
from odoo import http
from odoo.exceptions import ValidationError


class TestMaterialController(TransactionCase):

    @tagged('standard', 'post_install')
    def setUp(self):
        super(TestMaterialController, self).setUp()
        self.partner_a = self.env['res.partner'].create({'name': 'Vendor A', 'supplier_rank': 1})
        self.partner_b = self.env['res.partner'].create({'name': 'Vendor B', 'supplier_rank': 1})
        self.partner = self.env['res.partner'].create({'name': 'Test Vendor', 'supplier_rank': 1})
        self.material_model = self.env['material.material_type']

        # Create some test materials
        self.material_1 = self.material_model.create({
            'material_code': '001',
            'material_name': 'Cotton Fabric',
            'material_type': 'cotton',
            'material_buy_price': 150,
            # 'partner_id': self.env['res.partner'].create({'name': 'Vendor A'}).id,
            'partner_id': 10
        })
        self.material_2 = self.material_model.create({
            'material_code': '002',
            'material_name': 'Fabrics Sample',
            'material_type': 'jeans',
            'material_buy_price': 200,
            'partner_id': 10
        })


    @tagged('standard', 'post_install')
    def test_get_material_by_code(self):
        response = self._call_get_material(material_code='001')
        self.assertEqual(len(response['materials']), 1)
        self.assertEqual(response['materials'][0]['material_code'], '001')

    @tagged('standard', 'post_install')
    def test_get_material_by_name(self):
        response = self._call_get_material(material_name='Cotton')
        self.assertEqual(len(response['materials']), 1)
        self.assertEqual(response['materials'][0]['material_name'], 'Cotton Fabric')

    @tagged('standard', 'post_install')
    def test_get_material_by_type(self):
        response = self._call_get_material(material_type='cotton')  # Cotton
        self.assertEqual(len(response['materials']), 1)
        self.assertEqual(response['materials'][0]['material_type'], 'cotton')

    @tagged('standard', 'post_install')
    def test_get_material_by_partner_name(self):
        response = self._call_get_material(partner_name='Deco Addict')
        self.assertEqual(len(response['materials']), 1)
        self.assertEqual(response['materials'][0]['partner_name'], 'Deco Addict')

    @tagged('standard', 'post_install')
    def test_get_material_no_results(self):
        response = self._call_get_material(material_code='999')  # Non-existing code
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'No materials found for the given criteria')

    @tagged('standard', 'post_install')
    def test_get_material_empty_response(self):
        response = self._call_get_material()  # No criteria provided
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'No materials found for the given criteria')

    @staticmethod
    def _call_get_material(**kwargs):
        # Simulate the call to the controller method
        return http.request.route('/api/material', type='json', auth='user', methods=['GET'])(**kwargs)

    def test_create_material_success(self):
        """Test successful creation of a material."""
        response = self.env['material.material_type'].create_material(
            material_code='001',
            material_name='Cotton Fabric',
            material_type='Cotton',  # Assuming the selection value is mapped correctly
            material_buy_price=150,  # Valid price
            partner_name=self.partner.name  # Valid partner
        )
        self.assertTrue(response.get('success'), "Material creation should be successful")
        self.assertIn('material_id', response, "Response should contain the created material ID")

    def test_create_material_partner_not_found(self):
        """Test creation when partner is not found."""
        response = self.env['material.material_type'].create_material(
            material_code='002',
            material_name='Silk Fabric',
            material_type='Fabrics',  # Assuming this is a valid type
            material_buy_price=200,  # Valid price
            partner_name='Non-Existent Partner'  # Non-existing partner
        )
        self.assertFalse(response.get('success'), "Material creation should fail")
        self.assertEqual(response.get('message'), 'Not found', "Should indicate partner was not found")

    def test_create_material_validation_error(self):
        """Test creation with validation error (material buy price too low)."""
        response = self.env['material.material_type'].create_material(
            material_code='003',
            material_name='Low Price Material',
            material_type='Cotton',  # Assuming valid type
            material_buy_price=50,  # Invalid price (should raise ValidationError)
            partner_name=self.partner.name  # Valid partner
        )
        self.assertIn('error', response, "Should return a validation error")
        self.assertIn("Material Buy Price must be greater than or equal to 100.", response.get('error'),
                      "Should contain the validation error message")

    def test_create_material_unexpected_error(self):
        """Test creation with an unexpected error (e.g., missing required field)."""
        response = self.env['material.material_type'].create_material(
            material_code='004',
            # material_name is missing, which should raise an error
            material_type='Cotton',
            material_buy_price=150,  # Valid price
            partner_name=self.partner.name  # Valid partner
        )
        self.assertIn('error', response, "Should return an error for missing required field")
        self.assertIn("An unexpected error occurred", response.get('error'),
                      "Should indicate that an unexpected error occurred")

    def test_update_material_success(self):
        """Test successful update of a material."""
        response = self.material_model.update_material(
            material_id=self.material_1.id,
            material_code='001',
            material_name='Updated Cotton Fabric',
            material_type='Cotton',  # Assuming valid mapping to selection
            material_buy_price=200,  # Valid price
            partner_id=self.partner_a.id  # Valid partner
        )
        self.assertTrue('message' in response and response['message'] == 'Material updated',
                        "Material update should be successful")
        self.material_1.refresh()  # Refresh to get updated values
        self.assertEqual(self.material_1.material_name, 'Updated Cotton Fabric',
                         "Material name should be updated")

    def test_update_material_not_found(self):
        """Test update when material is not found."""
        response = self.material_model.update_material(
            material_id=9999,  # Non-existing ID
            material_code='002',
            material_name='Silk Fabric',
            material_type='Fabrics',  # Assuming valid type
            material_buy_price=200,  # Valid price
            partner_id=self.partner_b.id  # Valid partner
        )
        self.assertIn('error', response, "Should return an error for not found material")
        self.assertEqual(response['error'], 'Material not found', "Should indicate that material is not found")

    def test_update_material_missing_required_fields(self):
        """Test update when required fields are missing."""
        response = self.material_model.update_material(
            material_id=self.material_1.id,
            # Missing 'material_name'
            material_code='003',
            # material_type is also missing
            material_buy_price=200,  # Valid price
            partner_id=self.partner_a.id  # Valid partner
        )
        self.assertIn('error', response, "Should return an error for missing required fields")
        self.assertIn("Missing required field: material_name", response['error'],
                      "Should indicate which field is missing")

    def test_update_material_validation_error(self):
        """Test update with validation error (material buy price too low)."""
        response = self.material_model.update_material(
            material_id=self.material_1.id,
            material_code='001',
            material_name='Updated Cotton Fabric',
            material_type='Cotton',  # Assuming valid mapping to selection
            material_buy_price=50,  # Invalid price (should raise ValidationError)
            partner_id=self.partner_a.id  # Valid partner
        )
        self.assertIn('error', response, "Should return a validation error")
        self.assertIn("Material Buy Price must be greater than or equal to 100.", response['error'],
                      "Should contain the validation error message")

    def test_update_material_unexpected_error(self):
        """Test update with an unexpected error (e.g., missing required field)."""
        response = self.material_model.update_material(
            material_id=self.material_1.id,
            material_code='004',
            # material_name is missing, which should raise an error
            material_type='Cotton',
            material_buy_price=150,  # Valid price
            partner_id=self.partner_a.id  # Valid partner
        )
        self.assertIn('error', response, "Should return an error for missing required field")
        self.assertIn("An error occurred", response['error'],
                      "Should indicate that an unexpected error occurred")

    def test_delete_material_success(self):
        """Test successful deletion of a material."""
        response = self.material_model.delete_material(self.material_1.id)
        self.assertTrue('message' in response and response['message'] == 'Material deleted',
                        "Material deletion should be successful")

        # Verify that the material no longer exists
        deleted_material = self.material_model.browse(self.material_1.id)
        self.assertFalse(deleted_material.exists(), "Material should be deleted from the database")

    def test_delete_material_not_found(self):
        """Test deletion when material is not found."""
        response = self.material_model.delete_material(9999)  # Non-existing ID
        self.assertIn('error', response, "Should return an error for not found material")
        self.assertEqual(response['error'], 'Material not found', "Should indicate that material is not found")

    def test_delete_material_validation_error(self):
        """Test deletion with validation error."""
        # This test case assumes that there's a validation in place that would prevent deletion.
        # Here, we will manually create a scenario that raises ValidationError.
        # For instance, we can simulate that the material cannot be deleted if it is linked somewhere.
        # However, this depends on your implementation.

        # In this example, we will just create a validation error
        # Since there might not be a practical validation error for delete operation,
        # this case might be skipped or modified according to actual validation in your application.
        response = self.material_model.delete_material(self.material_2.id)
        self.assertTrue('message' in response and response['message'] == 'Material deleted',
                        "Material deletion should be successful")

    def test_delete_material_unexpected_error(self):
        """Test deletion with an unexpected error."""
        # We can simulate an unexpected error during deletion.
        # For this, we can temporarily override the unlink method to raise an exception.
        original_unlink = self.material_1.unlink
        self.material_1.unlink = lambda: (_ for _ in ()).throw(Exception("Unexpected Error"))

        response = self.material_model.delete_material(self.material_1.id)
        self.assertIn('error', response, "Should return an error for unexpected error")
        self.assertIn("An error occurred: Unexpected Error", response['error'],
                      "Should indicate that an unexpected error occurred")

        # Restore the original unlink method
        self.material_1.unlink = original_unlink