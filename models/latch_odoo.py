# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Endika Iglesias <endikaig@antiun.com>
#                 Antonio Espinosa <antonioea@antiun.com>
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
import datetime
from openerp.tools.config import config
import datetime
import latch

class latch_odoo(orm.Model):
    _name = "latch.odoo"
    _description = "Latch Odoo"
    _columns = {
        'name': fields.many2one('res.users', 'User',
                                required=True,
                                readonly=False),
        'token': fields.char("Token", size=200,
                             required=False),
        'code': fields.char("code", size=20,
                            required=False),
        'state': fields.char("state", size=20,
                             required=False),
    }

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
        if not ( (type(vals['token']) is str and \
            len(vals['token']) > 0) ):

            app_id, secret_key = self._conf(cr, uid, context=context)
            api = latch.Latch(app_id, secret_key)
            response = api.pair(vals['code'])
            data=response.get_data()
            error=response.get_error()
            if not 'accountId' in data:
                return False
            vals['token'] = str(data['accountId'])
        vals['code'] = ""

        return super(latch_odoo, self).create(cr, uid, vals,
                                              context=context)

    def unlink(self, cr, uid, ids, context=None):
        app_id, secret_key = self._conf(cr, uid, context=context)
        api = latch.Latch(app_id, secret_key)
        latch_obj = self.browse(cr, uid, ids, context=context)
        if type(latch_obj['token']) is str:
            response = api.unpair(latch_obj['token'])
            data=response.get_data()
            error=response.get_error()
        return super(latch_odoo, self).unlink(cr, uid, ids, context)