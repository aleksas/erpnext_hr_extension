// Copyright (c) 2016, Aleksas Pielikis and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Regular Work Summary Replies"] = {
	"filters": [
		{
			"fieldname":"group",
			"label": __("Group"),
			"fieldtype": "Link",
			"options": "Regular Work Summary Group",
			"reqd": 1
		},
		{
			"fieldname": "range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"reqd": 1
		}
	]
}
