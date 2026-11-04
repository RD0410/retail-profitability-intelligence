"""Generate a formula-led Superstore executive workbook from verified reference aggregates.

This is an optional authoring utility. The exported XLSX is already included in
project releases, so end users do not need artifact_tool installed to open it.
"""
from pathlib import Path
try:
 from .reference_data import REFERENCE
except ImportError:
 from reference_data import REFERENCE
from artifact_tool import Workbook, SpreadsheetFile

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'dashboards/retail_profitability_workbook.xlsx'
NAVY='#102F42';TEAL='#16868D';PALE='#E7F4F2';RED='#B94F58';GRAY='#6D8290';LIGHT='#F2F6F8';WHITE='#FFFFFF';INK='#243847'

wb=Workbook.create()
summary=wb.worksheets.add('Executive Summary')
region=wb.worksheets.add('Regional Performance')
subcat=wb.worksheets.add('Subcategory Analysis')
state=wb.worksheets.add('State Risk')
monthly=wb.worksheets.add('Monthly Trend')
scenario=wb.worksheets.add('Recovery Scenario')
notes=wb.worksheets.add('Source & Notes')

# Range helpers only — avoid unsupported isolated style attributes.
def title(sheet,header,sub,last='J'):
 sheet.merge_cells(f'A1:{last}2')
 sheet.get_range('A1').values=[[header]]
 sheet.get_range(f'A1:{last}2').format={'fill':NAVY,'font':{'bold':True,'color':WHITE,'size':18},'vertical_alignment':'center','row_height':25}
 sheet.merge_cells(f'A3:{last}3')
 sheet.get_range('A3').values=[[sub]]
 sheet.get_range(f'A3:{last}3').format={'font':{'size':10,'color':GRAY},'row_height':24}

def table_header(sheet,row,headers):
 x=sheet.get_range_by_indexes(row-1,0,1,len(headers))
 x.values=[headers];x.format={'fill':TEAL,'font':{'bold':True,'color':WHITE,'size':10},'row_height':28,'vertical_alignment':'center'}

def cells(sheet,addr,rows):sheet.get_range(addr).values=rows

def currency(sheet,r):sheet.get_range(r).set_number_format('$#,##0.00;[Red]($#,##0.00)')
def percentage(sheet,r):sheet.get_range(r).set_number_format('0.0%;[Red](0.0%)')
def colwidth(sheet,dict_):
 for col,width in dict_.items():sheet.get_range(f'{col}:{col}').format.column_width=width

# Region data — consolidated verified source slice.
title(region,'REGIONAL PROFITABILITY','Sales-weighted margin comparison | IBM/Tableau fictitious Superstore sample',last='H')
headers=['Region','Net Sales ($)','Profit ($)','Margin %','Avg Discount %','Order Lines','Unique Orders']
table_header(region,5,headers)
reg_orders={'Central':1175,'East':1401,'South':822,'West':1611}
regrows=[]
for d in REFERENCE['regions']:
 regrows.append([d['name'],d['sales'],d['profit'],None,d['discount']/d['n'],d['n'],reg_orders[d['name']]])
cells(region,'A6:G9',regrows)
for i in range(6,10):region.get_range(f'D{i}').formulas=[[f'=IFERROR(C{i}/B{i},0)']]
region.get_range('A10').values=[['TOTAL']]
for col in ('B','C','F','G'):region.get_range(f'{col}10').formulas=[[f'=SUM({col}6:{col}9)']]
region.get_range('D10').formulas=[['=IFERROR(C10/B10,0)']]
region.get_range('E10').formulas=[['=SUMPRODUCT(E6:E9,F6:F9)/SUM(F6:F9)']]
region.get_range('A10:G10').format={'fill':PALE,'font':{'bold':True,'color':INK},'row_height':25}
region.get_range('A6:G9').format.row_height=24
currency(region,'B6:C10');percentage(region,'D6:E10')
colwidth(region,{'A':19,'B':19,'C':19,'D':15,'E':18,'F':17,'G':18,'H':13,'I':13,'J':13})
region.get_range('C6:C9').conditional_formats.add_data_bar({'color':TEAL,'gradient':True})
chart=region.charts.add('bar',{'title':'Profit by region','has_legend':False})
series=chart.series.add('Profit ($)')
series.category_formula="'Regional Performance'!$A$6:$A$9";series.formula="'Regional Performance'!$C$6:$C$9"
chart.set_position('A13','G27')

# Subcategory analysis
cats=sorted(REFERENCE['subcategories'],key=lambda a:a['profit'])
title(subcat,'PRODUCT MIX | SUBCATEGORY MARGIN','Use observed negative-profit lines to identify hypotheses for product pricing and promotions.',last='J')
table_header(subcat,5,['Subcategory','Sales ($)','Profit ($)','Profit Margin','Order Lines','Contribution %'])
sc=[]
for d in cats:sc.append([d['name'],d['sales'],d['profit'],None,d['n'],None])
cells(subcat,'A6:F22',sc)
for i in range(6,23):
 subcat.get_range(f'D{i}').formulas=[[f'=IFERROR(C{i}/B{i},0)']]
 subcat.get_range(f'F{i}').formulas=[[f'=IFERROR(C{i}/\'Regional Performance\'!$C$10,0)']]
