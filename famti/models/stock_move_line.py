from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    film = fields.Char(string="Film")
    category = fields.Char(string="Film Category", tracking=True, help="This helps to categorise specific product.")
    film_type = fields.Char(string="Film Type", tracking=True, help="Film Type")
    lot_number = fields.Char(string="Lot Number", tracking=True, help="Lot Number")
    pallet_no = fields.Char(string="Pallet Number", tracking=True, help="Pallet Number")

    weight = fields.Float(string="Weight (kg)", tracking=True)
    lot_id = fields.Many2one('stock.lot',string='Serial Numbers')
    lot_name = fields.Char(string="Serial Number Name")

    weight_uom = fields.Selection(selection=[
        ('kg', 'Kg'),
        ('lbs', 'Lbs'),
        ('gm', 'Gm'),
    ], required=True, default='kg', string=" ")
    thickness = fields.Float(string="Thickness (micron)", tracking=True)
    thickness_uom = fields.Selection(selection=[('guage', 'Guage'), ('micron', 'Micron')], default='micron', string=" ",
                                     tracking=True)
    width = fields.Float(string="Width", help="This helps to categorise specific product.")
    width_uom = fields.Selection(selection=[('mm', 'MM'), ('inch', 'Inch')], default='mm', string=" ", tracking=True)
    core_id = fields.Selection(selection=[('3', '3 Inch'), ('6', '6 Inch')], string="Core", tracking=True)
    length = fields.Float(string="Length", tracking=True, help="Product Length")
    length_uom = fields.Selection(selection=[('m', 'M'), ('feet', 'Feet')], default='feet', string=" ", tracking=True)
    grade_type = fields.Selection([('a', 'A Grade'),('b', 'B Grade'),],string="Grade")
    mo_product_code =fields.Char(string="MO Product Code")

    def _action_done(self):
        res = super()._action_done()
        for line in self:
            if line.lot_id:
                previous_code= line.product_id.default_code
                line.lot_id.film = line.film
                line.lot_id.category = line.category
                line.lot_id.film_type = line.film_type
                line.lot_id.thickness = line.thickness
                line.lot_id.thickness_uom = line.thickness_uom
                line.lot_id.weight = line.weight
                line.lot_id.width_uom = line.width_uom
                line.lot_id.core_selection_id = line.core_id
                line.lot_id.lot_number = line.lot_number
                line.lot_id.pallet_no = line.pallet_no
                line.lot_id.width_val = line.width
                line.lot_id.width_uom = line.width_uom
                line.lot_id.length_val = line.length
                line.lot_id.length_uom = line.length_uom
                line.lot_id.grade_type = line.grade_type
        return res

    @api.onchange('lot_name')
    def _onchange_lot_name_check_duplicate(self):
        if self.lot_name:
            existing_lot = self.env['stock.lot'].search([
                ('name', '=', self.lot_name),
            ], limit=1)

            if existing_lot:
                raise ValidationError(
                    _("Serial Number '%s' already exists for the product '%s'. "
                    "Please check the product serial number.")
                    % (self.lot_name, self.product_id.display_name)
                )

class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_id = fields.Many2one(
        'stock.lot',
        string="Lot",
        domain="[('product_id', '=', product_id)]"
    )

    source_mo_id = fields.Many2one(
        'mrp.production',
        string="Source MO",
        compute="_compute_source_mo",
        store=True
    )

    @api.depends('lot_id')
    def _compute_source_mo(self):
        for move in self:
            print("------move",move.id)
            print("------lot_id",move.lot_id)
            mo = False
            if move.lot_id:
                move_line = self.env['stock.move.line'].search([
                    ('lot_id', '=', move.lot_id.id),
                    ('move_id.production_id', '!=', False)
                ], limit=1, order="id desc")

                mo = move_line.move_id.production_id if move_line else False

            move.source_mo_id = mo


    # @api.onchange('product_id')
    # def _onchange_product_id_set_lot_domain(self):
    #     if self.product_id:
    #         print("========",self.product_id.lot_ids)
    #         return {
    #             'domain': {
    #                 'lot_id': [
    #                     ('product_id', '=', self.product_id.id),
    #                     ('quantity', '>', 0)
    #                 ]
    #             }
    #         }
