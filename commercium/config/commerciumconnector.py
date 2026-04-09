from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Settings"),
			"icon": "fa fa-building",
			"items": [
				{
					"type": "doctype",
					"name": "Commercium",
					"label": _("Commercium"),
					"description": _("Settings"),
				},
			]
		}
	]