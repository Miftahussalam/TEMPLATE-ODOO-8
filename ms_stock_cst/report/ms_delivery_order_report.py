import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class wtc_delivery_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(wtc_delivery_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'no_urut': self.no_urut,
            'inv_number': self.get_inv_number,
            'remark': self.get_remark,
            'sales_code': self.sales_code,
        })
        self.no = 0
        
    def no_urut(self):
        self.no += 1
        return self.no
        
    def get_inv_number(self):
        picking_id = self.pool.get('stock.picking').browse(self.cr, self.uid, self.ids)
        obj_so = self.pool.get('sale.order')
        id_so = obj_so.search(self.cr, self.uid, [('procurement_group_id','=',picking_id.group_id.id)])
        so_id = obj_so.browse(self.cr, self.uid, id_so)
        inv_number = []
        for invoice_id in so_id.invoice_ids :
            if invoice_id.type != 'out_refund' :
                inv_number.append(str(invoice_id.number) or str(invoice_id.internal_number))
        if len(inv_number) == 1 :
            inv_number = inv_number[0]
        return inv_number
    
    def get_remark(self):
        picking_id = self.pool.get('stock.picking').browse(self.cr, self.uid, self.ids)
        obj_so = self.pool.get('sale.order')
        id_so = obj_so.search(self.cr, self.uid, [('procurement_group_id','=',picking_id.group_id.id)])
        so_id = obj_so.browse(self.cr, self.uid, id_so)
        return so_id.note
    
    def sales_code(self):
        picking_id = self.pool.get('stock.picking').browse(self.cr, self.uid, self.ids)
        ids_section_line = self.pool.get('crm.case.section.line').search(self.cr, self.uid, [('user_id','=',picking_id.sales_person_id.id)])
        if ids_section_line :
            section_line_ids = self.pool.get('crm.case.section.line').browse(self.cr, self.uid, ids_section_line[0])
            return section_line_ids.code
        return ""
        
report_sxw.report_sxw('report.wtc.do.report', 'stock.picking', 'addons/wtc_stock_hnc/report/wtc_delivery_order_report.rml', parser=wtc_delivery_order, header=False)