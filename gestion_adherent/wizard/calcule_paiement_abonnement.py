# -*- encoding: utf-8 -*-

from openerp.osv import  osv, orm
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import base64
import xmlrpclib
from openerp import pooler, sql_db , models, api ,fields
from openerp.api import Environment
from openerp.tools.translate import _
import convertion
from openerp.http import request


class paiement_abonnement(osv.Model):
	_name = "paiement.abonnement"

	_order='create_date desc'

	_inherit = [
		'mail.thread'
	]

	_mode_paiement = [
	('jours','Par Jour'),
	('mois', 'Par Mois'),
	('seance', 'Par séance')
	]

	_STATE = [
	('total','Totalement payée'),
	('partiel', 'Partièlement payée'),
	('cancel', 'Annulée')
	]

	_MODALITE = [
	('espece','Par Espèce'),
	('cheque', 'Par Cheque'),
	('aterme', 'A tèrme')
	]
	_EXTE_INTER = [
	('interne', 'Interne'),
	('externe', 'Externe')
	]

	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			   return []
		res=[]
		for abonnement in self.browse(cr, uid, ids,context=context):
			res.append((abonnement.id,  str(abonnement.adherent.name)+" "+str(abonnement.adherent.prenom)))            
		return res




	@api.model
	def get_default_date_debut(self):
		gym_ids = self._context.get('active_ids', [])
		gym_adh = self.env[('gym.adherent')].browse(gym_ids)
		return gym_adh.date

	@api.model
	def get_default_ext_int(self):
		gym_ids = self._context.get('active_ids', [])
		gym_adh = self.env[('gym.adherent')].browse(gym_ids)
		return gym_adh.ext_int

	@api.one
	@api.onchange('net_payee','tarif_a_payer')
	def get_reste_a_payer(self):
		self.reste_a_payer = 0.0
		if self.net_payee and self.tarif_a_payer:
			self.reste_a_payer =  self.tarif_a_payer - self.net_payee
			if self.reste_a_payer == 0.0:
				self.state = 'total'
			else:
				self.state ='partiel'
	
	"""Aqui hay los campos del clase primera lista"""
	name=fields.Char('Référence')
	debut = fields.Date('Date debut',default=get_default_date_debut)
	fin = fields.Date('Date fin',default=fields.Datetime.now)
	#ajouter le 12/09/2018
	solde_jour = fields.Integer('Nombre jours')
	####
	unit = fields.Float('Tarif Séance')
	nb_seance = fields.Integer('Nombre Séance',default=1)
	options= fields.One2many('gym.acheter.option','paiement_id','Options')
	services = fields.One2many('gym.acheter.service','paiement_id','Services')
	mode_p =fields.Selection(_mode_paiement,'Mode paiement',default='jours')
	is_options = fields.Boolean('Autres Services')
	garderier = fields.Boolean('Ajouter Transport')
	tarif_garderier = fields.Float('Tarif Transport',default=0.0)
	nb_jour_garderier = fields.Integer('Nombre Jours de Transport')
	state = fields.Selection(_STATE,'Etat facture')
	modalite = fields.Selection(_MODALITE,'Modalité de paiement',default='espece')
	add_remise = fields.Boolean('Ajouter remise')
	remise = fields.Float('Remise')
	scholar = fields.Boolean('Ajouter Frais scolaire ?')
	tarif_scholar = fields.Float('Frais Scolaire',default=0.0)
	date_facture = fields.Datetime('Date de facturation',default=fields.Datetime.now)
	note = fields.Text('Observations')
	#recuperar toda la suma de los productos vendidos o los servicios a pagar
	ext_int = fields.Selection(_EXTE_INTER,string='Situation',default=get_default_ext_int)
	generate_invoice = fields.Boolean('Générer une facture',default=True)




	@api.multi
	@api.onchange('options','services')
	def _get_total_options(self):
		total = 0.0
		for option in self:
			option.somme_options = sum(op.somme for op in option.options) + sum(op.somme_service for op in option.services)

		return total

	somme_options = fields.Float('Montant services')



	@api.multi
	def get_default_abonnement_id(self):
		gym_ids = self._context.get('active_ids', [])
		gym_adh = self.env[('gym.adherent')].browse(gym_ids)
		return gym_adh.abonnement_id.id


	@api.depends('adherent')
	def get_default_tarif(self):
		tarif= self.adherent.tarif_tree
		if tarif:
				self.tarif_abonnement = tarif
		return tarif
	tarif_abonnement = fields.Float(compute='get_default_tarif')


	@api.model
	def get_total_mois(self,debut,fin):
		nb_mois= 0
		d1 = datetime.strptime(fin, "%Y-%m-%d")
		d2 = datetime.strptime(debut, "%Y-%m-%d")
		if self.mode_p == 'jours':
			"""
			delta = float(((d1 - d2).days+1)/30.0)
			#if int(d1.month) == 01 or int(d1.month) == 03 or int(d1.month) == 05 or int(d1.month) == 07 or int(d1.month) == 08 or int(d1.month) == 10 or int(d1.month) == 12:
			if  abs((d1-d2).days) == 30:
				delta = float(((d1 - d2).days)/30.0)
			#exceotion pour mois février
			if int(d1.month) == 02 and int(d2.month) == 02 and abs((d1-d2).days) == 28:
				delta = float(((d1 - d2).days+2)/30.0)
			if int(d1.month) == 02 and int(d2.month) == 02 and abs((d1-d2).days) == 27:
				delta = float(((d1 - d2).days+3)/30.0)

			if (int(d1.month) - int(d2.month)) == 3 and abs((d1-d2).days) == 91 or abs((d1-d2).days) == 92:
				delta = 90/30.0

			if  ( abs((d1-d2).days) == 107 or abs((d1-d2).days) == 106 ) and ( (int(d1.month) - int(d2.month)) == 3 or (int(d1.month) - int(d2.month)) == 4 ):
				delta = 105/30.0
			"""
		if self.mode_p == 'mois':
			delta = d1.month - d2.month
		if d1 > d2 :
			nb_mois = float((d1.year - d2.year)*12) + delta
		self.nb_mois = nb_mois
		return nb_mois
	nb_mois = fields.Float(compute='get_total_mois')

	@api.one
	@api.depends('solde_jour','somme_options','unit','nb_seance','fin','debut','tarif_garderier','nb_jour_garderier','remise','tarif_scholar')
	def on_change_tarif_a_payer(self):
		result = 0.0
		if self.mode_p == 'mois':
			if self.abonnement_id.garderier:
				a_one__month =self.tarif_abonnement
				nb_mois = self.get_total_mois(self.debut,self.fin)
				result = ( a_one__month*nb_mois + self.abonnement_id.tarif_garderier * nb_mois )
				#a =  self._get_total_options()+ a_one__month*nb_mois + self.abonnement_id.tarif_garderier * nb_mois - self.remise
			else:
				a_one__month =self.tarif_abonnement
				nb_mois = self.get_total_mois(self.debut,self.fin)
				result = ( a_one__month*nb_mois )


				#a =  (self._get_total_options()+ a_one__month*nb_mois + (self.tarif_garderier * self.nb_jour_garderier)) - self.remise

		elif self.mode_p == 'jours':

			if self.abonnement_id and self.abonnement_id.garderier:
				a_one__month =self.tarif_abonnement
				nb_mois = float(self.solde_jour/30.0)
				result = ( a_one__month*nb_mois + (self.abonnement_id.tarif_garderier * nb_mois) )

			else:
				a_one__month =self.tarif_abonnement
				nb_mois = float(self.solde_jour)/30.0
				result = (a_one__month*nb_mois )
				

		else:
			result = (self.unit*self.nb_seance)
			#a = self._get_total_options()+(self.unit*self.nb_seance)

		if self.scholar:
			result += self.tarif_scholar

		if self.add_remise:
			result -= self.remise

		if self.garderier:
			 result += self.tarif_garderier * self.nb_jour_garderier


		result += self.somme_options
		self.tarif_a_payer = result


		return self.tarif_a_payer




	@api.multi
	def get_adherent_contrat(self):
		gym_ids = self._context.get('active_ids', [])
		gym_adh = self.env[('gym.adherent')].browse(gym_ids)
		return gym_adh

	@api.one
	@api.onchange('adherent')
	def onchange_contrat(self):
		self.abonnement_id = self.adherent.abonnement_id.id
		return self.abonnement_id.id

	@api.one
	@api.onchange('adherent','solde_jour')
	def onchange_abonement_remise(self):
		if self.adherent.abonnement_id.remise:
			self.add_remise = True
			self.remise = self.adherent.abonnement_id.taux_remise * float(self.solde_jour)/30.0
			return self.abonnement_id.taux_remise * float(self.solde_jour)/30.0


	@api.one
	@api.onchange('solde_jour')
	def onchange_date_fin(self):
		if self.solde_jour:
			if self.debut:
				self.fin = datetime.strptime(str(self.debut), "%Y-%m-%d") + timedelta(days=int(self.solde_jour))
			else:
				raise osv.except_osv(
					_('Attention!'),
					_('Prière de choisir une date debut'))
	
		


	"""Aqui hay los campos del clase //segunda lista"""

	abonnement_id = fields.Many2one('gym.abonnement','Abonnement', default= get_default_abonnement_id)
	tarif_a_payer = fields.Float('Tarif a payer',compute='on_change_tarif_a_payer',readonly=False,store=True,track_visibility='always')
	adherent = fields.Many2one('gym.adherent','Adherent',default=get_adherent_contrat, store=True)

	reste_a_payer = fields.Float('Reste a payer',store=True,readonly=False)
	net_payee = fields.Float('Net payé',track_visibility='always')
	"""Fin declaracion de los campos"""

	@api.multi
	@api.depends('net_payee')
	def get_amount_letter(self):
		amount = convertion.trad(self.tarif_a_payer,'Dinar')
		return amount

	@api.multi
	@api.depends('reste_a_payer')
	def get_reste_payer_letter(self):
		amount = convertion.trad(self.reste_a_payer,'Dinar')
		return amount


	@api.one
	@api.onchange('tarif_a_payer')
	def onchange_total_payer(self):
		self.net_payee = self.tarif_a_payer
		return self.net_payee

	@api.multi
	def open_record(self):
			rec_id = self.id
			form_id = self.env.ref('gestion_adherent.view_paieabonn_compute_wizard_history_2')

			return {
					'type': 'ir.actions.act_window',
					'name': 'Historique des paiements',
					'res_model': 'paiement.abonnement',
					'res_id': rec_id,
					'view_type': 'form',
					'view_mode': 'form',
					'view_id': form_id.id,
					'context': {},           
					#'flags': {'initial_mode': 'edit'},
					'target': 'current',
				}

	#la funcion principal para añadir los dias pagados a la suscripcion despues el pago
	@api.multi
	def paye_abonnement(self,context=None):
		if self.ext_int == 'interne':
			gym_ids = context.get('active_ids', [])
			gym_adh = self.env[('gym.adherent')]
			if self.debut and self.fin:
				for record in gym_adh.browse(gym_ids):
					record.abonnement_id.debut = self.debut
					record.abonnement_id.jusqua = self.fin
					#record.solde = abs(self.fin - self.debut)
					record.date=self.fin


	#abreviacion de los meses
	def get_month_letter(self):
		month = (date.today()).month
		month_letters = [('1','Jan'),
		('2','Fév'),
		('3','Mars'),
		('4','Avl'),
		('5','Mai'),
		('6','Jui'),
		('7','juil'),
		('8','Aout'),
		('9','Sept'),
		('10','Oct'),
		('11','Nov'),
		('12','Déc')]

		return month_letters[int(month)-1][1]

	#para añadir una sequencia a cada pago despues la creacion del record
	@api.model
	def create(self,vals):
		sequence=self.env[('ir.sequence')].get('reg_code_paie')
		ref = sequence+'-'+self.get_month_letter()+'-'+str((date.today()).year-2000)
		vals['name']=ref
		rec = super(paiement_abonnement, self).create(vals)
		if vals['ext_int'] == 'interne' and vals['abonnement_id']:
			##
			id_ab = int(vals['abonnement_id'])
			id_child = int(vals['adherent'])
			abonnement_id = self.env['gym.abonnement'].browse(id_ab)
			child = self.env['gym.adherent'].browse(id_child)
			abonnement_id.update({'jusqua':vals['fin'],'debut':vals['debut'],'mode_p':vals['mode_p']})
			if vals['solde_jour']:
				abonnement_id.update({'solde_jour':vals['solde_jour']})
			child.update({'date':vals['fin']})
			##
		if vals['tarif_a_payer'] == 0.0:
					raise osv.except_osv(
					_('Attention!'),
					_('La somme totale est égale a zéro !.'))

		if (vals['mode_p'] == 'mois' or vals['mode_p'] == 'jours') and not vals['adherent']:
					raise osv.except_osv(
					_('Attention!'),
					_('Veuillez ajouter un adhérent/un abonnement a ce paiement svp!.'))
		return rec

	@api.one
	def cancel_fac(self):
		self.state = 'cancel'


