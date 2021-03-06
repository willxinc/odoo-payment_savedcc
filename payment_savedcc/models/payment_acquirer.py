# -*- coding: utf-'8' "-*-"

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _

import logging
import pprint

_logger = logging.getLogger(__name__)


class SavedCCPaymentAcquirer(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_providers(self, cr, uid, context=None):
        providers = super(SavedCCPaymentAcquirer, self)._get_providers(cr, uid, context=context)
        providers.append(['savedcc', 'Saved Credit Card'])
        return providers

    def savedcc_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/savedcc/feedback'

    def _format_savedcc_data(self, cr, uid, context=None):
        bank_ids = [bank.id for bank in self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.bank_ids]
        # filter only bank accounts marked as visible
        bank_ids = self.pool['res.partner.bank'].search(cr, uid, [('id', 'in', bank_ids), ('footer', '=', True)], context=context)
        accounts = self.pool['res.partner.bank'].name_get(cr, uid, bank_ids, context=context)
        bank_title = _('Bank Accounts') if len(accounts) > 1 else _('Bank Account')
        bank_accounts = ''.join(['<ul>'] + ['<li>%s</li>' % name for id, name in accounts] + ['</ul>'])
        post_msg = '''<div>
<h3>Please use the following savedcc details</h3>
<h4>%(bank_title)s</h4>
%(bank_accounts)s
<h4>Communication</h4>
<p>Please use the order name as communication reference.</p>
</div>''' % {
            'bank_title': bank_title,
            'bank_accounts': bank_accounts,
        }
        return post_msg

    def create(self, cr, uid, values, context=None):
        """ Hook in create to create a default post_msg. This is done in create
        to have access to the name and other creation values. If no post_msg
        or a void post_msg is given at creation, generate a default one. """
        if values.get('name') == 'savedcc' and not values.get('post_msg'):
            values['post_msg'] = self._format_savedcc_data(cr, uid, context=context)
        return super(SavedCCPaymentAcquirer, self).create(cr, uid, values, context=context)


class SavedCCPaymentTransaction(osv.Model):
    _inherit = 'payment.transaction'

    _columns = {
        'savedcc_name': fields.char('CC Holder Name'),
        'savedcc_type': fields.char('CC type'),
        'savedcc_number': fields.char('CC Number'),
        'savedcc_expdate': fields.char('CC Expiry Date'),
        'savedcc_code': fields.char('CC Security Code'),
    }

    def _savedcc_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx_ids = self.search(
            cr, uid, [
                ('reference', '=', reference),
            ], context=context)

        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        return self.browse(cr, uid, tx_ids[0], context=context)

    def _savedcc_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        if float_compare(float(data.get('amount', '0.0')), tx.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % tx.amount))
        if data.get('currency') != tx.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), tx.currency_id.name))

        return invalid_parameters

    def _savedcc_form_validate(self, cr, uid, tx, data, context=None):
        data = {
            'savedcc_name': data.get('ccName'),
            'savedcc_type': data.get('ccType'),
            'savedcc_number': data.get('ccNumber'),
            'savedcc_expdate': data.get('ccDate'),
            'savedcc_code': data.get('ccCode'),
            'partner_reference': data.get('ccName')
        }
        if (data.get('ccName') == "" or data.get('ccNumber') == "" or data.get('ccDate') == ""):
            error = 'Received blank data for SavedCC payment %s, set as error' % (tx.reference)
            _logger.info(error)
            data.update(state='error', state_message=error)
        else:
            _logger.info('Validated savedcc payment for tx %s: set as done' % (tx.reference)),
            data.update(state='done', date_validate=data.get('date_stamp', fields.datetime.now()))
        return tx.write(data)
