from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    film = fields.Char(string="Film")
    category = fields.Char(string="Film Category", tracking=True, help="This helps to categorise specific product.")
    film_type = fields.Char(string="Film Type", tracking=True, help="Film Type")
    lot_number = fields.Char(string="Lot Number", tracking=True, help="Lot Number")
    pallet_no = fields.Char(string="Pallet Number", tracking=True, help="Pallet Number")

    weight = fields.Float(string="Weight (kg)", tracking=True)
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

    def _action_done(self):
        res = super()._action_done()
        for line in self:
            if line.lot_id:
                line.lot_id.film = line.film
                line.lot_id.category = line.category
                line.lot_id.film_type = line.film_type
                line.lot_id.thickness = line.thickness
                line.lot_id.weight = line.weight
                line.lot_id.core_id = line.core_id
                line.lot_id.lot_number = line.lot_number
                line.lot_id.pallet_no = line.pallet_no
        return res