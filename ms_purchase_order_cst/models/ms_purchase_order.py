from openerp import fields, api, models, SUPERUSER_ID
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from lxml import etree

class ms_purchase_order(models.Model):
    _inherit = 'purchase.order'

    # def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    #     if not context :
    #         context = {}
    #     res = super(ms_purchase_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    #     company_ids = self.pool.get('res.users').browse(cr, uid, uid).company_ids
    #     ids_company = [c.id for c in company_ids]
    #     doc = etree.XML(res['arch'])
    #     nodes_company = doc.xpath("//field[@name='company_id']")
    #     for node in nodes_company :
    #         node.set('domain', '[("id", "in", '+str(ids_company)+')]')
    #     res['arch'] = etree.tostring(doc)
    #     return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ms_purchase_order, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        company_ids = self.env['res.users'].browse(self._uid).company_ids
        ids_company = [c.id for c in company_ids]
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='company_id']"):
            node.set('domain', '[("id", "in", '+str(ids_company)+')]')
        res['arch'] = etree.tostring(doc)
        return res

    test_digits = fields.Float('Test Digits', digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    
    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        res = super(ms_purchase_order, self)._prepare_invoice(cr, uid, order, line_ids, context)
        res.update({
            'model_id': self.pool.get('ir.model').search(cr, uid, [('model','=',self.__class__.__name__)])[0],
            'transaction_id': order.id,
            'internal_number': self.pool.get('ir.sequence').get_sequence(cr, SUPERUSER_ID, 'SI')
        })
        return res
    
    @api.model
    def create(self, vals, context=None):
        if not vals['order_line']:
            raise osv.except_osv(('Tidak bisa disimpan !'), ("Silahkan isi detil terlebih dahulu !"))
        vals['name'] = self.env['ir.sequence'].sudo().get_sequence('PO')
        return super(ms_purchase_order, self).create(vals)
    
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
        return super(ms_purchase_order, self).write(vals)
    
    @api.multi
    def unlink(self):
        if self.state != 'draft' :
            raise osv.except_osv(('Invalid action !'), ('Tidak bisa dihapus jika state bukan Draft !'))
        return super(ms_purchase_order, self).unlink()
    
class ms_purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    _sql_constraints = [
        ('unique_order_product', 'unique(order_id,product_id)', 'Tidak boleh ada produk yg sama dalam satu transaksi!'),
    ]
    