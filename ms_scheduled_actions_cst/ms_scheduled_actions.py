from openerp import models, fields, api

class ms_scheduled_actions(models.Model):
    _name = "ms.scheduled.actions"
    _description = "Scheduled Actions"
    
    ## Reset Monthly Sequence
    ## Expected runs on First Day of Every Month
    @api.multi
    def action_reset_sequence(self):
        sequence_ids = self.env['ir.sequence'].sudo().search(['|',('prefix','like','%(month)s%'),('suffix','like','%(month)s%')])
        sequence_ids.write({'number_next_actual':1})
        