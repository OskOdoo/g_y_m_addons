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

class etablissement_adherent(models.Model):
	 

	_name = "etablissement.adherent"


	_order='typeE desc'


	name = fields.Char('Etablissement')
	siege = fields.Char('Siège')
	contact = fields.Char('Contact')
	typeE = fields.Selection([('ecole','Ecole'),('centre','Centre')],string='Type')



class saison_soclaire(models.Model):
	 

	_name = "saison.scolaire"


	_order='name desc'


	name = fields.Char('Saison')
	date_debut = fields.Date('Date debut')
	date_fin = fields.Date('Date fin')




class saison_soclaire_line(models.Model):
	 

	_name = "saison.scolaire.line"


	adherent = fields.Many2one('gym.adherent','Adhérent')
	ecole= fields.Many2one('etablissement.adherent')
	saison = fields.Many2one('saison.scolaire','Saison')
	niveau = fields.Char('Niveau')