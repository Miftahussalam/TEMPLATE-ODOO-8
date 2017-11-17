import xlsxwriter
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ms_report_sale_xlsx(osv.osv_memory):
    _name = "ms.report.sale.xlsx"
    _description = "Sale Report .xlsx"
    
    wbf = {}
    
    def _get_default(self, cr, uid, date=False, context=None):
        if date :
            return self.pool.get('res.company').get_default_date_model(cr, uid, context)
        else :
            return self.pool.get('res.users').browse(cr, uid, uid)
    
    _columns = {
        'state_x': fields.selection( ( ('choose','choose'),('get','get'))), #xls
        'data_x': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 100, readonly=True),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('progress', 'Sales Order'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Status'),
        'partner_ids': fields.many2many('res.partner', 'ms_report_sale_partner_rel', 'ms_report_sale_xlsx_id',
                                        'partner_id', 'Customer', domain=[('customer','=',True)]),
        'product_ids': fields.many2many('product.product', 'ms_report_sale_product_rel', 'ms_report_sale_xlsx_id',
                                        'product_id', 'Product'),
        'sale_order_ids': fields.many2many('sale.order', 'ms_report_sale_sale_order_rel', 'ms_report_sale_xlsx_id',
                                        'sale_id', 'Sale Order'),
    }
    
    _defaults = {
        'state_x': lambda*a : 'choose',
        'end_date' : datetime.now(),
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
        partner_ids = data['partner_ids']
        sale_order_ids = data['sale_order_ids']
        product_ids = data['product_ids']
        start_date = data['start_date']
        end_date = data['end_date']
        state = data['state']
        
        query_where = ' 1=1 '
        if start_date :
            query_where +=" AND so.date_order >= '%s'" % str(start_date + ' 00:00:00')
        if end_date :
            query_where +=" AND so.date_order <= '%s'" % str(end_date + ' 23:59:59')
        if partner_ids :
            query_where +=" AND so.partner_id in %s" % str(
                tuple(partner_ids)).replace(',)', ')')
        if sale_order_ids :
            query_where +=" AND so.id in %s" % str(
                tuple(sale_order_ids)).replace(',)', ')')
        if product_ids :
            query_where +=" AND pp.id in %s" % str(
                tuple(product_ids)).replace(',)', ')') 
        if state :
            query_where +=" AND so.state = '%s'" % str(state)
        
        query = """
            select so.name as so_number, so.date_order as so_date,
            rp.name as customer, pp.name_template as prod_name,
            sol.product_uom_qty as qty, sol.price_unit,
            sol.product_uom_qty * sol.price_unit as subtotal
            from sale_order so
            left join sale_order_line sol on sol.order_id = so.id
            left join product_product pp on pp.id = sol.product_id
            left join res_partner rp on rp.id = so.partner_id
            where %s
            order by so_number
        """ % (query_where)
        
        cr.execute(query)
        result = cr.fetchall()
        
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)        
        workbook = self.add_workbook_format(cr, uid, workbook)
        wbf = self.wbf
        
        #WKS 1
        worksheet = workbook.add_worksheet('Sale')
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:C1', 20)
        worksheet.set_column('D1:D1', 20)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 20)
        
        get_datetime = self._get_default(cr, uid, date=True, context=context)
        datetime = get_datetime.strftime("%Y-%m-%d %H:%M:%S")
        date = get_datetime.strftime("%Y-%m-%d")
        user = self._get_default(cr, uid)
        company_name = self._get_default(cr, uid, context=context).company_id.name
        filename = ('Sale Report ') + str(date) + '.xlsx'
        
        #WKS 1
        worksheet.write('A1', company_name , wbf['company'])
        worksheet.write('A2', 'Sale Report' , wbf['title_doc'])
        worksheet.write('A3', 'Tanggal ' + ('-' if start_date == False else str(start_date)) + ' s/d ' + ('-' if end_date == False else end_date))
        
        row=5
        
        worksheet.write('A%s' %(row), 'No' , wbf['header'])
        worksheet.write('B%s' %(row), 'Sale Number' , wbf['header'])
        worksheet.write('C%s' %(row), 'Sale Date' , wbf['header'])
        worksheet.write('D%s' %(row), 'Customer' , wbf['header'])        
        worksheet.write('E%s' %(row), 'Product Name' , wbf['header'])
        worksheet.write('F%s' %(row), 'Quantity' , wbf['header'])
        worksheet.write('G%s' %(row), 'Price Unit' , wbf['header'])
        worksheet.write('H%s' %(row), 'Subtotal' , wbf['header'])
        
        row+=1
        no = 0
        qty_total = 0
        total = 0
        row1 = row
        
        for res in result:
            so_name = res[0] if res[0] else ''
            so_date = res[1] if res[1] else ''
            customer = res[2] if res[2] else ''
            prod_name = res[3] if res[3] else ''
            qty = res[4] if res[4] else ''
            price_unit = res[5] if res[5] else ''
            subtotal = res[6] if res[6] else ''
            
            no += 1
            qty_total += qty
            total += subtotal
                                     
            worksheet.write('A%s' %row, no , wbf['content'])
            worksheet.write('B%s' %row, so_name , wbf['content'])                    
            worksheet.write('C%s' %row, so_date , wbf['content'])
            worksheet.write('D%s' %row, customer , wbf['content'])  
            worksheet.write('E%s' %row, prod_name , wbf['content'])
            worksheet.write('F%s' %row, qty , wbf['content_float'])
            worksheet.write('G%s' %row, price_unit , wbf['content_float'])
            worksheet.write('H%s' %row, subtotal , wbf['content_float'])
            
            row+=1
        
        worksheet.merge_range('A%s:B%s' % (row,row), 'Total', wbf['total'])
        worksheet.write('C%s' %row, '' , wbf['total_float'])
        worksheet.write('D%s' %row, '' , wbf['total_float'])
        worksheet.write('E%s' %row, '' , wbf['total_float'])
        worksheet.write_formula(row-1,5, '{=subtotal(9,F%s:F%s)}' % (row1, row-1), wbf['total_float'], qty_total)
        worksheet.write('G%s' %row, '' , wbf['total_float'])
        worksheet.write_formula(row-1,7, '{=subtotal(9,H%s:H%s)}' % (row1, row-1), wbf['total_float'], total)
        worksheet.write('A%s'%(row+2), '%s %s' % (str(datetime), user.name) , wbf['footer'])
        
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name':filename}, context=context)
        fp.close()
        
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'ms_report_sale_xlsx_cst', 'view_report_sale_xlsx')
        
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download .xlsx'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ms.report.sale.xlsx',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        
ms_report_sale_xlsx()