"""Validate Tableau's fictitious Superstore sample and build a local analytics mart.

Only Python standard library is required. The published data file is retrieved
on demand rather than redistributed in this project.
"""
from __future__ import annotations

import argparse
import csv
import io
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json
import sqlite3
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = ('https://raw.githubusercontent.com/mohamednsafi/'
              'superstore-sales-analysis/main/data/raw/Sample_Superstore.csv')
REQUIRED = {'Row ID','Order ID','Order Date','Ship Date','Ship Mode', 'Customer ID',
            'Segment','State','Region','Product ID','Category','Sub-Category',
            'Sales','Quantity','Discount','Profit'}
EXPECTED = {'rows':9994, 'orders':5009, 'customers':793,
            'sales': Decimal('2297200.86'), 'profit': Decimal('286397.02')}
FIELDNAMES = ['row_id','order_id','order_date','ship_date','ship_mode','customer_id',
              'segment','state','region','product_id','category','subcategory',
              'sales','quantity','discount','profit','year','month','margin',
              'discount_band','loss_flag']


def source_path(local_path: str | None, download: bool = True, root: Path = ROOT) -> Path:
    path = Path(local_path).expanduser() if local_path else root/'data/raw/Sample_Superstore.csv'
    if path.exists():
        return path
    if not download:
        raise FileNotFoundError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(SOURCE_URL, path)
    except Exception as e:
        raise RuntimeError(f'Cannot retrieve source CSV: {SOURCE_URL}. Download it manually and use --source PATH. {e}') from e
    return path


def date_value(raw: str) -> str:
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.strptime(raw.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f'Invalid order/ship date {raw!r}')


def clean_rows(source: Path):
    rows=[]; seen_ids=set()
    # Some published Superstore CSV copies contain Windows-1252 bytes
    # (for example, 0xA0 for a non-breaking space in product descriptions).
    # Prefer UTF-8 and fall back to Windows-1252 without discarding data.
    raw = source.read_bytes()
    try:
        decoded = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        decoded = raw.decode('cp1252')
    with io.StringIO(decoded, newline='') as f:
        reader=csv.DictReader(f)
        fields=set(reader.fieldnames or [])
        if not REQUIRED.issubset(fields):
            raise ValueError(f'Missing source columns: {sorted(REQUIRED-fields)}')
        for n, r in enumerate(reader, start=2):
            rid=r['Row ID'].strip()
            if not rid or rid in seen_ids: raise ValueError(f'Duplicate/missing Row ID at CSV row {n}: {rid!r}')
            seen_ids.add(rid)
            try:
                sales=Decimal(r['Sales'].strip()); profit=Decimal(r['Profit'].strip())
                disc=Decimal(r['Discount'].strip()); qty=int(r['Quantity'])
            except (InvalidOperation, ValueError) as exc: raise ValueError(f'Invalid amounts in row {n}') from exc
            if not (sales>=0 and Decimal(0)<=disc<=Decimal(1) and qty>0):
                raise ValueError(f'Out-of-range sales, discount or quantity in row {n}')
            order_date=date_value(r['Order Date']); ship_date=date_value(r['Ship Date'])
            if ship_date<order_date: raise ValueError(f'Ship date precedes order in row {n}')
            band=('0%' if disc==0 else '<10%' if disc<Decimal('0.10') else
                  '10–19%' if disc<Decimal('0.20') else '20–29%' if disc<Decimal('0.30') else '30%+')
            rows.append({'row_id':rid,'order_id':r['Order ID'].strip(),
             'order_date':order_date,'ship_date':ship_date,'ship_mode':r['Ship Mode'].strip(),
             'customer_id':r['Customer ID'].strip(),'segment':r['Segment'].strip(),
             'state':r['State'].strip(),'region':r['Region'].strip(),
             'product_id':r['Product ID'].strip(),'category':r['Category'].strip(),
             'subcategory':r['Sub-Category'].strip(),'sales':str(sales),
             'quantity':qty,'discount':str(disc),'profit':str(profit),
             'year':int(order_date[:4]), 'month':order_date[:7],
             'margin':str(profit/sales) if sales else '0',
             'discount_band':band,'loss_flag':int(profit<0)})
    return rows


def metrics(rows):
    sales=sum((Decimal(str(r['sales'])) for r in rows),Decimal(0)); profit=sum((Decimal(str(r['profit'])) for r in rows),Decimal(0))
    return {'lines':len(rows),'orders':len(set(r['order_id'] for r in rows)),
       'customers':len(set(r['customer_id'] for r in rows)),
       'sales':round(float(sales),2),'profit':round(float(profit),2),
       'margin':float(profit/sales) if sales else 0,
       'loss_lines':sum(1 for r in rows if Decimal(str(r['profit']))<0)}


def validate_reference(m):
    if m['lines'] != EXPECTED['rows'] or m['orders'] != EXPECTED['orders'] or m['customers'] != EXPECTED['customers']:
        raise ValueError(f'Unexpected source row/order/customer counts: {m}')
    for field in ('sales','profit'):
        if abs(Decimal(str(m[field])) - EXPECTED[field])>Decimal('0.02'):
            raise ValueError(f'Superstore source value mismatch for {field}: {m[field]}')