class gym_service(models.Model):
	_name = 'gym.service'
	_order='unit_mesure desc'


	name=fields.Char('Service')
	tarif= fields.Float('Tarif')
	unit_mesure = fields.Float('Unité')


class gym_option(models.Model):
	_name = 'gym.option'
	_order='quantite desc'


	name=fields.Char('Option')
	quantite=fields.Integer('Quantité')
	tarif= fields.Float('Tarif')


class gym_acheter_option(models.Model):
	_name = 'gym.acheter.option'
	_order='create_date desc'


	#recuperar el precio de cada producto
	@api.one
	@api.depends('quantite','option.lst_price')
	def get_tarif(self):

		if self.quantite and self.option.lst_price :
			self.somme = self.option.lst_price*self.quantite

	#recuperar la quantidad disponible de un producto
	@api.onchange('option')
	def get_disponible_qty(self):
			self.qty_dispo = self.option.quantite

			

	qty_dispo = fields.Integer(string='Disponible',readonly=True)
	quantite=fields.Integer('Qty',default=1)
	option = fields.Many2one('product.product','Produits')
	paiement_id = fields.Many2one('paiement.abonnement','Paiement')
	somme= fields.Float('Somme',compute='get_tarif',store='True')

	# #para decrementar la quantidad de un producto despues la venta
	# @api.model
	# def create(self,vals):
	# 	rec = super(gym_acheter_option, self).create(vals)

	# 	option = vals['option']
	# 	op = self.env['gym.option'].search([]).browse(option)
	# 	if op.quantite - vals['quantite'] > 0:
	# 			op.write({'quantite':op.quantite - vals['quantite']})
	# 	else:
	# 			raise osv.except_osv(
	# 				_('Attention!'),
	# 				_('Stock est insuffisant !.'))

	# 	return rec


	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			   return []
		res=[]
		for option in self.browse(cr, uid, ids,context=context):
			res.append((option.id,  str(option.option.name)))            
		return res



