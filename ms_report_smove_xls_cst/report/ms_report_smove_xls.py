import xlwt
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from .ms_report_smove import ms_report_smove_print
from openerp.tools.translate import translate

class ms_report_smove_print_xls(ms_report_smove_print):

    def __init__(self, cr, uid, name, context):
        super(ms_report_smove_print_xls, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'wanted_list_overview': self.pool.get('ms.report.smove.xls').ms_report_smove_fields(cr, uid, context),
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, 'report.smove', 'report', lang, src) or src

class report_smove_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(report_smove_xls, self).__init__(name, table, rml, parser, header, store)
        
        # Cell Styles
        _xs = self.xls_styles
        """
        _xs = {'right': 'align: horz right;', 
        'left': 'align: horz left;', 
        'center': 'align: horz center;', 
        'bottom': 'align: vert bottom;', 
        'top': 'align: vert top;', 
        'bold': 'font: bold true;', 
        'italic': 'font: italic true;', 
        'underline': 'font: underline true;', 
        'fill': 'pattern: pattern solid, fore_color 26;',
        'fill_blue': 'pattern: pattern solid, fore_color 27;', 
        'fill_grey': 'pattern: pattern solid, fore_color 22;',
        'wrap': 'align: wrap true;', 
        'borders_all': 'borders: left thin, right thin, top thin, bottom thin, left_colour 22, right_colour 22, top_colour 22, bottom_colour 22;', 
        'xls_title': 'font: bold true, height 240;'}
        """
        
        header_total_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        
        # Format Nomor
        self.number_style = xlwt.easyxf(_xs['center'])
        
        # Format Kolom Header
        self.column_header_style = xlwt.easyxf(header_total_format)
        
        # Format Kolom Data
        column_data_format = _xs['borders_all']
        self.column_data_style = xlwt.easyxf(column_data_format)
        self.column_data_style_date = xlwt.easyxf(column_data_format + _xs['left'], num_format_str=report_xls.date_format)
        self.column_data_style_decimal = xlwt.easyxf(column_data_format + _xs['right'], num_format_str=report_xls.decimal_format)
        
        # Format Total
        self.total_style = xlwt.easyxf(header_total_format)
        self.total_style_decimal = xlwt.easyxf(header_total_format + _xs['right'], num_format_str=report_xls.decimal_format)
        
        # XLS Template
        self.col_specs_template_overview = {
            'no': {
                'header': [1, 5, 'text', _render("_('No')")],
                'lines': [1, 0, 'number', _render("p['no']"), None, self.number_style],
                'totals': [1, 5, 'number', None]},
            'picking_type_name': {
                'header': [1, 25, 'text', _render("_('Picking Type')")],
                'lines': [1, 0, 'text', _render("p['picking_type_name']")],
                'totals': [1, 25, 'number', None]},
            'picking_name': {
                'header': [1, 25, 'text', _render("_('Picking Number')")],
                'lines': [1, 0, 'text', _render("p['picking_name']")],
                'totals': [1, 25, 'number', None]},
            'partner_name': {
                'header': [1, 30, 'text', _render("_('Partner Name')")],
                'lines': [1, 0, 'text', _render("p['partner_name']")],
                'totals': [1, 30, 'number', None]},
            'prod_tmpl': {
                'header': [1, 30, 'text', _render("_('Product')")],
                'lines': [1, 0, 'text', _render("p['prod_tmpl']")],
                'totals': [1, 30, 'number', None]},
            'qty': {
                'header': [1, 15, 'text', _render("_('Quantity')")],
                'lines': [1, 0, 'number', _render("p['qty']"), None, self.column_data_style_decimal],
                'totals': [1, 15, 'number', None]},
            'pick_date': {
                'header': [1, 25, 'text', _render("_('Date')")],
                'lines': [1, 0, 'text', _render("p['pick_date']")],
                'totals': [1, 25, 'number', None]},
            'pick_date_done': {
                'header': [1, 25, 'text', _render("_('Date of Transfer')")],
                'lines': [1, 0, 'text', _render("p['pick_date_done']")],
                'totals': [1, 25, 'number', None]},
            'src_location': {
                'header': [1, 35, 'text', _render("_('Source Location')")],
                'lines': [1, 0, 'text', _render("p['src_location']")],
                'totals': [1, 35, 'number', None]},
            'dest_location': {
                'header': [1, 35, 'text', _render("_('Destination Location')")],
                'lines': [1, 0, 'text', _render("p['dest_location']")],
                'totals': [1, 35, 'number', None]},
            'origin': {
                'header': [1, 25, 'text', _render("_('Source Document')")],
                'lines': [1, 0, 'text', _render("p['origin']")],
                'totals': [1, 25, 'number', None]},
            'backorder': {
                'header': [1, 25, 'text', _render("_('Backorder')")],
                'lines': [1, 0, 'text', _render("p['backorder']")],
                'totals': [1, 25, 'number', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wanted_list_overview = _p.wanted_list_overview
        self.col_specs_template_overview.update({})
        _ = _p._
        
        for r in _p.reports:
            ws_o = wb.add_sheet('Sheet 1')
            
            for ws in [ws_o]:
                ws.panes_frozen = True
                ws.remove_splits = True
                ws.portrait = 0  # Landscape
                ws.fit_width_to_pages = 1
            row_pos_o = 0
            
            # Set print header/footer
            for ws in [ws_o]:
                ws.header_str = self.xls_headers['standard']
                ws.footer_str = self.xls_footers['standard']
                
            # Company Name
            cell_style = xlwt.easyxf(_xs['left'])
            row_data = self.xls_row_template([('report_name', 1, 0, 'text', _p.company.name)], ['report_name'])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=cell_style)
            
            # Title
            cell_style = xlwt.easyxf(_xs['xls_title'])
            row_data = self.xls_row_template([('report_name', 1, 0, 'text', 'Report Stock Movement')], ['report_name'])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=cell_style)
            
            # Start Date & End Date
            cell_style = xlwt.easyxf(_xs['left'])
            isi_tgl = 'Tanggal ' + ('-' if data['date_start_date'] == False else str(data['date_start_date'])) + ' s/d ' + ('-' if data['date_end_date'] == False else str(data['date_end_date']))
            row_data = self.xls_row_template([('report_name', 1, 0, 'text', isi_tgl)], ['report_name'])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=cell_style)
            row_pos_o += 1
            
            # Report Column Headers
            c_specs_o = map(lambda x: self.render(x, self.col_specs_template_overview, 'header', render_space={'_': _p._}), wanted_list_overview)
            row_data = self.xls_row_template(c_specs_o, [x[0] for x in c_specs_o])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=self.column_header_style, set_column_size=True)
            ws_o.set_horz_split_pos(row_pos_o)
            
            row_data_begin = row_pos_o
            
            # Columns and Rows
            no = 0
            for p in r['datas']:
                c_specs_o = map(lambda x: self.render(x, self.col_specs_template_overview, 'lines'), wanted_list_overview)
                for x in c_specs_o :
                    if x[0] == 'no' :
                        no += 1
                        x[4] = no
                row_data = self.xls_row_template(c_specs_o, [x[0] for x in c_specs_o])
                row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=self.column_data_style)
            
            row_data_end = row_pos_o
            
            # Totals
            ws_o.write(row_pos_o, 0, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 1, 'Totals', self.total_style)
            ws_o.write(row_pos_o, 2, None, self.total_style_decimal)
            ws_o.set_vert_split_pos(3)
            ws_o.write(row_pos_o, 3, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 4, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 5, xlwt.Formula("SUM(F"+str(row_data_begin)+":F"+str(row_data_end)+")"), self.total_style_decimal)   
            ws_o.write(row_pos_o, 6, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 7, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 8, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 9, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 10, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 11, None, self.total_style_decimal)
            
            # Footer
            ws_o.write(row_pos_o + 1, 0, None)
            ws_o.write(row_pos_o + 2, 0, _p.datetime + ' ' + _p.username)

report_smove_xls('report.Report Stock Movement', 'ms.report.smove.xls', parser=ms_report_smove_print_xls)