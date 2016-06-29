from openerp import fields, api, models, SUPERUSER_ID
from openerp.osv import osv

class ms_sale_order(models.Model):
    _inherit = 'sale.order'
    
    def _inv_get(self, cr, uid, order, context=None):
        res = super(ms_sale_order, self)._inv_get(cr, uid, order, context)
        res.update({
            'internal_number': self.pool.get('ir.sequence').get_sequence(cr, SUPERUSER_ID, 'CI'),
            'model_id': self.pool.get('ir.model').search(cr, uid, [('model','=',self.__class__.__name__)])[0],
            'transaction_id': order.id,
        })
        return res
    
    @api.model
    def create(self, vals):
        if not vals['order_line']:
            raise osv.except_osv(('Tidak bisa disimpan !'), ("Silahkan isi detil terlebih dahulu !"))
        vals['name'] = self.env['ir.sequence'].get_sequence('SO')
        return super(ms_sale_order, self).create(vals)
    
    @api.multi
    def write(self, vals, context=None):
        vals.get('order_line', []).sort(reverse=True)
        if 'order_line' in vals :
            detail_exist = False
            for line in vals['order_line']:
                if line[0] in [4,1,0] :
                    detail_exist = True
                    break
            if not detail_exist :
                raise osv.except_osv(('Tidak bisa disimpan !'), ("Silahkan isi detil terlebih dahulu !"))
        return super(ms_sale_order, self).write(vals)
    
    @api.multi
    def unlink(self):
        if self.state != 'draft' :
            raise osv.except_osv(('Invalid action !'), ('Tidak bisa dihapus jika state bukan Draft !'))
        return super(ms_sale_order, self).unlink()
    
class ms_sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    _sql_constraints = [
        ('unique_order_product', 'unique(order_id,product_id)', 'Tidak boleh ada produk yg sama dalam satu transaksi!'),
    ]
    