currency(subcat,'B6:C22');percentage(subcat,'D6:D22');percentage(subcat,'F6:F22')
subcat.get_range('C6:C22').conditional_formats.add_cell_is({'operator':'lessThan','formula':0,'format':{'font':{'color':RED,'bold':True}}})
colwidth(subcat,{'A':23,'B':19,'C':19,'D':18,'E':18,'F':20,'G':13,'H':13})
scchart=subcat.charts.add('bar',{'title':'Profit contribution by subcategory','has_legend':False})
se=scchart.series.add('Profit ($)');se.category_formula="'Subcategory Analysis'!$A$6:$A$22";se.formula="'Subcategory Analysis'!$C$6:$C$22"
scchart.set_position('G5','O25')

# State risk leaderboard (ten lowest, based on source reference)
title(state,'STATE MARGIN RISK','Low-profit states merit root-cause review; discount association alone is not causal.',last='H')
table_header(state,5,['State','Sales ($)','Profit ($)','Margin %','Avg Discount %','Order Lines'])
srows=[]
for d in REFERENCE['states']:srows.append([d['name'],d['sales'],d['profit'],None,d['discount']/d['n'],d['n']])
cells(state,'A6:F15',srows)
for i in range(6,16):state.get_range(f'D{i}').formulas=[[f'=IFERROR(C{i}/B{i},0)']]
currency(state,'B6:C15');percentage(state,'D6:E15')
state.get_range('C6:C15').conditional_formats.add_cell_is({'operator':'lessThan','formula':0,'format':{'font':{'color':RED,'bold':True}}})
colwidth(state,{'A':23,'B':20,'C':20,'D':18,'E':20,'F':20})

# Monthly trend
months=REFERENCE['months']
title(monthly,'MONTHLY SALES & PROFIT','Observed sales and realized profit by month; 2014–2017 historical sample.',last='H')
table_header(monthly,5,['Month','Sales ($)','Profit ($)','Margin %'])
cells(monthly,'A6:D53',[[x['name'],x['sales'],x['profit'],None] for x in months])
for i in range(6,54):monthly.get_range(f'D{i}').formulas=[[f'=IFERROR(C{i}/B{i},0)']]
currency(monthly,'B6:C53');percentage(monthly,'D6:D53')
colwidth(monthly,{'A':17,'B':19,'C':19,'D':17,'E':13,'F':14,'G':14})
mc=monthly.charts.add('line',{'title':'Monthly revenue trend','has_legend':False})
se=mc.series.add('Sales ($)');se.category_formula="'Monthly Trend'!$A$6:$A$53";se.formula="'Monthly Trend'!$B$6:$B$53"
mc.set_position('F5','O20')

# Executive summary (formula-backed KPIs)
title(summary,'RETAIL PROFITABILITY INTELLIGENCE','Executive overview | Historical Superstore sample · retail margin diagnostics',last='J')
for c,lab in [('A','NET SALES'),('C','REALIZED PROFIT'),('E','MARGIN'),('G','UNIQUE ORDERS'),('I','LOSS LINES')]:
 summary.get_range(f'{c}5').values=[[lab]];summary.get_range(f'{c}5').format={'fill':PALE,'font':{'bold':True,'size':10,'color':GRAY},'row_height':22}
summary.get_range('A6').formulas=[["='Regional Performance'!B10"]]
summary.get_range('C6').formulas=[["='Regional Performance'!C10"]]
summary.get_range('E6').formulas=[['=IFERROR(C6/A6,0)']]
summary.get_range('G6').formulas=[["='Regional Performance'!G10"]]
summary.get_range('I6').values=[[REFERENCE['loss_lines']]]
for c in ['A','C','E','G','I']:summary.get_range(f'{c}6').format={'font':{'bold':True,'size':19,'color':INK},'row_height':40}
currency(summary,'A6');currency(summary,'C6');percentage(summary,'E6')
summary.get_range('A9').values=[['BUSINESS FINDINGS']];summary.get_range('A9:J9').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':26}
summary.merge_cells('A10:J10');summary.get_range('A10').values=[['Central region: 7.9% margin, versus West at 14.9%; inspect discounting and product mix before changing prices.']]
summary.merge_cells('A11:J11');summary.get_range('A11').values=[['Tables produced $206.97K in sales but -$17.73K realized profit across the sample.']]
summary.merge_cells('A12:J12');summary.get_range('A12').values=[['Texas shows -$25.73K realized profit despite $170.19K in sales; a priority for diagnostic review.']]
summary.merge_cells('A13:J13');summary.get_range('A13').values=[['These observational associations are not causal proof or a validated ROI forecast.']]
summary.get_range('A10:J13').format={'row_height':28,'font':{'size':11,'color':INK},'wrap_text':True}
summary.get_range('A16').values=[['MONITORING VIEW']]
summary.get_range('A16:J16').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':26}
summary_chart=summary.charts.add('bar',{'title':'Regional profit contribution','has_legend':False})
se=summary_chart.series.add('Profit ($)');se.category_formula="'Regional Performance'!$A$6:$A$9";se.formula="'Regional Performance'!$C$6:$C$9"
summary_chart.set_position('A18','F33')
summary_chart2=summary.charts.add('line',{'title':'Sales trend by month','has_legend':False})
se=summary_chart2.series.add('Sales ($)');se.category_formula="'Monthly Trend'!$A$6:$A$53";se.formula="'Monthly Trend'!$B$6:$B$53"
summary_chart2.set_position('G18','N33')
colwidth(summary,{'A':20,'B':4,'C':21,'D':4,'E':18,'F':4,'G':20,'H':4,'I':19,'J':20,'K':16,'L':16,'M':16,'N':16})

