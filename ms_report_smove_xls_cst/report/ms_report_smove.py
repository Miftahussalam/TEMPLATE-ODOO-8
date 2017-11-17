from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm

class ms_report_smove_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(ms_report_smove_print, self).__init__(cr, uid, name, context=context)
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        picking_type_code = data['picking_type_code']
        date_start_date = data['date_start_date']
        date_end_date = data['date_end_date']
        min_date_start_date = data['min_date_start_date']
        min_date_end_date = data['min_date_end_date']
        date_done_start_date = data['date_done_start_date']
        date_done_end_date = data['date_done_end_date']
        partner_ids = data['partner_ids']
        location_ids = data['location_ids']
        location_dest_ids = data['location_dest_ids']
        categ_ids = data['categ_ids']
        product_ids = data['product_ids']
        
        datetime = self.pool.get('res.company').get_default_date(self.cr, self.uid, self.context).strftime('%Y-%m-%d %H:%M:%S')
        user_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        timezone = user_id.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'
        
        where_picking_type_code = " 1=1 "
        if picking_type_code :
            if picking_type_code == 'incoming_and_outgoing' :
                where_picking_type_code = " spt.code in ('incoming','outgoing')"
            else :
                where_picking_type_code = " spt.code = '%s'" %picking_type_code
        where_date_start_date = " 1=1 "
        if date_start_date :
            where_date_start_date = " spick.date >= '%s'" % str(date_start_date)
        where_date_end_date = " 1=1 "
        if date_end_date :
            where_date_end_date = " spick.date <= '%s'" % str(date_end_date + " 23:59:59")
        where_min_date_start_date = " 1=1 "
        if min_date_start_date :
            where_min_date_start_date = " spick.min_date >= '%s'" % str(min_date_start_date)
        where_min_date_end_date = " 1=1 "
        if min_date_end_date :
            where_min_date_end_date = " spick.min_date <= '%s'" % str(min_date_end_date + " 23:59:59")
        where_date_done_start_date = " 1=1 "
        if date_done_start_date :
            where_date_done_start_date = " spick.date_done >= '%s'" % str(date_done_start_date)
        where_date_done_end_date = " 1=1 "
        if date_done_end_date :
            where_date_done_end_date = " spick.date_done <= '%s'" % str(date_done_end_date + " 23:59:59")
        where_partner_ids = " 1=1 "
        if partner_ids :
            where_partner_ids = " smove.partner_id in %s" % str(tuple(partner_ids)).replace(',)', ')')
        where_location_ids = " 1=1 "
        if location_ids :
            where_location_ids = " smove.location_id in %s" % str(tuple(location_ids)).replace(',)', ')')
        where_location_dest_ids = " 1=1 "
        if location_dest_ids :
            where_location_dest_ids = " smove.location_dest_id in %s" % str(tuple(location_dest_ids)).replace(',)', ')')
        where_categ_ids = " 1=1 "
        if categ_ids :
            where_categ_ids = " categ.id in %s" % str(tuple(categ_ids)).replace(',)', ')')
        where_product_ids = " 1=1 "
        if product_ids :
            where_product_ids = " smove.product_id in %s" % str(tuple(product_ids)).replace(',)', ')')
        
        query_smove = """
            select spt.name as picking_type_name, spick.name as picking_name,
            partner.name as partner_name, categ.name as prod_categ,
            prod.name_template as prod_tmpl, sum(smove.product_uom_qty) as qty,
            spick.date + interval %s as pick_date, spick.date_done + interval %s as pick_date_done,
            src_loc.complete_name as src_location, dest_loc.complete_name as dest_location,
            spick.origin, backorder.name as backorder
            from stock_move smove
            left join stock_picking spick on spick.id = smove.picking_id
            left join stock_picking backorder on backorder.id = spick.backorder_id
            left join stock_picking_type spt on spt.id = spick.picking_type_id
            left join stock_location src_loc on src_loc.id = smove.location_id
            left join stock_location dest_loc on dest_loc.id = smove.location_dest_id
            left join res_partner partner on partner.id = spick.partner_id
            left join product_product prod on prod.id = smove.product_id
            left join product_template prod_tmpl on prod_tmpl.id = prod.product_tmpl_id
            left join product_category categ on categ.id = prod_tmpl.categ_id
        """
        
        where = " where smove.state = 'done' and " + where_picking_type_code + " AND " + where_date_start_date + " AND " + where_date_end_date + " AND " + where_min_date_start_date + " AND " + where_min_date_end_date + " AND " + where_date_done_start_date + " AND " + where_date_done_end_date + " AND " + where_partner_ids + " AND " + where_location_ids + " AND " + where_location_dest_ids + " AND " + where_categ_ids + " AND " + where_product_ids
        group_by = " group by picking_type_name, picking_name, partner_name, prod_categ, prod_tmpl, pick_date, pick_date_done, src_location, dest_location, spick.origin, backorder"
        order = " order by picking_type_name"
        
        self.cr.execute(query_smove + where + group_by + order, (tz,tz,))
        all_lines = self.cr.dictfetchall()
        
        if all_lines :
            datas = map(lambda x : {
                'no': 0,
                'picking_type_name': str(x['picking_type_name'].encode('ascii','ignore').decode('ascii')) if x['picking_type_name'] != None else '',
                'picking_name': str(x['picking_name'].encode('ascii','ignore').decode('ascii')) if x['picking_name'] != None else '',
                'partner_name': str(x['partner_name'].encode('ascii','ignore').decode('ascii')) if x['partner_name'] != None else '',
                'prod_tmpl': str(x['prod_tmpl'].encode('ascii','ignore').decode('ascii')) if x['prod_tmpl'] != None else '',
                'qty': x['qty'],
                'pick_date': str(x['pick_date'].encode('ascii','ignore').decode('ascii')) if x['pick_date'] != None else '',
                'pick_date_done': str(x['pick_date_done'].encode('ascii','ignore').decode('ascii')) if x['pick_date_done'] != None else '',
                'src_location': str(x['src_location'].encode('ascii','ignore').decode('ascii')) if x['src_location'] != None else '',
                'dest_location': str(x['dest_location'].encode('ascii','ignore').decode('ascii')) if x['dest_location'] != None else '',
                'origin': str(x['origin'].encode('ascii','ignore').decode('ascii')) if x['origin'] != None else '',
                'backorder': str(x['backorder'].encode('ascii','ignore').decode('ascii')) if x['backorder'] != None else '',
            }, all_lines)
            reports = filter(lambda x: datas, [{'datas': datas}])
        else :
            reports = [{'datas': [{
                'no': 0,
                'picking_type_name': 'NO DATA FOUND',
                'picking_name': 'NO DATA FOUND',
                'partner_name': 'NO DATA FOUND',
                'prod_tmpl': 'NO DATA FOUND',
                'qty': 0,
                'pick_date': 'NO DATA FOUND',
                'pick_date_done': 'NO DATA FOUND',
                'src_location': 'NO DATA FOUND',
                'dest_location': 'NO DATA FOUND',
                'origin': 'NO DATA FOUND',
                'backorder': 'NO DATA FOUND',
            }]}]
        
        self.localcontext.update({
            'reports': reports,
            'datetime': datetime,
            'username': user_id.name,
        })
        super(ms_report_smove_print, self).set_context(objects, data, ids, report_type)
        
class wrapped_vat_declaration_print(orm.AbstractModel):
    _name = 'report.ms_report_smove.report_smove'
    _inherit = 'report.abstract_report'
    _template = 'ms_report_smove.report_smove'
    _wrapped_report_class = ms_report_smove_print
    