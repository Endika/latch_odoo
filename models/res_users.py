# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Endika Iglesias <endika2@gmail.com>
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


class res_users(orm.Model):
    _inherit = "res.users"

    def authenticate(self, db, login, password, user_agent_env):
        uid = self._login(db, login, password)
        if uid:
            cr = self.pool.cursor()
            uid_admin = openerp.SUPERUSER_ID
            context = None
            latch_pool = self.pool['latch.odoo']
            latch_ids = latch_pool.search(cr,
                                          uid_admin,
                                          [('name', '=', int(uid))])
            if latch_ids:
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
                    app_id = False
                if secret_key is False or len(secret_key) <= 0:
                    secret_key = False

                latch_obj = latch_pool.browse(cr, uid_admin, latch_ids)
                api = latch.Latch(app_id, secret_key)
                response = api.status(str(latch_obj['token']))
                data = response.get_data()
                error = response.get_error()
                try:
                    if data['operations'][app_id]['status'] != 'on':
                        return False
                except Exception, e:
                    return False

        return super(res_users, self).authenticate(db, login, password,
                                                   user_agent_env)

    def action_latch_wizard(self, cr, uid, ids, vals, context=None):
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'latch_odoo', 'wizard_latch_pare')
        ctx = {'res_users_popup':True}
        return {
            'name': 'Latch account',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'latch.odoo',
            'context': ctx,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': [res and res[1] or False],
        }
