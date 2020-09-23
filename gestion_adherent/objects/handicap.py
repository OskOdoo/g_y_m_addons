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

class handicap_compensation(models.Model):
	 

	_name = "handicap.compensation"


	_order='name desc'

	adherent = fields.Many2one('gym.adherent','Malade')
	name = fields.Char('Designation')
	categorie = fields.Char('Catégorie')
	date = fields.Date('Date')
	ipp = fields.Char('IPP ou %')
	oranisme = fields.Char('Organisme')
	echeance =fields.Char('Echeance')
	impact = fields.Char('Cadre')


class securite_sociale(models.Model):
	 

	_name = "securite.sociale"


	_order='name desc'

	name = fields.Char('Immatriculation')
	categorie = fields.Char('Catégorie')
	date = fields.Date('Date')
	ipp = fields.Char('IPP ou %')
	oranisme = fields.Char('Organisme')
	echeance =fields.Char('Echeance')
	impact = fields.Char('Cadre')
