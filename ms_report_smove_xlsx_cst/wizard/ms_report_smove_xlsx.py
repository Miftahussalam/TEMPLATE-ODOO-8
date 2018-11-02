import xlsxwriter
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ms_report_smove_xlsx(osv.osv_memory):
    _name = "ms.report.smove.xlsx"
    _description = "Report Stock Movement .xlsx"
    
    wbf = {}
    
    def _get_default(self, cr, uid, date=False, context=None):
        if date :
            return self.pool.get('res.company').get_default_date_model(cr, uid, context)
        else :
            return self.pool.get('res.users').browse(cr, uid, uid)
    
    _columns = {
        'state_x': fields.selection((('choose','choose'),('get','get'))), #xls
        'data_x': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 100, readonly=True),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'picking_type_code': fields.selection([
            ('incoming_and_outgoing','Receipts and Delivery Orders'),
            ('incoming','Receipts'),
            ('outgoing','Delivery Orders'),
            ('internal','Internal Transfers')
        ], 'Picking Type'),
        'partner_ids': fields.many2many('res.partner', 'ms_report_smove_partner_rel', 'ms_report_smove_xlsx_id',
            'partner_id', 'Partners'),
        'product_ids': fields.many2many('product.product', 'ms_report_smove_product_rel', 'ms_report_smove_xlsx_id',
            'product_id', 'Products'),
        'categ_ids': fields.many2many('product.category', 'ms_report_smove_categ_rel', 'ms_report_smove_xlsx_id',
            'categ_id', 'Categories'),
        'location_ids': fields.many2many('stock.location', 'ms_report_smove_location_rel', 'ms_report_smove_xlsx_id',
            'location_id', 'Locations'),
        'location_dest_ids': fields.many2many('stock.location', 'ms_report_smove_location_dest_rel', 'ms_report_smove_xlsx_id',
            'location_dest_id', 'Destination Locations'),
    }
    
    _defaults = {
        'state_x': lambda*a : 'choose',
    }
    
    def add_workbook_format(self, cr, uid, workbook):
        self.wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        self.wbf['header'].set_border()
        
        self.wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        self.wbf['header_no'].set_border()
        self.wbf['header_no'].set_align('vcenter')
                
        self.wbf['footer'] = workbook.add_format({'align':'left'})
        
        self.wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self.wbf['content_datetime'].set_left()
        self.wbf['content_datetime'].set_right()
        
        self.wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        self.wbf['content_date'].set_left()
        self.wbf['content_date'].set_right() 
        
        self.wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        self.wbf['title_doc'].set_font_size(12)
        
        self.wbf['company'] = workbook.add_format({'align': 'left'})
        self.wbf['company'].set_font_size(11)
        
        self.wbf['content'] = workbook.add_format()
        self.wbf['content'].set_left()
        self.wbf['content'].set_right() 
        
        self.wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        self.wbf['content_float'].set_right() 
        self.wbf['content_float'].set_left()

        self.wbf['content_number'] = workbook.add_format({'align': 'right'})
        self.wbf['content_number'].set_right() 
        self.wbf['content_number'].set_left() 
        
        self.wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        self.wbf['content_percent'].set_right() 
        self.wbf['content_percent'].set_left() 
                
        self.wbf['total_float'] = workbook.add_format({'bold':1, 'bg_color':'#FFFFDB', 'align':'right', 'num_format':'#,##0.00'})
        self.wbf['total_float'].set_top()
        self.wbf['total_float'].set_bottom()            
        self.wbf['total_float'].set_left()
        self.wbf['total_float'].set_right()         
        
        self.wbf['total_number'] = workbook.add_format({'align':'right','bg_color': '#FFFFDB','bold':1})
        self.wbf['total_number'].set_top()
        self.wbf['total_number'].set_bottom()            
        self.wbf['total_number'].set_left()
        self.wbf['total_number'].set_right()
        
        self.wbf['total'] = workbook.add_format({'bold':1,'bg_color': '#FFFFDB','align':'center'})
        self.wbf['total'].set_left()
        self.wbf['total'].set_right()
        self.wbf['total'].set_top()
        self.wbf['total'].set_bottom()
        
        self.wbf['header_detail_space'] = workbook.add_format({})
        self.wbf['header_detail_space'].set_left()
        self.wbf['header_detail_space'].set_right()
        self.wbf['header_detail_space'].set_top()
        self.wbf['header_detail_space'].set_bottom()
        
        self.wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2'})
        self.wbf['header_detail'].set_left()
        self.wbf['header_detail'].set_right()
        self.wbf['header_detail'].set_top()
        self.wbf['header_detail'].set_bottom()
                        
        return workbook
        
    def excel_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids,context=context)[0]
        return self._print_excel_report(cr, uid, ids, data, context=context)
        
    def _print_excel_report(self, cr, uid, ids, data, context=None):
        picking_type_code = data['picking_type_code']
        start_date = data['start_date']
        end_date = data['end_date']
        partner_ids = data['partner_ids']
        product_ids = data['product_ids']
        categ_ids = data['categ_ids']
        location_ids = data['location_ids']
        location_dest_ids = data['location_dest_ids']
        
        where_picking_type_code = " 1=1 "
        if picking_type_code :
            if picking_type_code == 'incoming_and_outgoing' :
                where_picking_type_code = " spt.code in ('incoming','outgoing')"
            else :
                where_picking_type_code = " spt.code = '%s'" %picking_type_code
        where_start_date = " 1=1 "
        if start_date :
            where_start_date = " spick.date >= '%s'" % str(start_date)
        where_end_date = " 1=1 "
        if end_date :
            where_end_date = " spick.date <= '%s'" % str(end_date + " 23:59:59")
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
        
        get_datetime = self._get_default(cr, uid, date=True, context=context)
        datetime = get_datetime.strftime("%Y-%m-%d %H:%M:%S")
        date = get_datetime.strftime("%Y-%m-%d")
        user_id = self._get_default(cr, uid)
        company_name = self._get_default(cr, uid, context=context).company_id.name
        filename = ('Report Stock Movement ') + str(date) + '.xlsx'
        
        timezone = user_id.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'
        
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
        
        where = " where smove.state = 'done' and " + where_picking_type_code + " AND " + where_start_date + " AND " + where_end_date + " AND " + where_partner_ids + " AND " + where_location_ids + " AND " + where_location_dest_ids + " AND " + where_categ_ids + " AND " + where_product_ids
        group_by = " group by picking_type_name, picking_name, partner_name, prod_categ, prod_tmpl, pick_date, pick_date_done, src_location, dest_location, spick.origin, backorder"
        order = " order by picking_type_name, picking_name"
        
        cr.execute(query_smove + where + group_by + order, (tz,tz,))
        result = cr.fetchall()
        
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)        
        workbook = self.add_workbook_format(cr, uid, workbook)
        wbf = self.wbf
        
        #WKS 1
        worksheet = workbook.add_worksheet('Stock Move')
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:C1', 20)
        worksheet.set_column('D1:D1', 20)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 20)
        worksheet.set_column('I1:I1', 30)
        worksheet.set_column('J1:J1', 30)
        worksheet.set_column('K1:K1', 20)
        worksheet.set_column('L1:L1', 20)
        
        #WKS 1
        worksheet.write('A1', company_name , wbf['company'])
        worksheet.write('A2', 'Report Stock Movement' , wbf['title_doc'])
        worksheet.write('A3', 'Tanggal ' + ('-' if start_date == False else str(start_date)) + ' s/d ' + ('-' if end_date == False else end_date))
        
        row=5
        
        worksheet.write('A%s' %(row), 'No' , wbf['header'])
        worksheet.write('B%s' %(row), 'Picking Type' , wbf['header'])
        worksheet.write('C%s' %(row), 'Picking Number' , wbf['header'])
        worksheet.write('D%s' %(row), 'Partner Name' , wbf['header'])
        worksheet.write('E%s' %(row), 'Product' , wbf['header'])
        worksheet.write('F%s' %(row), 'Quantity' , wbf['header'])
        worksheet.write('G%s' %(row), 'Date' , wbf['header'])
        worksheet.write('H%s' %(row), 'Date of Transfer' , wbf['header'])
        worksheet.write('I%s' %(row), 'Source Location' , wbf['header'])
        worksheet.write('J%s' %(row), 'Destination Location' , wbf['header'])
        worksheet.write('K%s' %(row), 'Source Document' , wbf['header'])
        worksheet.write('L%s' %(row), 'Backorder' , wbf['header'])
        
        row+=1
        no = 0
        tot_qty = 0
        row1 = row
        
        for res in result:
            picking_type = res[0] if res[0] else ''
            picking_name = res[1] if res[1] else ''
            partner_name = res[2] if res[2] else ''
            prod_categ = res[3] if res[3] else ''
            product_name = res[4] if res[4] else ''
            qty = res[5] if res[5] else 0
            date = res[6] if res[6] else ''
            date_done = res[7] if res[7] else ''
            src_location = res[8] if res[8] else ''
            dest_location = res[9] if res[9] else ''
            origin = res[10] if res[10] else ''
            backorder = res[11] if res[11] else ''
            
            no += 1
            tot_qty += qty
            
            worksheet.write('A%s' %row, no , wbf['content'])
            worksheet.write('B%s' %row, picking_type , wbf['content'])                    
            worksheet.write('C%s' %row, picking_name , wbf['content'])
            worksheet.write('D%s' %row, partner_name , wbf['content'])  
            worksheet.write('E%s' %row, product_name , wbf['content'])
            worksheet.write('F%s' %row, qty , wbf['content_float'])
            worksheet.write('G%s' %row, date , wbf['content'])
            worksheet.write('H%s' %row, date_done , wbf['content'])
            worksheet.write('I%s' %row, src_location , wbf['content'])
            worksheet.write('J%s' %row, dest_location , wbf['content'])
            worksheet.write('K%s' %row, origin , wbf['content'])
            worksheet.write('L%s' %row, backorder , wbf['content'])
            
            row+=1
        
        worksheet.merge_range('A%s:B%s' % (row,row), 'Total', wbf['total'])
        worksheet.write('C%s' %row, '' , wbf['total_float'])
        worksheet.write('D%s' %row, '' , wbf['total_float'])
        worksheet.write('E%s' %row, '' , wbf['total_float'])
        worksheet.write_formula(row-1,5, '{=subtotal(9,F%s:F%s)}' % (row1, row-1), wbf['total_float'], tot_qty)
        worksheet.write('G%s' %row, '' , wbf['total_float'])
        worksheet.write('H%s' %row, '' , wbf['total_float'])
        worksheet.write('I%s' %row, '' , wbf['total_float'])
        worksheet.write('J%s' %row, '' , wbf['total_float'])
        worksheet.write('K%s' %row, '' , wbf['total_float'])
        worksheet.write('L%s' %row, '' , wbf['total_float'])
        worksheet.write('A%s'%(row+2), '%s %s' % (str(datetime), user_id.name) , wbf['footer'])
        
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name':filename}, context=context)
        fp.close()
        
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'ms_report_smove_xlsx_cst', 'view_report_smove_xlsx')
        
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download .xlsx'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ms.report.smove.xlsx',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def categ_ids_change(self, cr, uid, ids, ids_categ, context=None):
        value = {}
        if ids_categ :
            value['product_ids'] = False
        return {'value':value}
        
ms_report_smove_xlsx()