# What-if model: assumptions colored to signal user-controlled inputs.
title(scenario,'MARGIN RECOVERY | SCENARIO MODEL','Sensitivity test, not a forecast: hypothetical recoverable portion of negative line profits.',last='H')
scenario.get_range('A5:B8').values=[['Assumption','Value'],['Negative profit-line exposure ($)',REFERENCE['negative_profit_exposure']],['Assumed recoverable share',0.25],['Estimated program cost ($)',5000]]
scenario.get_range('A5:B5').format={'fill':TEAL,'font':{'bold':True,'color':WHITE},'row_height':25}
scenario.get_range('A7:B8').format={'fill':'#E8F3FF','font':{'color':'#23548B'},'row_height':26}
scenario.get_range('A10:B13').values=[['Scenario output','Formula'],['Hypothetical gross recovery',None],['Assumed net profit change',None],['Illustrative adjusted net margin',None]]
scenario.get_range('A10:B10').format={'fill':NAVY,'font':{'bold':True,'color':WHITE}}
scenario.get_range('B11').formulas=[['=B6*B7']]
scenario.get_range('B12').formulas=[['=B11-B8']]
scenario.get_range('B13').formulas=[["=('Regional Performance'!$C$10+B12)/'Regional Performance'!$B$10"]]
currency(scenario,'B6');currency(scenario,'B8');percentage(scenario,'B7');currency(scenario,'B11:B12');percentage(scenario,'B13')
scenario.merge_cells('A16:H17')
scenario.get_range('A16').values=[['Scenario assumes recovery of a chosen fraction of negative profit-line amounts, unchanged sales volume and unaffected positive-profit lines. No causal effect has been established.']]
scenario.get_range('A16:H17').format={'fill':LIGHT,'wrap_text':True,'font':{'size':10,'color':GRAY},'row_height':28}
colwidth(scenario,{'A':39,'B':24,'C':14,'D':14,'E':14,'F':14,'G':14,'H':14})

# Source/citation and guardrails
title(notes,'SOURCE AND ANALYTICAL DEFINITIONS','Sample data / data rights / calculation boundaries',last='H')
texts=[('Dataset','Tableau Sample — Superstore (fictional retail records)'),
('Publisher','Tableau / Salesforce, available as Tableau Public sample data'),
('Official link','https://public.tableau.com/app/resources/sample-data'),
('Download source used for reproducibility','https://github.com/mohamednsafi/superstore-sales-analysis/blob/main/data/raw/Sample_Superstore.csv'),
('Row grain','One record is an order line (not an order or customer).'),
('Net sales','SUM(Sales) across lines'),('Realized profit','SUM(Profit) across lines'),
('Profit margin','SUM(Profit) / SUM(Sales) (sales-weighted), not mean of line margins'),
('Average discount','Simple line-level mean of Discount; NOT weighted by revenue'),
('Orders','COUNTD(Order ID); do not sum order counts across multiple overlapping dimensions'),
('Loss exposure','SUM(ABS(Profit)) for negative-profit lines; not a revenue loss prediction'),
('Time coverage','2014-01 through 2017-12 in this archived CSV version'),
('Limitations','Fictitious sample. No customer acquisition cost, returns, inventory or causal intervention data.'),
('Workbook scope','Fixed reference snapshot; regenerated CSV outputs are produced separately by the Python pipeline.')]
notes.get_range('A5:B18').values=[list(t) for t in texts]
notes.get_range('A5:A18').format={'fill':LIGHT,'font':{'bold':True,'color':INK},'row_height':25}
notes.get_range('B5:B18').format={'font':{'color':INK,'size':10},'wrap_text':True,'row_height':26}
colwidth(notes,{'A':39,'B':96,'C':12,'D':12})

# Display verification before export
print('Sheets',wb.inspect({'kind':'sheet','include':'id,name'}).ndjson[:700])
print('Preview',wb.inspect({'kind':'table','range':'Regional Performance!A5:G10','include':'values,formulas','table_max_rows':7,'table_max_cols':7}).ndjson[:1200])
print('Errors',wb.inspect({'kind':'match','search_term':'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A','options':{'use_regex':True,'max_results':30}}).ndjson[:500])
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
SpreadsheetFile.export_xlsx(wb).save(str(OUTPUT))
print('Exported',OUTPUT,OUTPUT.stat().st_size)