class gym_acheter_service(models.Model):
	_name = 'gym.acheter.service'
	_order='create_date desc'

	#recuperar el precio de un servicio
	@api.one
	@api.depends('duree','service.tarif')
	def get_tarif_service(self):

		if self.duree and self.service.tarif :
			self.somme_service = self.service.tarif*self.duree/self.service.unit_mesure

	duree = fields.Float('Durée')
	service = fields.Many2one('gym.service','Service')
	paiement_id = fields.Many2one('paiement.abonnement','Paiement')
	somme_service = fields.Float('Somme',compute='get_tarif_service',store='True')
	transport_id = fields.Many2one('adherent.transport','Transport')


class depense_depense(models.Model):
	_name = 'depense.depense'
	_order = 'date desc'

	_TYPE_DEPENSE = [
			('salaire','Salaire'),
			('avance', 'Avance'),
			('remboursement','Remboursement'),
			('fm', "Main d'oeuvre"),
			('achat', 'Achat'),
			('Autre', 'Autre'),
			]

	@api.model
	def get_default_employee_id(self):
		gym_ids = self._context.get('active_ids', [])
		gym_adh = self.env[('hr.employee')].browse(gym_ids)
		return gym_adh.id




	name = fields.Char('Dépense')
	frais = fields.Float('Montant',required=True)
	date = fields.Date('Date',required=True)
	bloc = fields.Boolean('A ne pas compter')
	type_depense = fields.Selection(_TYPE_DEPENSE,'Type dépense',default='Autre')
	employee_id = fields.Many2one('hr.employee','Employé',default=get_default_employee_id)


	@api.multi
	@api.onchange('employee_id','type_depense','date')
	def onchange_name_depense(self):
			if self.employee_id and self.type_depense and self.date:
				session = request.__dict__.get('jsonrequest')
				params = session.get('params')
				args = params.get('args')[1]
				emp = args.get('employee_id')
				id_emp = emp.get('id')
				fecha = datetime.strptime(str(self.date), "%Y-%m-%d")
				name = str(self.employee_id.name)

				self.name =  str(self.type_depense) +" Le "+str(fecha.year)+'/'+str(fecha.month)+'/'+str(fecha.day)+ " Pour l'employé " + name

	@api.multi
	@api.onchange('type_depense')
	def onchange_bloc(self):
		if self.type_depense == 'remboursement':
			self.bloc = True
		else :
			self.bloc = False

	@api.multi
	@api.onchange('employee_id','type_depense','date','frais')
	def get_all_avance(self):
		if self.employee_id and self.type_depense == 'salaire':
			fin = debut = False
			somme_avance = 0.0
			somme_rembourssement = 0.0
			if self.date:
				fecha = datetime.strptime(str(self.date), "%Y-%m-%d")
				mois = fecha.month
				annee = fecha.year
				debut = datetime.strptime(str(annee)+'-'+str(mois)+'-01', "%Y-%m-%d")
				if mois == 2:
					fin = datetime.strptime(str(annee)+'-'+str(mois)+'-28', "%Y-%m-%d")
				else :
					fin = datetime.strptime(str(annee)+'-'+str(mois)+'-30', "%Y-%m-%d")

				session = request.__dict__.get('jsonrequest')
				params = session.get('params')
				args = params.get('args')[1]
				emp = args.get('employee_id')
				id_emp = emp.get('id')
				avances = self.env['depense.depense'].search([('employee_id','=',id_emp),('date','>=',debut),('date','<=',fin)])
				#base_url = self.env['ir.config_parameter'].get_param('web.base.url')
				for a in avances:
					if a.type_depense == 'avance':
						somme_avance += a.frais
					elif a.type_depense == 'remboursement':
						somme_rembourssement += a.frais
					else:
						continue
			self.frais = ( self.employee_id.base + somme_rembourssement ) - somme_avance


