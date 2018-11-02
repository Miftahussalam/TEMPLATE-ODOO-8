from openerp import fields, api, models
from openerp.osv import osv

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    model_id = fields.Many2one('ir.model', string='Model')
    transaction_id = fields.Integer('Transaction ID')
    
    @api.multi
    def unlink(self):
        if self.state != 'draft' :
            raise osv.except_osv(('Invalid action !'), ('Tidak bisa dihapus jika state bukan Draft !'))
        return super(account_invoice, self).unlink()
    
class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    _sql_constraints = [
        ('unique_invoice_product', 'unique(invoice_id,product_id)', 'Tidak boleh ada produk yg sama dalam satu transaksi!'),
    ]
    