import xlsxwriter
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ms_report_hutang_xlsx(osv.osv_memory):
    _name = "ms.report.hutang.xlsx"
    _description = "Report Hutang XLSX"
    
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
        'status': fields.selection([
            ('outstanding', 'Outstanding'),
            ('reconciled', 'Reconciled')
        ], 'Status', default='outstanding'),
        'partner_ids': fields.many2many('res.partner', 'ms_report_hutang_supplier_rel', 'ms_report_hutang_xlsx_id',
                                        'supplier_id', 'Supplier', copy=False, domain=[('supplier','=',True)]),
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
        start_date = data['start_date']
        end_date = data['end_date']
        status = data['status']
        partner_ids = data['partner_ids']
        
        query_where = ' 1=1 '
        if start_date :
            query_where +=" AND aml.date >= '%s'" % str(start_date)
        if end_date :
            query_where +=" AND aml.date <= '%s'" % str(end_date)
        if partner_ids :
            query_where +=" AND aml.partner_id in %s" % str(
                tuple(partner_ids)).replace(',)', ')')
        if status == 'outstanding' :
            query_where +=" AND aml.reconcile_id is null"
        elif status == 'reconciled' :
            query_where +=" AND aml.reconcile_id is not null"
        
        get_datetime = self._get_default(cr, uid, date=True, context=context)
        datetime = get_datetime.strftime("%Y-%m-%d %H:%M:%S")
        date = get_datetime.strftime("%Y-%m-%d")
        user_id = self._get_default(cr, uid)
        company_name = self._get_default(cr, uid, context=context).company_id.name
        filename = ('Report Hutang ') + str(date) + '.xlsx'
        
        timezone = user_id.tz or 'Asia/Jakarta'
        if timezone == 'Asia/Jayapura' :
            tz = '9 hours'
        elif timezone == 'Asia/Pontianak' :
            tz = '8 hours'
        else :
            tz = '7 hours'
        
        query = """
            select rp.name, ai.number, aml.date, aml.date_maturity, aml.credit - aml.debit as total_piutang,
            case when aml.reconcile_partial_id is not null then aml3.credit - aml3.debit
            when aml.reconcile_id is not null then 0
                else aml.credit - aml.debit
                end as amount_residual,
            current_date - aml.date_maturity as overdue,
            case when aml.reconcile_id is not null then 'Reconciled' else 'Outstanding'
            end as status
            from account_move_line aml
            left join (select aml2.reconcile_partial_id, sum(aml2.debit) as debit, sum(aml2.credit) as credit from account_move_line aml2 WHERE aml2.reconcile_partial_id is not null GROUP BY aml2.reconcile_partial_id) aml3 on aml.reconcile_partial_id = aml3.reconcile_partial_id
            left join account_invoice ai on ai.move_id = aml.move_id
            left join res_partner rp on rp.id = aml.partner_id
            left join account_account a on a.id = aml.account_id
            where ai.type = 'in_invoice' and a.type = 'payable' and %s
            order by rp.name
        """ % (query_where)
        
        cr.execute(query)
        result = cr.fetchall()
        
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)        
        workbook = self.add_workbook_format(cr, uid, workbook)
        wbf = self.wbf
        
        #WKS 1
        worksheet = workbook.add_worksheet('Hutang')
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 30)
        worksheet.set_column('C1:C1', 20)
        worksheet.set_column('D1:D1', 20)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 20)
        worksheet.set_column('I1:I1', 20)
        worksheet.set_column('J1:J1', 20)
        worksheet.set_column('K1:K1', 20)
        worksheet.set_column('L1:L1', 20)
        worksheet.set_column('M1:M1', 20)
        
        #WKS 1
        worksheet.write('A1', company_name , wbf['company'])
        worksheet.write('A2', 'Report Hutang' , wbf['title_doc'])
        worksheet.write('A3', 'Tanggal ' + ('-' if start_date == False else str(start_date)) + ' s/d ' + ('-' if end_date == False else end_date))
        
        row=5
        
        worksheet.write('A%s' %(row), 'No' , wbf['header'])
        worksheet.write('B%s' %(row), 'Supplier' , wbf['header'])
        worksheet.write('C%s' %(row), 'Invoice Number' , wbf['header'])
        worksheet.write('D%s' %(row), 'Date' , wbf['header'])
        worksheet.write('E%s' %(row), 'Due Date' , wbf['header'])
        worksheet.write('F%s' %(row), 'Total Hutang' , wbf['header'])
        worksheet.write('G%s' %(row), 'Sisa Hutang' , wbf['header'])
        worksheet.write('H%s' %(row), 'Not Due' , wbf['header'])
        worksheet.write('I%s' %(row), 'Overdue 1-30' , wbf['header'])
        worksheet.write('J%s' %(row), 'Overdue 31-60' , wbf['header'])
        worksheet.write('K%s' %(row), 'Overdue 61-90' , wbf['header'])
        worksheet.write('L%s' %(row), 'Overdue +90' , wbf['header'])
        worksheet.write('M%s' %(row), 'Status' , wbf['header'])
        
        row+=1
        no = 0
        grand_tot_hutang = 0
        tot_residual = 0
        tot_not_due = 0
        tot_overdue_1_30 = 0
        tot_overdue_31_60 = 0
        tot_overdue_61_90 = 0
        tot_overdue_lebih_90 = 0
        row1 = row
        
        for res in result:
            supp = res[0] if res[0] else ''
            inv_number = res[1] if res[1] else ''
            date = res[2] if res[2] else ''
            due_date = res[3] if res[3] else ''
            tot_hutang = res[4] if res[4] else 0
            residual = abs(res[5]) if res[5] else 0
            not_due = residual if res[6] <= 0 else 0
            overdue_1_30 = residual if res[6] >= 1 and res[6] <= 30 else 0
            overdue_31_60 = residual if res[6] >= 31 and res[6] <= 60 else 0
            overdue_61_90 = residual if res[6] >= 61 and res[6] <= 90 else 0
            overdue_lebih_90 = residual if res[6] > 90 else 0
            status = res[7] if res[7] else ''
            
            no += 1
            grand_tot_hutang += tot_hutang
            tot_residual += residual
            tot_not_due += not_due
            tot_overdue_1_30 += overdue_1_30
            tot_overdue_31_60 += overdue_31_60
            tot_overdue_61_90 += overdue_61_90
            tot_overdue_lebih_90 += overdue_lebih_90
            
            worksheet.write('A%s' %row, no , wbf['content'])
            worksheet.write('B%s' %row, supp , wbf['content'])                    
            worksheet.write('C%s' %row, inv_number , wbf['content'])
            worksheet.write('D%s' %row, date , wbf['content'])  
            worksheet.write('E%s' %row, due_date , wbf['content'])
            worksheet.write('F%s' %row, tot_hutang , wbf['content_float'])
            worksheet.write('G%s' %row, residual , wbf['content_float'])
            worksheet.write('H%s' %row, not_due , wbf['content_float'])
            worksheet.write('I%s' %row, overdue_1_30 , wbf['content_float'])
            worksheet.write('J%s' %row, overdue_31_60 , wbf['content_float'])
            worksheet.write('K%s' %row, overdue_61_90 , wbf['content_float'])
            worksheet.write('L%s' %row, overdue_lebih_90 , wbf['content_float'])
            worksheet.write('M%s' %row, status , wbf['content'])
            
            row+=1
        
        worksheet.merge_range('A%s:B%s' % (row,row), 'Grand Total', wbf['total'])
        worksheet.write('C%s' %row, '' , wbf['total_float'])
        worksheet.write('D%s' %row, '' , wbf['total_float'])
        worksheet.write('E%s' %row, '' , wbf['total_float'])
        worksheet.write_formula(row-1,5, '{=subtotal(9,F%s:F%s)}' % (row1, row-1), wbf['total_float'], grand_tot_hutang)
        worksheet.write_formula(row-1,6, '{=subtotal(9,G%s:G%s)}' % (row1, row-1), wbf['total_float'], tot_residual)
        worksheet.write_formula(row-1,7, '{=subtotal(9,H%s:H%s)}' % (row1, row-1), wbf['total_float'], tot_not_due)
        worksheet.write_formula(row-1,8, '{=subtotal(9,I%s:I%s)}' % (row1, row-1), wbf['total_float'], tot_overdue_1_30)
        worksheet.write_formula(row-1,9, '{=subtotal(9,J%s:J%s)}' % (row1, row-1), wbf['total_float'], tot_overdue_31_60)
        worksheet.write_formula(row-1,10, '{=subtotal(9,K%s:K%s)}' % (row1, row-1), wbf['total_float'], tot_overdue_61_90)
        worksheet.write_formula(row-1,11, '{=subtotal(9,L%s:L%s)}' % (row1, row-1), wbf['total_float'], tot_overdue_lebih_90)
        worksheet.write('M%s' %row, '' , wbf['total_float'])
        worksheet.write('A%s'%(row+2), '%s %s' % (str(datetime), user_id.name) , wbf['footer'])
        
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name':filename}, context=context)
        fp.close()
        
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'ms_report_hutang_xlsx_cst', 'view_report_hutang_xlsx')
        
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLSX'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ms.report.hutang.xlsx',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        
ms_report_hutang_xlsx()