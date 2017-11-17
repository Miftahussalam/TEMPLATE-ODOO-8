from openerp import api, models
from datetime import datetime
import pytz
import string
from pytz import timezone

class res_company(models.Model):
    _inherit = 'res.company'
    
    def get_default_date(self, cr, uid, context=None):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
    
    @api.one
    def get_default_date_one(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
    
    @api.multi
    def get_default_date_multi(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))    
    
    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
    
    @api.multi
    def punctuation(self, words):
        for n in range(len(words)) :
            if words[n] in string.punctuation :
                return True
        return False
    