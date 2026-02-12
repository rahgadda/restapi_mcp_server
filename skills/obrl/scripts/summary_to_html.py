#!/usr/bin/env python3
import re, html, datetime, argparse, json
from pathlib import Path

def parse_md_table(md_text: str):
    lines = [l.strip() for l in md_text.splitlines() if l.strip().startswith('|')]
    rows = []
    for l in lines:
        cells = [c.strip() for c in l.strip('|').split('|')]
        # skip separator rows (----)
        if all(re.fullmatch(r'-+', c.replace(' ', '')) for c in cells):
            continue
        rows.append(cells)
    header = rows[0] if rows else []
    data = rows[1:] if len(rows) > 1 else []
    return header, data

def render_html(header, data, ts_label: str) -> str:
    head_html = '<tr>' + ''.join(
        f'<th data-col="{i}" tabindex="0" role="columnheader" aria-sort="none">{html.escape(c)}<span class="sort-indicator"></span></th>'
        for i,c in enumerate(header)
    ) + '</tr>' if header else ''
    body_html = '\n'.join('<tr>' + ''.join(f'<td data-col="{header[idx] if idx < len(header) else idx}">{html.escape(c)}</td>' for idx,c in enumerate(r)) + '</tr>' for r in data)
    column_options = ''.join(f'<option value="{i}">{html.escape(c)}</option>' for i,c in enumerate(header))
    status_counts = {}
    status_col = len(header) - 1 if header else -1
    if status_col >= 0:
        for row in data:
            key = row[status_col].strip().upper()
            status_counts[key] = status_counts.get(key, 0) + 1
    stats_raw = json.dumps(status_counts)
    stats_json = stats_raw.replace('\\', '\\\\').replace("'", r"\'")
    # Use placeholder substitution to avoid brace escaping issues with str.format
    TEMPLATE = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OBRL Run Summary %%TS%%</title>
  <style>
    :root {
      color-scheme:light dark;
      --bg:#f7f8fb; --panel:#ffffff; --panel-alt:#f1f4ff; --text:#0f172a; --muted:#475569; --accent:#2563eb;
      --success:#16a34a; --error:#dc2626; --warning:#d97706; --skipped:#6366f1;
      --border:#d0d8ea; --stripe:#f5f7ff;
    }
    :root[data-theme="dark"] {
      --bg:#05060a; --panel:#10131c; --panel-alt:#171b28; --text:#f3f4f6; --muted:#9ba3b4; --accent:#4da3ff;
      --success:#22c55e; --error:#ef4444; --warning:#f59e0b; --skipped:#818cf8;
      --border:#1f2433; --stripe:#0c101b;
    }
    * { box-sizing:border-box; }
    html,body { background:var(--bg); color:var(--text); font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; margin:0; }
    body { padding:32px 0; }
    .wrap { max-width:1200px; margin:0 auto; padding:0 20px 64px; }
    header { display:flex; flex-direction:column; gap:12px; margin-bottom:24px; }
    .header-top { display:flex; justify-content:space-between; gap:16px; align-items:center; flex-wrap:wrap; }
    header h1 { font-size:28px; margin:0; font-weight:600; }
    header .meta { color:var(--muted); font-size:14px; }
    .theme-toggle { display:flex; align-items:center; gap:8px; font-size:14px; color:var(--muted); }
    .switch { position:relative; display:inline-block; width:46px; height:24px; }
    .switch input { opacity:0; width:0; height:0; }
    .slider { position:absolute; cursor:pointer; top:0; left:0; right:0; bottom:0; background:var(--border); transition:.3s; border-radius:24px; }
    .slider:before { position:absolute; content:""; height:18px; width:18px; left:4px; bottom:3px; background:white; border-radius:50%; transition:.3s; }
    input:checked + .slider { background:var(--accent); }
    input:checked + .slider:before { transform:translateX(20px); }
    .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px; }
    .card { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:14px 16px; display:flex; flex-direction:column; gap:4px; }
    .card small { text-transform:uppercase; letter-spacing:.08em; font-size:11px; color:var(--muted); }
    .card strong { font-size:24px; font-weight:600; }
    .card.success { border-color:rgba(34,197,94,.4); }
    .card.error { border-color:rgba(239,68,68,.4); }
    .card.warning { border-color:rgba(245,158,11,.4); }
    .card.skipped { border-color:rgba(129,140,248,.4); }
    .controls { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:16px; display:flex; flex-wrap:wrap; gap:16px; align-items:center; margin-bottom:20px; }
    .controls label { font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
    .controls input[type=text], .controls select {
      background:var(--panel-alt); color:var(--text); border:1px solid var(--border); border-radius:8px; padding:10px 12px; min-width:200px;
    }
    .controls input[type=text]::placeholder { color:var(--muted); }
    .table-wrap { background:var(--panel); border:1px solid var(--border); border-radius:16px; box-shadow:0 20px 45px rgba(0,0,0,.35); overflow:hidden; }
    table { width:100%; border-collapse:collapse; font-size:14px; }
    thead th { background:var(--panel-alt); padding:12px 14px; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:2; cursor:pointer; user-select:none; }
    tbody td { padding:12px 14px; border-bottom:1px solid rgba(255,255,255,.05); }
    tbody tr:nth-child(odd) { background:var(--stripe); }
    tbody tr:hover { background:rgba(77,163,255,.08); }
    .sort-indicator { margin-left:6px; opacity:.5; font-size:11px; }
    th[aria-sort="ascending"] .sort-indicator::after { content:'\u2191'; color:var(--accent); }
    th[aria-sort="descending"] .sort-indicator::after { content:'\u2193'; color:var(--accent); }
    th[aria-sort="none"] .sort-indicator::after { content:'\u2195'; color:var(--muted); }
    .badge { padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:6px; }
    .badge::before { content:''; width:8px; height:8px; border-radius:50%; display:inline-block; }
    .badge.success { background:rgba(34,197,94,.15); color:var(--success); border:1px solid rgba(34,197,94,.4); }
    .badge.success::before { background:var(--success); }
    .badge.failed,.badge.error { background:rgba(239,68,68,.15); color:var(--error); border:1px solid rgba(239,68,68,.4); }
    .badge.failed::before,.badge.error::before { background:var(--error); }
    .badge.warning { background:rgba(245,158,11,.18); color:var(--warning); border:1px solid rgba(245,158,11,.4); }
    .badge.warning::before { background:var(--warning); }
    .badge.skipped { background:rgba(129,140,248,.2); color:var(--skipped); border:1px solid rgba(129,140,248,.4); }
    .badge.skipped::before { background:var(--skipped); }
    .empty { text-align:center; padding:32px; color:var(--muted); }
    @media (max-width:720px){
      header h1 { font-size:24px; }
      .controls { flex-direction:column; align-items:flex-start; }
      .controls input[type=text], .controls select { width:100%; }
      table { font-size:13px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="header-top">
        <h1>OBRL Execution Report</h1>
        <div class="theme-toggle">
          <span>Dark mode</span>
          <label class="switch">
            <input id="themeSwitch" type="checkbox">
            <span class="slider"></span>
          </label>
        </div>
      </div>
      <div class="meta">Generated: <strong>%%TS%%</strong></div>
    </header>
    <section class="cards" aria-label="Status summary">
      <div class="card success"><small>Total Steps</small><strong id="totalSteps">0</strong></div>
      <div class="card success"><small>Success</small><strong id="statSuccess">0</strong></div>
      <div class="card error"><small>Failed/Error</small><strong id="statFail">0</strong></div>
      <div class="card skipped"><small>Skipped</small><strong id="statSkip">0</strong></div>
    </section>
    <div class="controls" aria-label="Table controls">
      <div>
        <label for="q">Search</label>
        <input id="q" type="text" placeholder="Filter rows (search all columns)…">
      </div>
      <div>
        <label for="status">Status</label>
        <select id="status"><option value="">All Statuses</option></select>
      </div>
      <div>
        <label for="column">Column</label>
        <select id="column"><option value="">All Columns</option>%%COLS%%</select>
      </div>
    </div>
    <div class="table-wrap">
      <table id="tbl" role="table" aria-label="OBRL Run Summary">
        <thead>%%HEAD%%</thead>
        <tbody>
        %%BODY%%
        </tbody>
      </table>
      <div class="empty" id="emptyState" hidden>No rows match the current filters.</div>
    </div>
  </div>
  <script>
  (function(){
    const tbl=document.getElementById('tbl');
    const tbody=tbl.querySelector('tbody');
    const headers=Array.from(tbl.querySelectorAll('thead th'));
    const q=document.getElementById('q');
    const status=document.getElementById('status');
    const column=document.getElementById('column');
    const emptyState=document.getElementById('emptyState');
    const stats=JSON.parse('%%STATS%%');
    const totalSteps=document.getElementById('totalSteps');
    const statSuccess=document.getElementById('statSuccess');
    const statFail=document.getElementById('statFail');
    const statSkip=document.getElementById('statSkip');
    totalSteps.textContent=tbody.rows.length;
    statSuccess.textContent=(stats.SUCCESS||0)+(stats.OK||0);
    statFail.textContent=(stats.FAILED||0)+(stats.ERROR||0);
    statSkip.textContent=(stats.SKIPPED||0)+(stats.WARNING||0);
    const statuses=new Set(Array.from(tbody.querySelectorAll('tr')).map(r=>(r.cells[r.cells.length-1].textContent||'').trim()));
    Array.from(statuses).filter(Boolean).sort().forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;status.appendChild(o);});
    function matchesFilter(row){
      const cells=Array.from(row.cells).map(c=>c.textContent.toLowerCase());
      const txt=q.value.trim().toLowerCase();
      const colIdx=column.value===''?null:parseInt(column.value,10);
      const st=status.value.trim();
      let hit=true;
      if(txt){hit=colIdx===null?cells.some(v=>v.includes(txt)):(cells[colIdx]||'').includes(txt);}
      if(hit&&st){const cur=(cells[cells.length-1]||'').toUpperCase();hit=cur===st.toUpperCase();}
      return hit;
    }
    function applyFilter(){
      let visible=0;
      Array.from(tbody.rows).forEach(r=>{
        const show=matchesFilter(r);
        r.style.display=show?'':'none';
        if(show) visible+=1;
      });
      emptyState.hidden=visible!==0;
    }
    q.addEventListener('input',applyFilter);status.addEventListener('change',applyFilter);column.addEventListener('change',applyFilter);
    function getCellValue(row,idx){const v=row.cells[idx]?.textContent||'';return v.trim();}
    function isNumericColumn(idx){return idx===0;}
    function sortBy(idx){
      const current=headers[idx].getAttribute('aria-sort');
      const next=current==='ascending'?'descending':'ascending';
      headers.forEach(h=>h.setAttribute('aria-sort','none'));
      headers[idx].setAttribute('aria-sort',next);
      const rows=Array.from(tbody.rows).filter(r=>r.style.display!=='none');
      const dir=next==='ascending'?1:-1;
      rows.sort((a,b)=>{
        const va=getCellValue(a,idx);const vb=getCellValue(b,idx);
        if(isNumericColumn(idx)){const na=parseFloat(va)||0, nb=parseFloat(vb)||0;return (na-nb)*dir;}
        return va.localeCompare(vb,undefined,{numeric:true,sensitivity:'base'})*dir;});
      rows.forEach(r=>tbody.appendChild(r));
    }
    headers.forEach((h,i)=>{h.addEventListener('click',()=>sortBy(i));h.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();sortBy(i);}});});
    const statusClassMap={
      'SUCCESS':'success','OK':'success','FAILED':'failed','ERROR':'error','WARNING':'warning','SKIPPED':'skipped'
    };
    Array.from(tbody.rows).forEach(r=>{
      const c=r.cells[r.cells.length-1];
      const val=c.textContent.trim();
      const cls=statusClassMap[val.toUpperCase()]||'warning';
      c.innerHTML='<span class="badge '+cls+'">'+val+'</span>';
    });
    const switchEl=document.getElementById('themeSwitch');
    const root=document.documentElement;
    const stored=localStorage.getItem('obrl-theme');
    if(stored==='dark'){root.dataset.theme='dark';switchEl.checked=true;} else {root.dataset.theme='light';}
    switchEl.addEventListener('change',()=>{
      const next=switchEl.checked?'dark':'light';
      root.dataset.theme=next;
      localStorage.setItem('obrl-theme',next);
    });
  })();
  </script>
</body>
</html>'''
    html_doc = TEMPLATE.replace('%%TS%%', html.escape(ts_label)) \
                       .replace('%%HEAD%%', head_html) \
                       .replace('%%BODY%%', body_html) \
                       .replace('%%COLS%%', column_options) \
                       .replace('%%STATS%%', stats_json)
    return html_doc

def main():
    ap = argparse.ArgumentParser(description='Convert summary.md to interactive summary.html with sorting/filtering')
    ap.add_argument('--dir', default='.', help='Directory containing summary.md (default: current)')
    args = ap.parse_args()
    base = Path(args.dir)
    md_path = base / 'summary.md'
    md_text = md_path.read_text()
    header, data = parse_md_table(md_text)
    ts_label = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    html_doc = render_html(header, data, ts_label)
    # Always overwrite formatted.html inside the target directory
    out = base / 'formatted.html'
    out.write_text(html_doc)
    print(str(out))

if __name__ == '__main__':
    main()