from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    film = fields.Char(string="Film")
    category = fields.Char(string="Film Category", tracking=True, help="This helps to categorise specific product.")
    film_type = fields.Char(string="Film Type", tracking=True, help="Film Type")
    thickness = fields.Float(string="Thickness (micron)", tracking=True)
    weight = fields.Float(string="Weight (kg)", tracking=True)
    core_id = fields.Char(string="Core Id", tracking=True)

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
        return res