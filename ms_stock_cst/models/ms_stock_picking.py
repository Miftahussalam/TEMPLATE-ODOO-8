from openerp import models, fields

class ms_stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def kosong(self):
        
        return True