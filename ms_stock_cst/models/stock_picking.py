from openerp import models, fields, api

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def kosong(self):
        
        return True