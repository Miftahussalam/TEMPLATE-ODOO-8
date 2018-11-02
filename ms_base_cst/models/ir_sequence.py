from openerp import models, SUPERUSER_ID

class ir_sequence(models.Model):
    _inherit = 'ir.sequence'
    
    def get_sequence(self, cr, uid, name, context=None):
        id_sequence = self.search(cr, uid, [('name', '=', name)])
        if not id_sequence :
            id_sequence = self.create(cr, SUPERUSER_ID, {
                'name': name,
                'implementation': 'no_gap',
                'prefix': name + '/%(y)s/%(month)s/',
                'padding': 5
            })
        return self.next_by_id(cr, uid, id_sequence)
    