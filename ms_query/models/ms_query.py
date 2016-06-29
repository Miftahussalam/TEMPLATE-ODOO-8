from openerp import fields, api, models
from openerp.osv import osv

class ms_query(models.Model):
    _name = "ms.query"
    _description = "Query"
    
    backup = fields.Text('Backup Syntax')
    name = fields.Text('Syntax')
    result = fields.Text('Result')
    
#     @api.model
#     def create(self, vals):
#         raise osv.except_osv(('Perhatian !'), ("Tidak bisa disimpan, form ini hanya untuk Pengecekan"))
    
    def filter_change(self):
        if self.partner_id or self.product_id or self.uom_id :
            where_partner_id = "and 1=1 "
            if self.partner_id :
                where_partner_id = " and po.partner_id = %s" %self.partner_id.id
            where_product_id = " and 1=1 "
            if self.product_id :
                where_product_id = " and pol.product_id = %s" %self.product_id.id
            where_uom_id = " and 1=1 "
            if self.uom_id :
                where_uom_id = " and pol.product_uom = %s" %self.uom_id.id
            self._cr.execute("""select po.date_order, po.partner_id, pol.product_id, pol.product_uom, pol.price_unit
                from purchase_order po
                left join purchase_order_line pol on pol.order_id = po.id
                left join res_partner rp on rp.id = po.partner_id
                left join product_product pp on pp.id = pol.product_id
                left join product_uom pu on pu.id = pol.product_uom
                where po.state not in ('draft','sent','cancel') """ + where_partner_id + where_product_id + where_uom_id +
                """ order by rp.name, pp.name_template, pu.name limit 5""")
            
            history_line = []
            for res in self._cr.fetchall() :
                vals = {
                    'date': res[0],
                    'partner_id': res[1],
                    'product_id': res[2],
                    'uom_id': res[3],
                    'unit_price': res[4],
                }
                history_line.append(vals)
            self.history_line = history_line
        else :
            self.history_line = False
            
    @api.multi
    def execute_query(self):
        self._cr.execute(self.name)
        try :
            self.result = self._cr.fetchall()
        except Exception :
            self.result = 'berhasil'
        