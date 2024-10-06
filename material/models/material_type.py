from odoo import fields, models, api
from odoo.exceptions import ValidationError


class MaterialType(models.Model):
    _name = 'material.material_type'
    _description = 'Material Type'

    material_code = fields.Char(string='Material Code',
                                help="Material Code.",
                                required=True)
    material_name = fields.Char(string='Material Name',
                                help="Material Name.",
                                required=True)
    material_type = fields.Selection(
            [
                ('cotton', 'Cotton'),
                ('fabrics', 'Fabrics'),
                ('jeans', 'Jeans'),
            ],
            string="Material Type",
            default='cotton',
            required=True
        )
    material_buy_price = fields.Float(
        string='Material Buy Price',
        help="Harga beli material.",
        required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        # domain="[('supplier_rank', '>', 0)]",
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
        required=True
    )

    @api.constrains('material_buy_price')
    def _check_material_buy_price(self):
        print('check material buy price')
        for record in self:
            if record.material_buy_price < 100:
                print('check material buy price error')
                raise ValidationError("Material Buy Price must be greater than or equal to 100.")

    @api.model
    def get_material_type_value(self, description):
        print('get_material_type_value')
        # Fetch the selection values from the model
        material_type_field = self.fields_get(allfields=['material_type'])
        print('material_type_field %s' % material_type_field)
        material_type_selection = material_type_field['material_type']['selection']
        print('material_type_selection %s' % material_type_selection)
        # Create a dynamic map from the selection values
        material_type_map = {desc: value for value, desc in material_type_selection}
        print('material_type_map %s ' % material_type_map)

        # Return the mapped selection value for the description
        return material_type_map.get(description)