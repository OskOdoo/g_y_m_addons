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

class gym_adherent(models.Model):
	 

	_name = "gym.adherent"


	_order='name desc'




	_FIDELITE = [
	('0', ''),
	('1', 'Débutant'),
	('2', 'En progrés'),
	('3', 'Compétant'),
	('4', 'Profésionnel')
	]
	_sexe = [
	('masc', 'Garçon'),
	('fem', 'Fille')
	]

	_GS = [
	('0', ''),
	('1', 'A'),
	('2', 'B'),
	('3', 'AB'),
	('4', 'O')
	]


	_GS2 = [
	('pos', 'Positif'),
	('neg', 'Négatif')
	]

	_EXTE_INTER = [
	('interne', 'Interne'),
	('externe', 'Externe')
	]

	def name_get(self, cr, user, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		if not len(ids):
			return []
		def _name_get(d):
			name = d.get('name','')
			prenom = d.get('prenom',False)
			# Vivek
			#End
			if prenom:
				name = '%s %s' % (name,prenom)
			return (d['id'], name)


		result = []
		for adherent in self.browse(cr, user, ids, context=context):
			# Vivek
			prd_temp = self.pool.get('gym.adherent').browse(cr, user, adherent.id, context=context)
			# End
			mydict = {
						  'id': adherent.id,
						  'name': prd_temp.name,
						  #vivek
						  'prenom': prd_temp.prenom,
						  }
			result.append(_name_get(mydict))
		return result

	
	@api.one
	@api.onchange('ext_int')
	def onchange_externe(self):
		if self.ext_int and self.ext_int == 'externe':
			extern_group = self.env['gym.group'].search([('name','=','Externe')]).id 
			if extern_group:
				self.group_id == extern_group
			else: 
				raise osv.except_osv(
								_('Attention !'),
								_('Veillez vérifier l\'existance du groupe "Externe" svp!\n'+
								'-Ajoutez le groupe en cas n\'existe pas \n'+
								'-Ecrivez le nom du groupe Correctement ( Externe )'))
			



	"""Aqui hay los campos del clase"""
	name = fields.Char('Nom Enfant', required=True)
	date_debut = fields.Date('Date debut',default=fields.Datetime.now)
	prenom = fields.Char('Prénom Enfant')
	cn_id = fields.Char('Adresse')
	date_nais =  fields.Date('Date de naissance')
	lieu_nais =  fields.Char('Lieu de naissance')
	fidelite =fields.Selection(_FIDELITE,'Catégorie')
	mois_payee = fields.Boolean()
	# abonnement_id = fields.Many2one('gym.abonnement','Abonnement')
	solde = fields.Integer(string='solde')
	tarif_tree = fields.Float(string='Montant a payer')
	image =fields.Binary(string="Photo")

	cmpt = fields.Integer('Retardement')
	sexe =fields.Selection(_sexe,'Sexe')
	date = fields.Date('Date de prochaine paiement')
	color = fields.Integer('Color index', default=0,readonly=False)
	parents = fields.Many2many('res.partner',string='Tuteurs',domain=[('tuteur','=',True)])
	poids = fields.Float('Poids')
	taille= fields.Float('Taille')
	groupe_sanguin = fields.Selection(_GS,'Groupe Sanguin')
	rhesus = fields.Selection(_GS2,'Rhesus')
	pere = fields.Char('Père')
	mere = fields.Char('Mère')
	partner_mobile = fields.Char('Mobile')
	ext_int = fields.Selection(_EXTE_INTER,string='Situation',default='interne')
	default_code = fields.Char('Identifiant')
	securite_sociale = fields.Char('Sécurité Sociale')

	etablissement_ids = fields.One2many('saison.scolaire.line','adherent','Scolarité')
	compensation_ids = fields.One2many('handicap.compensation','adherent','Compensation')
	assure = fields.Many2one('res.partner','Assure',domain=[('assure','=',True)])
	saison = fields.Many2one('saison.scolaire',default=1)
	abonnement_ids = fields.One2many('sale.order','child','Abonnements')
	count = fields.Integer('Abonnements',compute='count_abonnements')
	
	@api.multi
	def count_abonnements(self):
		for record in self:
			record.count = record.env['sale.order'].search_count([('child','=',record.id),('state','in',('progress','manual','done'))])
		return record.count
	"""Fin declaracion de los campos"""

