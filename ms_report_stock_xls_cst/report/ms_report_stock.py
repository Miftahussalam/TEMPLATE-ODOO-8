from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm

class ms_report_stock_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(ms_report_stock_print, self).__init__(cr, uid, name, context=context)
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        product_ids = data['product_ids']
        categ_ids = data['categ_ids']
        location_ids = data['location_ids']
        
        datetime = self.pool.get('res.company').get_default_date(self.cr, self.uid, self.context).strftime('%Y-%m-%d %H:%M:%S')
        user_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        timezone = user_id.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'
        
        if categ_ids :
            product_ids = self.pool.get('product.product').search(self.cr, self.uid, [('categ_id','in',categ_ids)])
        where_product_ids = " 1=1 "
        where_product_ids2 = " 1=1 "
        if product_ids :
            where_product_ids = " quant.product_id in %s" % str(tuple(product_ids)).replace(',)', ')')
            where_product_ids2 = " product_id in %s" % str(tuple(product_ids)).replace(',)', ')')
        ids_location = self.pool.get('stock.location').search(self.cr, self.uid, [('usage','=','internal')])
        where_location_ids = " quant.location_id in %s" % str(tuple(ids_location)).replace(',)', ')')
        where_location_ids2 = " location_id in %s" % str(tuple(ids_location)).replace(',)', ')')
        if location_ids :
            where_location_ids = " quant.location_id in %s" % str(tuple(location_ids)).replace(',)', ')')
            where_location_ids2 = " location_id in %s" % str(tuple(location_ids)).replace(',)', ')')
        
        query = """
            select prod.name_template as product, categ.name as prod_categ, loc.complete_name as location,
            quant.in_date + interval %s as tgl_masuk, date_part('days', now() - (quant.in_date + interval %s)) as aging, sum(quant.qty) as total_product, sum(quant2.qty) as stock, sum(quant3.qty) as reserved
            from stock_quant quant
            left join (select * from stock_quant where """ + where_product_ids2 + " AND " + where_location_ids2 + """ and reservation_id is null) quant2 on quant2.id = quant.id
            left join (select * from stock_quant where """ + where_product_ids2 + " AND " + where_location_ids2 + """ and reservation_id is not null) quant3 on quant3.id = quant.id
            left join stock_location loc on loc.id=quant.location_id
            left join product_product prod on prod.id=quant.product_id
            left join product_template prod_tmpl on prod_tmpl.id=prod.product_tmpl_id
            left join product_category categ on categ.id=prod_tmpl.categ_id
        """
        
        where = " WHERE" + where_product_ids + " AND " + where_location_ids
        group_by = " group by product, prod_categ, location, tgl_masuk"
        order = " order by tgl_masuk"
        
        self.cr.execute(query + where + group_by + order, (tz,tz,))
        all_lines = self.cr.dictfetchall()
        
        if all_lines :
            datas = map(lambda x : {
                'no': 0,
                'product': str(x['product'].encode('ascii','ignore').decode('ascii')) if x['product'] != None else '',
                'prod_categ': str(x['prod_categ'].encode('ascii','ignore').decode('ascii')) if x['prod_categ'] != None else '',
                'location': str(x['location'].encode('ascii','ignore').decode('ascii')) if x['location'] != None else '',
                'tgl_masuk': str(x['tgl_masuk'].encode('ascii','ignore').decode('ascii')) if x['tgl_masuk'] != None else '',
                'aging': x['aging'],
                'total_product': x['total_product'],
                'stock': x['stock'],
                'reserved': x['reserved'],
            }, all_lines)
            reports = filter(lambda x: datas, [{'datas': datas}])
        else :
            reports = [{'datas': [{
                'no': 0,
                'product': 'NO DATA FOUND',
                'prod_categ': 'NO DATA FOUND',
                'location': 'NO DATA FOUND',
                'tgl_masuk': 'NO DATA FOUND',
                'aging': 0,
                'total_product': 0,
                'stock': 0,
                'reserved': 0,
            }]}]
        
        self.localcontext.update({
            'reports': reports,
            'datetime': datetime,
            'username': user_id.name,
        })
        super(ms_report_stock_print, self).set_context(objects, data, ids, report_type)
        
class wrapped_vat_declaration_print(orm.AbstractModel):
    _name = 'report.ms_report_stock.report_stock'
    _inherit = 'report.abstract_report'
    _template = 'ms_report_stock.report_stock'
    _wrapped_report_class = ms_report_stock_print
    