class adherent_transport(models.Model):
	_name = 'adherent.transport'
	_inherit = [
		'mail.thread'
	]
	_order = 'date desc'


	_STATE = [
	('encours','En cours'),
	('close', 'Terminée'),
	('cancel', 'Annulée')
	]

	_MODAL = [
	('espece','Espèce'),
	('cheque', 'Cheque'),
	('terme', 'A tèrme')
	]


	@api.one
	def validate_liv(self):
		self.state = 'close'


	@api.one
	def cancel_liv(self):
		self.state = 'cancel'


	@api.one
	def set_draft_liv(self):
		self.state = 'encours'

	date = fields.Datetime('Date Transport',default=fields.Datetime.now)
	name = fields.Char('Référence')
	partner = fields.Many2one('res.partner','Partenaire/Client')
	price = fields.Float('Prix Total',track_visibility='always')
	transport= fields.One2many('gym.acheter.service','transport_id','Transport')
	state = fields.Selection(_STATE,'Etat Transport',default='encours')
	modalite = fields.Selection(_MODAL,'Modalité de paiement',default='espece')
	note = fields.Text('Observations')

	@api.multi
	@api.depends('transport')
	def _get_total_options(self):
		total = 0.0
		for option in self:
			option.somme_options = sum(op.somme_service for op in option.transport)
			total = option.somme_options
		return total

	somme_options = fields.Float(compute='_get_total_options',invisible=True)


	@api.onchange('somme_options')
	def onchange_somme_transport(self):
		if self.somme_options:
			self.price = self.somme_options


	@api.multi
	@api.depends('price')
	def get_amount_letter(self):
		amount = convertion.trad(self.price,'Dinar')
		return amount