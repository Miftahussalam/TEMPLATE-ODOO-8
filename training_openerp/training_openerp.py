from openerp.osv import osv, fields
import time
from openerp import tools

class Kursus (osv.osv):
    _name = 'training.kursus'
    
    def _check_keterangan(self, cr, uid, ids, context=None):
        cek = True
        kursus = self.browse(cr, uid, ids, context=context)[0]
        if kursus.name == kursus.keterangan:
            return False
        return cek
    
    _columns = {
        'name': fields.char('Judul Kursus', 128, required=True),
        'keterangan': fields.text('Keterangan'),
        'koordinator_id': fields.many2one('res.users', string='Koordinator', select=True),
        'sesi_ids': fields.one2many('training.sesi', 'kursus_id', 'Sesi'),
    }
    
    _constraints = [
        (_check_keterangan, 'Keterangan tidak boleh sama dengan nama kursus !', ['name', 'keterangan']),
    ]
     
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Nama kursus harus unique !'),
    ]
    
    def copy(self, cr, uid, ids, defaults, context=None):
        # Simpan field name dari record yang telah di duplicate ke variabel nama_lama
        nama_lama = self.browse(cr, uid, ids, context=context).name
         
        # Bikin nama copyan dari record yang telah di duplicate ke variable nama_baru
        nama_baru = 'Copy of %s' % nama_lama
         
        # Pastikan nama copyan dari record yang kita duplicate TIDAK ADA di tabel
        eksis = self.search(cr, uid, [('name', 'like', nama_baru)])
         
        # Jika ternyata nama copyan dari record yang kita duplicate ADA di tabel MAKA tambahkan bilangan integer
        if eksis:
            nama_baru = '%s %d' % (nama_baru, len(eksis)+1)
         
        # Isi nilai field name yang baru dengan nama yang telah kita buat pada variabel nama_baru
        defaults['name'] = nama_baru
         
        # Panggil method parent dengan super()
        return super(Kursus, self).copy(cr, uid, ids, defaults, context=context)
    
    def report_kursus(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'training.kursus'
        datas['form'] = self.read(cr, uid, ids)[0]
  
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'webkit.kursus',
            'report_type': 'webkit',
            'datas': datas,
        }

Kursus()

class Sesi(osv.osv):
    _name = 'training.sesi'
    
    def _get_kehadiran_persen(self, cr, uid, ids, field, arg, context=None):
        val = self.browse(cr,uid,ids,context=context)
        result = {}
        for x in val:
            result[x.id] = (len(x.peserta_ids) / float(x.kursi)) * 100.0
        return result
    
    def _get_jumlah_peserta(self, cr, uid, ids, field, arg, context=None):
        val = self.browse(cr,uid,ids,context=context)
        result = {}
        for x in val:
            result[x.id] = len(x.peserta_ids)
        return result
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result
 
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    _columns = {
        'name': fields.char('Judul Sesi', 128, required=True),
        'tanggal_mulai': fields.date('Tanggal Mulai'),
        'durasi': fields.float('Durasi', digits=(16,2), help="Durasi dalam hari"),
        'kursi':fields.integer('Jumlah Kursi'),
        'instructur_id': fields.many2one('res.partner', 'Instructur', domain=[('instructur', '=', True)]),
        'kursus_id':fields.many2one('training.kursus', 'Kursus', required=True, ondelete='cascade'),
        'peserta_ids': fields.one2many('training.peserta', 'sesi_id', 'Peserta'),
        'kuota_kehadiran_persen': fields.function(_get_kehadiran_persen, method=True, type='float', string='Kuota Kursi'),
        'active': fields.boolean('Active'),
        'jumlah_peserta': fields.function(_get_jumlah_peserta, method=True, type='integer', string='Jumlah Peserta'),
        'image': fields.binary("Foto"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image, string="Medium-sized image", type="binary", multi="_get_image",
            store={'training.sesi': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),}),
        'image_small': fields.function(_get_image, fnct_inv=_set_image, string="Small-sized image", type="binary", multi="_get_image",
            store={'training.sesi': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10)}),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')], 'Status', readonly=True),
    }
    
    _defaults = {
        'kursi': 1,
        'active': True,
        'tanggal_mulai': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }
    
    #salah
    def onchange_hitung_kuota(self, cr, uid, ids, kursi, peserta):
        if kursi <= 0:
            return {
                'warning': { 
                    'title': 'Perhatian',
                    'message': 'Jumlah kursi harus diatas 0'
                }
            }
        val = {
            'value': {'kuota_kehadiran_persen': (len(peserta) / float(kursi)) * 100.0}
        }
        return val
    
    def sesi_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})
         
    def sesi_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirmed'})
         
    def sesi_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})
 
Sesi()

class Peserta(osv.osv):
    _name = 'training.peserta'
    _rec_name = 'peserta_id'
    _columns = {
        'peserta_id': fields.many2one('res.partner','Peserta',required=True, ondelete="cascade"),
        'sesi_id': fields.many2one('training.sesi','Sesi', required=True, ondelete="cascade"),
    }
 
Peserta()

class Partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'instructur' : fields.boolean('Instructur'),
    }
Partner()

class WizardTambahPeserta(osv.osv_memory):
    _name = 'training.tambah.peserta.wizard'
    _columns = {
        'sesi_ids': fields.many2many('training.sesi', 'tambah_peserta_sesi_rel', 'tambah_peserta_id', 'sesi_id', 'Sesi', required=True),
        'peserta_ids': fields.one2many('training.peserta.wizard', 'wizard_id', 'Para Peserta'),
    }
 
    def tambah_peserta(self, cr, uid, ids, context=None):
        sesi_obj = self.pool.get('training.sesi')
         
        # Ambil value dari form wizard dan menyimpannya ke variabel wizard
        wizard = self.browse(cr, uid, ids[0], context=context)
         
        # Bikin list/array yang berisi kumpulan id sesi yang dipilih dan menyimpannya ke variabel sesi_ids 
        sesi_ids = [s.id for s in wizard.sesi_ids]
         
        # Contoh code diatas sama seperti ini :
        # sesi_ids = []
        # for s in wizard.sesi_ids:
        #     sesi_ids.append(s.id)
         
         
        # Bikin dict yang berisi kumpulan data peserta yang dipilih dan menyimpannya ke variabel data_peserta
        data_peserta = [{'peserta_id': x.peserta_id.id} for x in wizard.peserta_ids]
         
        # Contoh code diatas sama seperti ini :
        # data_peserta = []
        # for x in wizard.peserta_ids:
        #     data_peserta.append({
        #                        'peserta_id': x.peserta_id.id
        #    })
        # Element dict (key dan value) disesuaikan dengan nama field pada object 'training.peserta'
         
        # Cara lain untuk menambah data peserta melalui object sesi
        sesi_obj.write(cr, uid, sesi_ids, {'peserta_ids': [(0, 0, data) for data in data_peserta]}, context)
 
        return {}
 
WizardTambahPeserta()
   
class WizardPeserta(osv.osv_memory):
    _name = 'training.peserta.wizard'
    _columns = {
        'peserta_id': fields.many2one('res.partner', 'Peserta', required=True),
        'wizard_id':fields.many2one('training.tambah.peserta.wizard'),
    }
    
WizardPeserta()