# -*- encoding: utf-8 -*-

from openerp.osv import  osv, orm
import time
from datetime import date
from datetime import datetime, timedelta
import base64
import xmlrpclib
from openerp import pooler, sql_db , models, api ,fields
from openerp.api import Environment
from openerp.tools.translate import _
import json 
import math
import convertion


class account_ordre(models.Model):
	 
	_name = "account.ordre"
	_order ="id asc"

	name =fields.Char('Titre/Mois')
	date_debut = fields.Date('Date du',default=fields.Datetime.now)
	date_fin = fields.Date('Date au')

	@api.one
	@api.onchange('date_debut')
	def onchange_date_fin(self):
			if self.date_debut:
				self.date_fin = datetime.strptime(str(self.date_debut), "%Y-%m-%d") + timedelta(days=30)
			else:
				raise osv.except_osv(
					_('Attention!'),
					_('Prière de choisir une date debut'))



class account_invoice(models.Model):
	 
	_order ="debut , number_ref asc"
	_inherit = "account.invoice"
	_mode_paiement = [
	('jours','Par Jour'),
	('mois', 'Par Mois'),
	('seance', 'Par séance')
	]

	_cans_casnos = [
	('cnas_en_caisse','CNAS EN CAISSE'),
	('cnas_hors_caisse', 'CNAS HORS CAISSE'),
	('casnos', 'CASNOS'),
	('caisse_militaire', 'CAISSE MILITAIRE')
	]

	@api.model
	def get_ordre_facture(self):
		id_returned = False
		res = self.env.cr.execute('select "id" from "account_ordre" order by "id" desc limit 1')
		#this condition is importante , elimine error 'NoneType' object has no attribute 'id'	
		if res:
			id_returned = self.env.cr.fetchone()
			return id_returned
		else: 
			return False

	@api.multi
	@api.depends('partner_id')
	def onchange_sequence(self):
		if self.partner_id.cnas_casnos in ('cnas_en_caisse','cnas_hors_caisse') :
			self.sequence_id = self.env['ir.sequence'].search([('code','=','code_cnas')])
		else:
			self.sequence_id = self.env['ir.sequence'].search([('code','=','code_casnos')])
		return self.sequence_id


	child= fields.Many2one('gym.adherent','Enfant',required=True)
	debut = fields.Date('Depuis',default=fields.Datetime.now,required=True)
	jusqua = fields.Date('jusqu\' à',default=fields.Datetime.now,required=True)
	jours_ouvrable = fields.Float('Nombre Jours Ouvrable')
	mode_p =fields.Selection(_mode_paiement,'Mode paiement',default='mois')
	cnas_casnos = fields.Selection(_cans_casnos,string='Classement')
	#number = fields.Char(related='number_ref', store=True, readonly=True, copy=False)
	number_ref = fields.Char("Facture Num",copy=False,store=True)
	sequence_id = fields.Many2one('ir.sequence','Sequence',compute='onchange_sequence',store=True)
	ordre_id = fields.Many2one('account.ordre','Ordre du mois')#, default=get_ordre_facture)

	_sql_constraints = [
		('number_ref_uniq', 'unique(number_ref)',
			'Attention la facture doit avoir un numéro unique'),
	]
	# @api.multi
	# def open_wizard(self):
		
	# 	return {
	# 		'view_type': 'form',
	# 		'view_mode': 'form',
	# 		'res_model': 'paiement.abonnement',
	# 		'target': 'new',
	# 		'type': 'ir.actions.act_window',
	# 		'context': {'adherent': self.child.id}
	# 	} 





	@api.multi
	@api.depends('amount_total')
	def get_amount_letter(self):
		amount = convertion.trad(self.amount_total,'Dinar')
		return amount


	
	# @api.multi
	# @api.depends('partner_id')
	# def _get_invoice_number(self):
	# 	res = '/'
	# 	temp = False
	# 	for record in self:
	# 		if record.partner_id and not record.partner_id.is_company:
	# 			temp = str(record.partner_id.securite_s)
	# 		else:
	# 			temp = str(record.child.securite_sociale)
	# 		if temp :
	# 			res = record.number_ref = (datetime.strptime(record.debut, '%Y-%m-%d').date()).strftime('%m')+ str((date.today()).year-2000)+'/'+ temp
	# 	return res



	@api.model
	def create(self,vals): 
		if vals['partner_id']:
			partner = self.env['res.partner'].search([('id','=',vals['partner_id'])])
			if partner.cnas_casnos in ('cnas_en_caisse','cnas_hors_caisse') :
				vals['number_ref']=self.env['ir.sequence'].get('code_cnas')
			if partner.cnas_casnos == 'casnos' :
				vals['number_ref']=self.env['ir.sequence'].get('code_casnos')
		return super(account_invoice , self).create(vals)