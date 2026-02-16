from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_serial_no = fields.Boolean(string="MO Serial No")
    supplier_name = fields.Many2one('res.partner',string="Supplier Name")
    material_type = fields.Char(string="Material Type")
    type_reference = fields.Char(string="Type")
    film_description = fields.Text(string="Film Description")
    treatment_in = fields.Char(string="Treatment In")
    treatment_out = fields.Char(string="Treatment Out")
    product_reference_code = fields.Char(string="Product Code")



class ProductProduct(models.Model):
    _inherit = "product.product"

    mo_serial_no = fields.Boolean(string="MO Serial No")

    supplier_name = fields.Many2one('res.partner',string="Supplier Name")
    film_description = fields.Text(string="Film Description")
    material_type = fields.Char(string="Material Type")
    type_reference = fields.Char(string="Type")
    treatment_in = fields.Char(string="Treatment In")
    treatment_out = fields.Char(string="Treatment Out")