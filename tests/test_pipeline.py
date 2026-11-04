import csv
from pathlib import Path
import tempfile
import unittest
from decimal import Decimal
from src.pipeline import clean_rows,date_value,group_rows,metrics,validate_reference

BASE={'Row ID':'1','Order ID':'A-001','Order Date':'1/1/2017','Ship Date':'1/3/2017',
      'Ship Mode':'Standard','Customer ID':'C1','Segment':'Consumer','State':'Texas',
      'Region':'Central','Product ID':'P1','Category':'Furniture','Sub-Category':'Tables',
      'Sales':'100','Quantity':'2','Discount':'0.30','Profit':'-20'}
class PipelineTests(unittest.TestCase):
 def make_csv(self,entries):
  f=tempfile.NamedTemporaryFile(mode='w',newline='',suffix='.csv',delete=False)
  writer=csv.DictWriter(f,fieldnames=list(BASE));writer.writeheader();writer.writerows(entries);f.close()
  self.addCleanup(lambda:Path(f.name).unlink(missing_ok=True));return Path(f.name)
 def test_clean_and_metrics(self):
  a=dict(BASE);b=dict(BASE,**{'Row ID':'2','Order ID':'A-001','Sales':'50','Profit':'10','Discount':'0.10'})
  rows=clean_rows(self.make_csv([a,b]));m=metrics(rows)
  self.assertEqual((m['lines'],m['orders'],m['customers']),(2,1,1))
  self.assertEqual((m['sales'],m['profit']), (150,-10))
  self.assertEqual(m['loss_lines'],1)
 def test_group_weighted_margin(self):
  a=dict(BASE);b=dict(BASE,**{'Row ID':'2','Sales':'900','Profit':'180','Order ID':'A-002'})
  rows=clean_rows(self.make_csv([a,b]));g=group_rows(rows,['region'])
  self.assertEqual(g[0]['sales'],1000);self.assertEqual(g[0]['profit'],160)
  self.assertEqual(g[0]['margin'],.16)
 def test_duplicate_id_rejected(self):
  with self.assertRaisesRegex(ValueError,'Duplicate'):
   clean_rows(self.make_csv([BASE,BASE]))
 def test_invalid_discount_rejected(self):
  with self.assertRaisesRegex(ValueError,'Out-of-range'):
   clean_rows(self.make_csv([dict(BASE, Discount='1.1')]))
 def test_ship_date_precedes_order_rejected(self):
  with self.assertRaisesRegex(ValueError,'Ship date'):
   clean_rows(self.make_csv([dict(BASE, **{'Ship Date':'12/31/2016'})]))
 def test_missing_columns_rejected(self):
  path=self.make_csv([BASE]);text=path.read_text().replace('Sub-Category,','Missing_Column,')
  path.write_text(text)
  with self.assertRaisesRegex(ValueError,'Missing source columns'):clean_rows(path)
 def test_reference_check_rejects_wrong_data(self):
  with self.assertRaisesRegex(ValueError,'Unexpected source'):
   validate_reference({'lines':2,'orders':1,'customers':1,'sales':150,'profit':10})
 def test_iso_date(self):self.assertEqual(date_value('11/8/2016'),'2016-11-08')
if __name__=='__main__':unittest.main()
