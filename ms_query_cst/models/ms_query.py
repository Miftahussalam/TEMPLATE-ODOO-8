from openerp import fields, api, models

class ms_query(models.Model):
    _name = "ms.query"
    _description = "Query"
    
    backup = fields.Text('Backup Syntax')
    name = fields.Text('Syntax')
    result = fields.Text('Result')
            
    @api.multi
    def execute_query(self):
        self._cr.execute(self.name)
        try :
            self.result = self._cr.fetchall()
        except Exception :
            self.result = 'berhasil'
        