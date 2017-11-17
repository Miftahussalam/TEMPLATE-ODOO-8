import xlwt
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from .ms_report_stock import ms_report_stock_print
from openerp.tools.translate import translate

class ms_report_stock_print_xls(ms_report_stock_print):
    
    def __init__(self, cr, uid, name, context):
        super(ms_report_stock_print_xls, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'wanted_list_overview': self.pool.get('ms.report.stock.xls').ms_report_stock_fields(cr, uid, context),
            '_': self._,
        })
    
    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, 'report.stock', 'report', lang, src) or src
    
class report_stock_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(report_stock_xls, self).__init__(name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        
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
            'product': {
                'header': [1, 35, 'text', _render("_('Product')")],
                'lines': [1, 0, 'text', _render("p['product']")],
                'totals': [1, 35, 'number', None]},
            'prod_categ': {
                'header': [1, 22, 'text', _render("_('Product Category')")],
                'lines': [1, 0, 'text', _render("p['prod_categ']")],
                'totals': [1, 22, 'number', None]},
            'location': {
                'header': [1, 40, 'text', _render("_('Location')")],
                'lines': [1, 0, 'text', _render("p['location']")],
                'totals': [1, 40, 'number', None]},
            'tgl_masuk': {
                'header': [1, 22, 'text', _render("_('Incoming Date')")],
                'lines': [1, 0, 'text', _render("p['tgl_masuk']")],
                'totals': [1, 22, 'number', None]},
            'aging': {
                'header': [1, 22, 'text', _render("_('Stock Age')")],
                'lines': [1, 0, 'number', _render("p['aging']"), None, self.column_data_style_decimal],
                'totals': [1, 22, 'number', None]},
            'total_product': {
                'header': [1, 22, 'text', _render("_('Total Product')")],
                'lines': [1, 0, 'number', _render("p['total_product']"), None, self.column_data_style_decimal],
                'totals': [1, 22, 'number', None]},
            'stock': {
                'header': [1, 22, 'text', _render("_('Stock')")],
                'lines': [1, 0, 'number', _render("p['stock']"), None, self.column_data_style_decimal],
                'totals': [1, 22, 'number', None]},
            'reserved': {
                'header': [1, 22, 'text', _render("_('Reserved')")],
                'lines': [1, 0, 'number', _render("p['reserved']"), None, self.column_data_style_decimal],
                'totals': [1, 22, 'number', None]},
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

            # set print header/footer
            for ws in [ws_o]:
                ws.header_str = self.xls_headers['standard']
                ws.footer_str = self.xls_footers['standard']

            # Company Name
            cell_style = xlwt.easyxf(_xs['left'])
            row_data = self.xls_row_template([('report_name', 1, 0, 'text', _p.company.name)], ['report_name'])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=cell_style)
            
            # Title
            cell_style = xlwt.easyxf(_xs['xls_title'])
            row_data = self.xls_row_template([('report_name', 1, 0, 'text', 'Report Stock')], ['report_name'])
            row_pos_o = self.xls_write_row(ws_o, row_pos_o, row_data, row_style=cell_style)
            
            # Start Date & End Date
            cell_style = xlwt.easyxf(_xs['left'])
            isi_tgl = 'Per Tanggal ' + _p.datetime
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
            ws_o.write(row_pos_o, 1, "Total", self.total_style)
            ws_o.write(row_pos_o, 2, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 3, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 4, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 5, None, self.total_style_decimal)
            ws_o.write(row_pos_o, 6, xlwt.Formula("SUM(G"+str(row_data_begin)+":G"+str(row_data_end)+")"), self.total_style_decimal)
            ws_o.write(row_pos_o, 7, xlwt.Formula("SUM(H"+str(row_data_begin)+":H"+str(row_data_end)+")"), self.total_style_decimal)
            ws_o.write(row_pos_o, 8, xlwt.Formula("SUM(I"+str(row_data_begin)+":I"+str(row_data_end)+")"), self.total_style_decimal)
            
            # Footer
            ws_o.write(row_pos_o + 1, 0, None)
            ws_o.write(row_pos_o + 2, 0, _p.datetime + ' ' + _p.username)

report_stock_xls('report.Report Stock', 'ms.report.stock.xls', parser=ms_report_stock_print_xls)