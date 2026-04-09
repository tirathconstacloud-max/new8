source_link = "https://github.com/libracore/commerciumconnector"
docs_base_url = "https://github.com/libracore/commerciumconnector"
headline = "ERPNext Commercium Connector"
sub_heading = "Sync transactions between Commercium and ERPNext"
long_description = """ERPNext Commercium Connector will sync data between your comerce and ERPNext accounts.
<br>
<ol>
	<li> It will sync Products and Cutomers between commercium and ERPNext</li>
	<li> It will push Orders from commercium to ERPNext
		<ul>
			<li>
				If the Order has been paid for in commercium, it will create a Sales Invoice in ERPNext and record the corresponding Payment Entry
			</li>
			<li>
				If the Order has been fulfilled in commercium, it will create a draft Delivery Note in ERPNext
			</li>
		</ul>
	</li>
</ol>"""
docs_version = "1.0.0"

def get_context(context):
	context.title = "ERPNext Commercium Connector"