from openerp.osv import orm, fields, osv

class ms_report_smove_xls(orm.TransientModel):
    _name = 'ms.report.smove.xls'
    _description = 'Report Stock Movement .xls'
    _rec_name = 'picking_type_code'
    
    _columns = {
        'picking_type_code': fields.selection([
            ('incoming_and_outgoing','Receipts and Delivery Orders'),
            ('incoming','Receipts'),
            ('outgoing','Delivery Orders'),
            ('internal','Internal Transfers')
        ], 'Picking Type'),
        'date_start_date': fields.date('Start Date'),
        'date_end_date': fields.date('End Date'),
        'min_date_start_date': fields.date('Start Date'),
        'min_date_end_date': fields.date('End Date'),
        'date_done_start_date': fields.date('Start Date'),
        'date_done_end_date': fields.date('End Date'),
        'partner_ids': fields.many2many('res.partner', 'ms_report_smove_partner_rel', 'ms_report_smove_xls_id',
            'partner_id', 'Partners'),
        'location_ids': fields.many2many('stock.location', 'ms_report_smove_location_rel', 'ms_report_smove_xls_id',
            'location_id', 'Source Locations'),
        'location_dest_ids': fields.many2many('stock.location', 'ms_report_smove_location_dest_rel', 'ms_report_smove_xls_id',
            'location_dest_id', 'Destination Locations'),
        'categ_ids': fields.many2many('product.category', 'ms_report_smove_category_rel', 'ms_report_smove_xls_id',
            'categ_id', 'Product Categories'),
        'product_ids': fields.many2many('product.product', 'ms_report_smove_product_rel', 'ms_report_smove_xls_id',
            'product_id', 'Products'),
    }
    
    def ms_report_smove_fields(self, cr, uid, context=None):
        return [
            'no',\
            'picking_type_name',\
            'picking_name',\
            'partner_name',\
            'prod_tmpl',\
            'qty',\
            'pick_date',\
            'pick_date_done',\
            'src_location',\
            'dest_location',\
            'origin',\
            'backorder',\
        ]
    
    def xls_export(self, cr, uid, ids, context=None):
        if context is None :
            context = {}
        datas = self.read(cr, uid, ids)[0]
        return {'type':'ir.actions.report.xml', 'report_name':'Report Stock Movement', 'datas':datas}
    
    def categ_ids_change(self, cr, uid, ids, ids_categ, context=None):
        value = {}
        if ids_categ :
            value['product_ids'] = False
        return {'value':value}
    