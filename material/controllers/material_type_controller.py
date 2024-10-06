from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class MaterialController(http.Controller):
    # @http.route('/api/material', type='json', auth='none', methods=['GET'])
    # def get_all_materials(self):
    #     materials = request.env['material.material_type'].search([])
    #     return {
    #         'status': 'success',
    #         'data': [{
    #             'material_code': m.material_code,
    #             'material_name': m.material_name,
    #             'material_type': m.material_type,
    #             'material_buy_price': m.material_buy_price,
    #             'partner_id': m.partner_id.id if m.partner_id else None,
    #         } for m in materials]
    #     }

    @http.route('/api/material', type='json', auth='user', methods=['GET'])
    def get_material(self, **kwargs):
        domain = []

        # Extract and build domain from query parameters
        if 'material_code' in kwargs:
            domain.append(('material_code', '=', kwargs['material_code']))
        if 'material_name' in kwargs:
            domain.append(('material_name', 'ilike', kwargs['material_name']))  # Case-insensitive search
        if 'material_type' in kwargs:
            domain.append(('material_type', '=', kwargs['material_type']))
        if 'partner_name' in kwargs:
            domain.append(('partner_id.name', 'ilike', kwargs['partner_name']))
        # Search for materials based on the constructed domain
        print("domain: %s" % domain)
        materials = request.env['material.material_type'].search(domain)
        print("materials: %s" % materials)
        if not materials:
            return {'error': 'No materials found for the given criteria'}

        # Prepare the response
        result = []
        for material in materials:
            result.append({
                'id': material.id,
                'material_code': material.material_code,
                'material_name': material.material_name,
                'material_type': material.material_type,
                'material_buy_price': material.material_buy_price,
                'partner_id': material.partner_id.id if material.partner_id else None,
                'partner_name': material.partner_id.name if material.partner_id else None
            })

        return {'materials': result}

    @http.route('/api/material', type='json', auth='user', methods=['POST'])
    def create_material(self, **kwargs):
        print("create_material %s" % kwargs)
        # Retrieve the partner name from the request
        partner_name = kwargs.get('partner_name')

        # Initialize partner_id to None
        partner_id = None

        # Get the material_type description from the request
        material_type_description = kwargs.get('material_type')

        material_type_value = request.env['material.material_type'].get_material_type_value(material_type_description)
        print('material_type_value %s ' % material_type_value)

        if partner_name and material_type_value:
            # Search for partners matching the provided name
            partners = request.env['res.partner'].search([('name', 'ilike', partner_name)])
            print("partners %s " % partners)
            # If more than one partner is found, take the first one
            if partners:
                partner_id = partners[0].id  # Get the first partner's ID
                print("partner_id %s " % partner_id)
                try:
                    # Prepare material data for creation
                    material_data = {
                        'material_code': kwargs.get('material_code'),
                        'material_name': kwargs.get('material_name'),
                        'material_type': material_type_value,
                        'material_buy_price': kwargs.get('material_buy_price'),
                        'partner_id': partner_id,
                    }
                    print("material data bfr insert: %s " % material_data)
                    new_material = request.env['material.material_type'].create(material_data)
                    print("new_material aft insert: %s " % new_material)
                    return {
                        'success': True,
                        'material_id': new_material.id,
                        'message': 'Material created successfully'
                    }
                except ValidationError as e:
                    print('ValidationError')
                    request.env.cr.rollback()
                    return {'error': str(e)}
                except Exception as e:
                    request.env.cr.rollback()
                    return {'error': f'An unexpected error occurred: {str(e)}'}
            else:
                return {
                    'success': False,
                    'partner': partners,
                    'message': 'Not found'
                }

    @http.route('/api/material', type='json', auth='user', methods=['PUT'])
    def update_material(self, **kwargs):
        material_id = None
        if 'material_id' in kwargs:
            material_id = kwargs.get('material_id'),
        material = request.env['material.material_type'].browse(material_id)

        if not material.exists():
            return {'error': 'Material not found'}
        required_fields = ['material_code', 'material_name', 'material_type', 'material_buy_price', 'partner_id']
        for field in required_fields:
            if field not in kwargs:
                return {'error': f'Missing required field: {field}'}

        try:
            material_data = {
                'id': kwargs.get('material_id'),
                'material_code': kwargs.get('material_code'),
                'material_name': kwargs.get('material_name'),
                'material_type': kwargs.get('material_type'),
                'material_buy_price': kwargs.get('material_buy_price'),
                'partner_id': kwargs.get('partner_id'),
            }
            material.write(material_data)
            return {'message': 'Material updated', 'material_id': material.id}
        except ValidationError as e:
            request.env.cr.rollback()
            return {'error': str(e)}
        except Exception as e:
            request.env.cr.rollback()
            return {'error': f'An error occurred: {str(e)}'}

    @http.route('/api/material/<int:material_id>', type='json', auth='user', methods=['DELETE'])
    def delete_material(self, material_id):
        try:
            # Fetch the material record
            material = request.env['material.material_type'].browse(material_id)
            # Check if the material exists
            if not material.exists():
                return {'error': 'Material not found'}
            # Delete the material
            material.unlink()
            return {'message': 'Material deleted'}

        except ValidationError as e:
            # Handle validation errors if any
            return {'error': str(e)}

        except Exception as e:
            # Handle any other exceptions that may occur
            return {'error': f'An error occurred: {str(e)}'}