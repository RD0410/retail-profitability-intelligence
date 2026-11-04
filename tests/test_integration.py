import csv
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from src.pipeline import REQUIRED, build

class IntegrationTests(unittest.TestCase):
    def test_fixture_to_sql_csv_and_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('sql','dashboards'):
                (root/folder).mkdir()
            origin=Path(__file__).resolve().parents[1]
            for f in ('01_schema.sql','02_analysis_views.sql'):
                shutil.copy(origin/'sql'/f,root/'sql'/f)
            shutil.copy(origin/'dashboards/dashboard_template.html',root/'dashboards/dashboard_template.html')
            raw=root/'data/raw/superstore_fixture.csv'; raw.parent.mkdir(parents=True)
            first={'Row ID':'1','Order ID':'O-001','Order Date':'1/1/2017','Ship Date':'1/3/2017','Ship Mode':'Standard Class',
                   'Customer ID':'C-001','Segment':'Consumer','State':'Texas','Region':'Central',
                   'Product ID':'P-001','Category':'Furniture','Sub-Category':'Tables',
                   'Sales':'100','Quantity':'2','Discount':'0.30','Profit':'-20'}
            second=dict(first,**{'Row ID':'2','Order ID':'O-002','Sales':'200','Profit':'50','Discount':'0.00','State':'California','Region':'West'})
            with raw.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(first));writer.writeheader();writer.writerows([first,second])
            m=build(root,source=str(raw),enforce_reference=False)
            self.assertEqual(m['lines'],2)
            self.assertEqual(m['orders'],2)
            self.assertEqual(m['sales'],300)
            self.assertEqual(m['profit'],30)
            with sqlite3.connect(root/'data/processed/retail_profitability.db') as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM v_state_risk').fetchone()[0],2)
                self.assertEqual(db.execute('SELECT ROUND(SUM(profit),2) FROM sales_lines').fetchone()[0],30)
            self.assertTrue((root/'tableau/monthly_trend.csv').exists())
            dashboard=(root/'dashboards/retail_profitability_dashboard.html').read_text()
            self.assertIn('const ROW_DATA = [[',dashboard)
            self.assertNotIn('/*__ROW_DATA__*/',dashboard)
            self.assertNotIn('__SNAPSHOT_JSON__',dashboard)
            self.assertIn('Central',dashboard)

if __name__=='__main__': unittest.main()
