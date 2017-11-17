import xlsxwriter
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ms_report_stock_xlsx(osv.osv_memory):
    _name = "ms.report.stock.xlsx"
    _description = "Report Stock .xlsx"
    
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
        'product_ids': fields.many2many('product.product', 'ms_report_stock_product_rel', 'ms_report_stock_xlsx_id',
            'product_id', 'Products'),
        'categ_ids': fields.many2many('product.category', 'ms_report_stock_categ_rel', 'ms_report_stock_xlsx_id',
            'categ_id', 'Categories'),
        'location_ids': fields.many2many('stock.location', 'ms_report_stock_location_rel', 'ms_report_stock_xlsx_id',
            'location_id', 'Locations'),
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
        product_ids = data['product_ids']
        categ_ids = data['categ_ids']
        location_ids = data['location_ids']
        
        if categ_ids :
            product_ids = self.pool.get('product.product').search(cr, uid, [('categ_id','in',categ_ids)])
        where_product_ids = " 1=1 "
        where_product_ids2 = " 1=1 "
        if product_ids :
            where_product_ids = " quant.product_id in %s" % str(tuple(product_ids)).replace(',)', ')')
            where_product_ids2 = " product_id in %s" % str(tuple(product_ids)).replace(',)', ')')
        ids_location = self.pool.get('stock.location').search(cr, uid, [('usage','=','internal')])
        where_location_ids = " quant.location_id in %s" % str(tuple(ids_location)).replace(',)', ')')
        where_location_ids2 = " location_id in %s" % str(tuple(ids_location)).replace(',)', ')')
        if location_ids :
            where_location_ids = " quant.location_id in %s" % str(tuple(location_ids)).replace(',)', ')')
            where_location_ids2 = " location_id in %s" % str(tuple(location_ids)).replace(',)', ')')
        
        get_datetime = self._get_default(cr, uid, date=True, context=context)
        datetime = get_datetime.strftime("%Y-%m-%d %H:%M:%S")
        date = get_datetime.strftime("%Y-%m-%d")
        user_id = self._get_default(cr, uid)
        company_name = self._get_default(cr, uid, context=context).company_id.name
        filename = ('Report Stock ') + str(date) + '.xlsx'
        
        timezone = user_id.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'
        
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
        
        cr.execute(query + where + group_by + order, (tz,tz,))
        result = cr.fetchall()
        
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)        
        workbook = self.add_workbook_format(cr, uid, workbook)
        wbf = self.wbf
        
        #WKS 1
        worksheet = workbook.add_worksheet('Stock')
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 30)
        worksheet.set_column('C1:C1', 20)
        worksheet.set_column('D1:D1', 30)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 20)
        worksheet.set_column('I1:I1', 20)
        
        #WKS 1
        worksheet.write('A1', company_name , wbf['company'])
        worksheet.write('A2', 'Report Stock' , wbf['title_doc'])
        worksheet.write('A3', 'Per Tanggal %s'%datetime)
        
        row=5
        
        worksheet.write('A%s' %(row), 'No' , wbf['header'])
        worksheet.write('B%s' %(row), 'Product' , wbf['header'])
        worksheet.write('C%s' %(row), 'Product Category' , wbf['header'])
        worksheet.write('D%s' %(row), 'Location' , wbf['header'])
        worksheet.write('E%s' %(row), 'Incoming Date' , wbf['header'])
        worksheet.write('F%s' %(row), 'Stock Age' , wbf['header'])
        worksheet.write('G%s' %(row), 'Total Product' , wbf['header'])
        worksheet.write('H%s' %(row), 'Stock' , wbf['header'])
        worksheet.write('I%s' %(row), 'Reserved' , wbf['header'])
        
        row+=1
        no = 0
        tot_product = 0
        tot_stock = 0
        tot_reserve = 0
        row1 = row
        
        for res in result:
            prod = res[0] if res[0] else ''
            prod_categ = res[1] if res[1] else ''
            location = res[2] if res[2] else ''
            incoming_date = res[3] if res[3] else ''
            stock_age = res[4] if res[4] else 0
            qty = res[5] if res[5] else 0
            stock_qty = res[6] if res[6] else 0
            reserve_qty = res[7] if res[7] else 0
            
            no += 1
            tot_product += qty
            tot_stock += stock_qty
            tot_reserve += reserve_qty
            
            worksheet.write('A%s' %row, no , wbf['content'])
            worksheet.write('B%s' %row, prod , wbf['content'])                    
            worksheet.write('C%s' %row, prod_categ , wbf['content'])
            worksheet.write('D%s' %row, location , wbf['content'])  
            worksheet.write('E%s' %row, incoming_date , wbf['content'])
            worksheet.write('F%s' %row, stock_age , wbf['content_float'])
            worksheet.write('G%s' %row, qty , wbf['content_float'])
            worksheet.write('H%s' %row, stock_qty , wbf['content_float'])
            worksheet.write('I%s' %row, reserve_qty , wbf['content_float'])
            
            row+=1
        
        worksheet.merge_range('A%s:B%s' % (row,row), 'Grand Total', wbf['total'])
        worksheet.write('C%s' %row, '' , wbf['total_float'])
        worksheet.write('D%s' %row, '' , wbf['total_float'])
        worksheet.write('E%s' %row, '' , wbf['total_float'])
        worksheet.write('F%s' %row, '' , wbf['total_float'])
        worksheet.write_formula(row-1,6, '{=subtotal(9,G%s:G%s)}' % (row1, row-1), wbf['total_float'], tot_product)
        worksheet.write_formula(row-1,7, '{=subtotal(9,H%s:H%s)}' % (row1, row-1), wbf['total_float'], tot_stock)
        worksheet.write_formula(row-1,8, '{=subtotal(9,I%s:I%s)}' % (row1, row-1), wbf['total_float'], tot_reserve)
        worksheet.write('A%s'%(row+2), '%s %s' % (str(datetime), user_id.name) , wbf['footer'])
        
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name':filename}, context=context)
        fp.close()
        
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'ms_report_stock_xlsx_cst', 'view_report_stock_xlsx')
        
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download .xlsx'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ms.report.stock.xlsx',
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
        
ms_report_stock_xlsx()