def group_rows(rows, keys):
    grouped={}
    for r in rows:
        key=tuple(r[k] for k in keys)
        if key not in grouped:
            grouped[key]={'line_items':0,'orders':set(), 'sales':Decimal(0),'profit':Decimal(0),'discount':Decimal(0),'loss_lines':0}
        x=grouped[key];x['line_items']+=1;x['orders'].add(r['order_id'])
        x['sales']+=Decimal(str(r['sales']));x['profit']+=Decimal(str(r['profit']))
        x['discount']+=Decimal(str(r['discount']));x['loss_lines']+=int(r['loss_flag'])
    result=[]
    for key,v in grouped.items():
        item=dict(zip(keys,key)); item.update({
         'line_items':v['line_items'],'orders':len(v['orders']),
         'sales':round(float(v['sales']),2),'profit':round(float(v['profit']),2),
         'margin':round(float(v['profit']/v['sales']),6) if v['sales'] else 0,
         'avg_discount':round(float(v['discount']/v['line_items']),6),
         'loss_lines':v['loss_lines']})
        result.append(item)
    return sorted(result,key=lambda x:tuple(str(x[k]) for k in keys))


def export_csv(path: Path, rows, columns=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: raise ValueError(f'No data for export {path}')
    cols=columns or list(rows[0])
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(rows)


def build_db(rows, root: Path):
    dest=root/'data/processed/retail_profitability.db'
    schema=(root/'sql/01_schema.sql').read_text()
    views=(root/'sql/02_analysis_views.sql').read_text()
    with sqlite3.connect(dest) as db:
        db.executescript('DROP VIEW IF EXISTS v_discount_performance; DROP VIEW IF EXISTS v_state_risk; DROP VIEW IF EXISTS v_regional_profitability; DROP TABLE IF EXISTS sales_lines;')
        db.executescript(schema)
        fields=['row_id','order_id','order_date','ship_date','ship_mode','customer_id','segment','state','region','product_id','category','subcategory','sales','quantity','discount','profit','year','month','discount_band','loss_flag']
        sql='INSERT INTO sales_lines ('+', '.join(fields)+') VALUES ('+','.join('?' for _ in fields)+')'
        db.executemany(sql,[[r[f] for f in fields] for r in rows]);db.executescript(views)
        m=db.execute('SELECT COUNT(*), ROUND(SUM(sales),2), ROUND(SUM(profit),2) FROM sales_lines').fetchone()
        if m[0]!=len(rows): raise AssertionError('SQLite count mismatch')
        sql_sale=round(sum(float(r['sales']) for r in rows),2)
        if abs(m[1]-sql_sale)>0.02: raise AssertionError('SQLite revenue reconciliation mismatch')
    return dest


def build_html(rows, root):
    # Retail dashboard uses a compact projection rather than customer identifiers.
    slim=[[r['month'],r['region'],r['category'],r['subcategory'],r['segment'],r['state'],
           float(r['sales']),float(r['profit']),float(r['discount']),r['order_id']]
          for r in rows]
    data=json.dumps(slim, separators=(',',':')).replace('</','<\\/')
    template=(root/'dashboards/dashboard_template.html').read_text()
    template=template.replace('__SNAPSHOT_JSON__','null')
    dest=root/'dashboards/retail_profitability_dashboard.html'
    dest.write_text(template.replace('/*__ROW_DATA__*/','const ROW_DATA = '+data+';'),encoding='utf-8')
    return dest


def build(root:Path=ROOT, source:str|None=None, enforce_reference=True):
    raw=source_path(source,root=root)
    rows=clean_rows(raw);m=metrics(rows)
    if enforce_reference:validate_reference(m)
    out=root/'data/processed';out.mkdir(parents=True,exist_ok=True)
    export_csv(out/'retail_clean.csv',rows,FIELDNAMES)
    groups={
      'regional_profitability':('region',),
      'category_profitability':('category',),
      'regional_category':('region','category'),
      'subcategory_profitability':('category','subcategory'),
      'state_risk':('region','state'),
      'discount_performance':('discount_band',),
      'monthly_trend':('month',),
      'regional_monthly_trend':('region','month'),
      'segment_profitability':('segment',),
    }
    for name,keys in groups.items():export_csv(root/f'tableau/{name}.csv',group_rows(rows,list(keys)))
    (out/'metrics.json').write_text(json.dumps(m,indent=2))
    database=build_db(rows,root)
    html=build_html(rows,root)
    print(f"Validated {m['lines']:,} retail order lines across {m['orders']:,} orders; sales ${m['sales']:,.2f}, profit ${m['profit']:,.2f}.")
    print(f'Generated: {html} | {database} | 9 Tableau summary extracts')
    return m


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',help='Local Superstore CSV; otherwise downloads referenced public copy')
    p.add_argument('--allow-alternate',action='store_true',help='Allow a different version of Superstore (no reference total check)')
    args=p.parse_args();build(source=args.source,enforce_reference=not args.allow_alternate)

if __name__=='__main__': main()
