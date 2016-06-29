import time
from openerp.report import report_sxw
 
class ParserStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ParserStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_kursus': self.get_kursus,
        })
    
    def get_kursus(self, form):     
        data = self.pool.get('training.kursus').browse(self.cr, self.uid, [form['form']['id']])
        return data
    
report_sxw.report_sxw('report.rml.sesi', 'training.sesi', 'addons/training_openerp/report/report_sesi.rml', parser = ParserStatus, header = False)
report_sxw.report_sxw('report.webkit.kursus', 'training.kursus', 'addons/training_openerp/report/report_kursus.mako', parser = ParserStatus, header = False)