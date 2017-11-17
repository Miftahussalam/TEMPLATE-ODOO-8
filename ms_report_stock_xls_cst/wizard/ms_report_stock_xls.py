from openerp.osv import orm, fields, osv

class ms_report_stock_xls(orm.TransientModel):
    _name = 'ms.report.stock.xls'
    _description = 'Report Stock .xls'
    
    def get_default_date(self, cr, uid, context=None):
        return self.pool.get('res.company').get_default_date(cr, uid, context)
    
    _columns = {
        'product_ids': fields.many2many('product.product', 'ms_report_stock_product_rel', 'ms_report_stock_xls_id',
            'product_id', 'Products'),
        'categ_ids': fields.many2many('product.category', 'ms_report_stock_categ_rel', 'ms_report_stock_xls_id',
            'categ_id', 'Categories'),
        'location_ids': fields.many2many('stock.location', 'ms_report_stock_location_rel', 'ms_report_stock_xls_id',
            'location_id', 'Locations'),
    }
    
    def ms_report_stock_fields(self, cr, uid, context=None):
        return [
            'no',\
            'product',\
            'prod_categ',\
            'location',\
            'tgl_masuk',\
            'aging',\
            'total_product',\
            'stock',\
            'reserved',\
        ]
    
    def xls_export(self, cr, uid, ids, context=None):
        if context is None :
            context = {}
        datas = self.read(cr, uid, ids)[0]
        return {'type':'ir.actions.report.xml', 'report_name':'Report Stock', 'datas':datas}
    
    def categ_ids_change(self, cr, uid, ids, ids_categ, context=None):
        value = {}
        if ids_categ :
            value['product_ids'] = False
        return {'value':value}
    