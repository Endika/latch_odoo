# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Endika Iglesias <endika2@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.config import config
import openerp
import latch
import logging
_logger = logging.getLogger(__name__)



class latch_odoo(orm.Model):
    _name = "latch.odoo"
    _description = "Latch Odoo"
    _columns = {
        'name': fields.many2one('res.users', 'User',
                                required=True,
                                readonly=False),
        'token': fields.char("Token", size=200,
                             required=False,
                             readonly=False),
        'code': fields.char("code", size=20,
                            required=False),
        'state': fields.selection((('sinparear', 'Sin parear'),
                                   ('pareado', 'Pareado')),
                                  'Estado'),
    }

    def _get_uid(self, cr, uid, context):
        return uid

    def _load_latch(self, cr, uid, context):
        is_popup = context.get('res_users_popup',False)
        if not is_popup:
            return 'sinparear'

        uid_admin = openerp.SUPERUSER_ID
        latch_pool = self.pool['latch.odoo']
        latch_ids = latch_pool.search(cr,
                                      uid_admin,
                                      [('name', '=', int(uid))])
        pare_state = 'sinparear'
        if latch_ids:
            latch_obj = self.browse(cr, uid_admin, latch_ids)
            pare_state = latch_obj['state']
        return pare_state

    _defaults = {'state': _load_latch,
                 'name': _get_uid}

    def _conf(self, cr, uid, context=None):
        config_pool = self.pool.get('ir.config_parameter')
        app_id = config_pool.get_param(cr, uid,
                                       'latch_odoo.app_id',
                                       default=False,
                                       context=context)
        secret_key = config_pool.get_param(cr,
                                           uid,
                                           'latch_odoo.secret_key',
                                           default=False,
                                           context=context)
        if app_id is False or len(app_id) <= 0:
            return False
        if secret_key is False or len(secret_key) <= 0:
            return False
        return app_id, secret_key

    def create(self, cr, uid, vals, context=None):
        if not 'name' in vals.keys():
            if 'code' in vals.keys() and not vals['code'] is False:
                #self.action_get_pair_user(cr, uid, [], vals, context=context)
                vals['name'] = uid
            else:
                self.action_get_unpair_user(cr, uid, [], vals, context=None)
                return True
        if 'token' in vals.keys() and \
            not ((type(vals['token']) is str and len(vals['token']) > 0)):
            if type(vals['code']) is bool:
                return False
            app_id, secret_key = self._conf(cr, uid, context=context)
            api = latch.Latch(app_id, secret_key)
            response = api.pair(vals['code'])
            data = response.get_data()
            error = response.get_error()
            if 'accountId' not in data:
                return False
            vals['token'] = str(data['accountId'])
        vals['code'] = ""
        vals['state'] = "pareado"

        return super(latch_odoo, self).create(cr, uid, vals,
                                              context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not type(vals['token']) is str or len(vals['token']) <= 0:
            return False
        app_id, secret_key = self._conf(cr, uid, context=context)
        api = latch.Latch(app_id, secret_key)
        response = api.status(vals['token'])
        data = response.get_data()
        error = response.get_error()
        try:
            latch_status = data['operations'][app_id]['status']
            ok = False if latch_status != 'on' else True
        except Exception, e:
            return False

        return super(latch_odoo, self).write(cr, uid, ids,
                                             vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        app_id, secret_key = self._conf(cr, uid, context=context)
        api = latch.Latch(app_id, secret_key)
        for latch_id in ids:
            latch_obj = self.browse(cr, uid, latch_id, context=context)
            if type(latch_obj['token']) is str:
                response = api.unpair(latch_obj['token'])
                data = response.get_data()
                error = response.get_error()
        return super(latch_odoo, self).unlink(cr, uid, ids, context=context)

    def action_get_pair_user(self, cr, uid, ids, vals, context=None):
        #latch_pool = self.pool.get('latch.odoo')
        #latch_pool.create(cr, uid, {'name': uid, 'code': vals['code']}, context=context)
        return True

    def action_get_unpair_user(self, cr, uid, ids, vals, context=None):
        app_id, secret_key = self._conf(cr, uid, context=context)
        api = latch.Latch(app_id, secret_key)
        uid_admin = openerp.SUPERUSER_ID
        latch_pool = self.pool['latch.odoo']
        latch_ids = latch_pool.search(cr,
                                      uid_admin,
                                      [('name', '=', int(uid))])
        if latch_ids:
            self.unlink(cr, uid_admin, latch_ids, context=context)