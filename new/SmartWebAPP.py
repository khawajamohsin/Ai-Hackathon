"""Smart Bus Reservation - website. Run in IDLE with F5.
Starts a small web server on your own computer and opens the site in your browser.
Stop it with Shell > Restart Shell (Ctrl+F6) or by closing the IDLE Shell window.
Data is kept in the browser page only: refreshing the page resets everything."""
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Smart Bus Reservation</title>
<style>
:root{--bg:#f4f7fb;--card:#fff;--tx:#1a2230;--mu:#64708a;--ac:#1d6fe8;--ok:#12805c;--bad:#c0392b;--bd:#e2e8f0;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0e131b;--card:#171e2a;--tx:#e8edf5;--mu:#98a2b8;--ac:#5b9bff;--ok:#3ecf9a;--bad:#ff7b6b;--bd:#28313f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0e131b;--card:#171e2a;--tx:#e8edf5;--mu:#98a2b8;--ac:#5b9bff;--ok:#3ecf9a;--bad:#ff7b6b;--bd:#28313f;color-scheme:dark}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--ac);color:#fff;padding:18px 16px;text-align:center}
header h1{margin:0;font-size:1.3rem}header p{margin:2px 0 0;opacity:.85;font-size:.85rem}
nav{display:flex;gap:6px;overflow-x:auto;padding:10px 12px;background:var(--card);border-bottom:1px solid var(--bd);position:sticky;top:0}
nav button{flex:none;border:1px solid var(--bd);background:var(--bg);color:var(--tx);padding:9px 14px;border-radius:20px;font:inherit;cursor:pointer}
nav button.on{background:var(--ac);color:#fff;border-color:var(--ac)}
main{max-width:760px;margin:0 auto;padding:14px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;margin-bottom:10px}
.row{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center}
.mu{color:var(--mu);font-size:.9rem}b.id{color:var(--ac)}
.badge{padding:2px 10px;border-radius:12px;font-size:.78rem;font-weight:600;border:1px solid currentColor}
.Available,.Confirmed{color:var(--ok)}.Partially{color:#b7791f}.Full,.Cancelled{color:var(--bad)}
input,select{width:100%;padding:11px;margin:4px 0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--bg);color:var(--tx);font:inherit}
label{font-size:.9rem;font-weight:600}
.btn{background:var(--ac);color:#fff;border:0;padding:12px 18px;border-radius:8px;font:inherit;font-weight:600;cursor:pointer;width:100%}
.btn.s{width:auto;padding:8px 14px;background:var(--bad)}
.msg{padding:12px;border-radius:8px;margin-bottom:12px;border:1px solid}.msg.ok{color:var(--ok)}.msg.err{color:var(--bad)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.stat b{display:block;font-size:1.4rem}
</style></head><body>
<header><h1>🚌 Smart Bus Reservation</h1><p>Browse routes, book seats, cancel, and view reports</p></header>
<nav id="nav"></nav><main id="view"></main>
<script>
const CITIES=["Karachi","Hyderabad","Sukkur","Mirpur Khas","Lahore"];
const routes=[["R101","Karachi","Hyderabad","08:00 AM",1200,40],["R102","Karachi","Sukkur","09:30 AM",2000,36],
["R103","Hyderabad","Mirpur Khas","11:00 AM",800,32],["R104","Karachi","Lahore","07:00 PM",5000,45],
["R105","Sukkur","Hyderabad","02:00 PM",1500,30]].map(([id,from,to,time,price,total])=>({id,from,to,time,price,total,left:total}));
const bookings=[];let nextId=1001,tab="Routes",msg=null,onlySeats=false,term="";
const TABS=["Routes","Search","Book","My Bookings","Report"];
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const st=r=>!r.left?["Fully Booked","Full"]:r.left==r.total?["Available","Available"]:["Partially Booked","Partially"];
const money=n=>"Rs. "+n.toLocaleString();
const byId=id=>routes.find(r=>r.id==id.trim().toUpperCase());
const posInt=v=>/^\d+$/.test(v.trim())&&+v>0?+v:null;
const routeCard=r=>{const[s,c]=st(r);return`<div class="card"><div class="row"><span><b class="id">${r.id}</b> ${r.from} → ${r.to}</span><span class="badge ${c}">${s}</span></div>
<div class="mu">${r.time} · ${money(r.price)} per seat · ${r.left}/${r.total} seats free</div></div>`};

function go(t){tab=t;msg=null;render()}
function book(){
  const name=$name.value.trim(),age=posInt($age.value),r=byId($route.value),seats=posInt($seats.value);
  const err=!name?"Name cannot be empty.":!age?"Age must be a positive whole number.":!seats?"Seats must be a positive whole number.":
    seats>r.left?`Only ${r.left} seat(s) available.`:null;
  if(err)msg={t:"err",h:"Booking rejected: "+err};
  else{const b={id:"B"+nextId++,name,age,route:r,seats,fare:r.price*seats,status:"Confirmed"};
    bookings.push(b);r.left-=seats;
    msg={t:"ok",h:`<b>Booking confirmed!</b><br>ID ${b.id} · ${esc(name)} · ${r.id} (${r.from} → ${r.to})<br>${seats} seat(s) × ${money(r.price)} = <b>${money(b.fare)}</b>`}}
  render()}
function cancel(id){
  const b=bookings.find(x=>x.id==id);
  if(b&&b.status=="Confirmed"){b.route.left+=b.seats;b.status="Cancelled";
    msg={t:"ok",h:`Booking ${id} cancelled. ${b.seats} seat(s) restored to ${b.route.id} (now ${b.route.left}).`}}
  render()}

const views={
Routes:()=>`<label><input type="checkbox" style="width:auto;margin:0 8px 12px 0" ${onlySeats?"checked":""} onchange="onlySeats=this.checked;render()">Only routes with seats</label>`
  +routes.filter(r=>!onlySeats||r.left).map(routeCard).join(""),
Search:()=>{const t=term.trim().toLowerCase();
  const hits=!t?[]:routes.filter(r=>r.id.toLowerCase()==t||r.from.toLowerCase()==t||r.to.toLowerCase()==t);
  return`<label>Route ID or city</label><input id="q" value="${esc(term)}" placeholder="e.g. R101 or Hyderabad" oninput="term=this.value;render(true)">`
  +(!t?`<p class="mu">Type a route ID or city name.</p>`:hits.map(routeCard).join("")||`<p class="mu">No routes found for “${esc(term.trim())}”.</p>`)},
Book:()=>(msg?`<div class="msg ${msg.t}">${msg.h}</div>`:"")+`<div class="card"><label>Passenger name</label><input id="$name" autocomplete="off">
<label>Age</label><input id="$age" inputmode="numeric"><label>Route</label>
<select id="$route">${routes.map(r=>`<option value="${r.id}">${r.id} · ${r.from} → ${r.to} (${r.left} free)</option>`).join("")}</select>
<label>Number of seats</label><input id="$seats" inputmode="numeric"><button class="btn" onclick="book()">Book ticket</button></div>`,
"My Bookings":()=>(msg?`<div class="msg ${msg.t}">${msg.h}</div>`:"")+(bookings.map(b=>`<div class="card"><div class="row"><span><b class="id">${b.id}</b> ${esc(b.name)}</span>
<span class="badge ${b.status}">${b.status}</span></div><div class="mu">${b.route.id} · ${b.seats} seat(s) · ${money(b.fare)}</div>
${b.status=="Confirmed"?`<button class="btn s" onclick="cancel('${b.id}')">Cancel booking</button>`:""}</div>`).join("")||`<p class="mu">No bookings found.</p>`),
Report:()=>{const ok=bookings.filter(b=>b.status=="Confirmed");
  const stat=(l,v)=>`<div class="card stat"><span class="mu">${l}</span><b>${v}</b></div>`;
  return`<div class="stats">${stat("Total bookings",bookings.length)}${stat("Confirmed",ok.length)}${stat("Cancelled",bookings.length-ok.length)}
${stat("Seats reserved",ok.reduce((s,b)=>s+b.seats,0))}${stat("Confirmed revenue",money(ok.reduce((s,b)=>s+b.fare,0)))}${stat("Fully booked routes",routes.filter(r=>!r.left).length)}</div>
<h3>Schedule by departure city</h3>`+CITIES.map(c=>{const d=routes.filter(r=>r.from==c);
  return`<div class="card"><b>${c}</b>${d.map(r=>`<div class="mu">${r.id} → ${r.to} | ${r.time}</div>`).join("")||`<div class="mu">No scheduled departures.</div>`}</div>`}).join("")}
};
function render(keep){
  $nav.innerHTML=TABS.map(t=>`<button class="${t==tab?"on":""}" onclick="go('${t}')">${t}</button>`).join("");
  $view.innerHTML=views[tab]();
  if(keep){const q=document.getElementById("q");q.focus();q.setSelectionRange(q.value.length,q.value.length)}}
const $nav=document.getElementById("nav"),$view=document.getElementById("view");
render();
</script></body></html>
'''.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, *args):  # keep the Shell quiet
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)  # port 0 = any free port
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"Smart Bus website running at {url}\nPress Ctrl+C or restart the Shell to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
