/* Thailand Budget Intelligence front-end. Receives the payload built by utils/payload.py (see app.py). */
window.GovDash={init:function(DATA){
const root=document.getElementById("root"); if(!root||!window.d3) return;
root.innerHTML=`<div id="fit"><div class="stage" id="stage">
  <header>
    <div class="brand">
      <svg viewBox="0 0 24 24" fill="none" stroke="#4cc9ff" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/></svg>
      <div><h1>Thailand Budget Intelligence</h1><div class="sub">แดชบอร์ดวิเคราะห์งบประมาณภาครัฐรายจังหวัด</div></div>
    </div>
    <nav class="nav" role="tablist" aria-label="มุมมอง">
      <button class="pill" role="tab" data-t="1" aria-selected="true">1 · ภาพรวมประเทศ (National)</button>
      <button class="pill" role="tab" data-t="2" aria-selected="false">2 · ภาพรวมจังหวัด (Provincial)</button>
      <button class="pill" role="tab" data-t="3" aria-selected="false">3 · วิเคราะห์ความไม่สอดคล้อง (Mismatch)</button>
    </nav>
    <div class="ctrl">
      <button class="srcbtn" id="srcbtn">ⓘ แหล่งข้อมูล</button>
      <span class="chip"><i class="dot red"></i>แดง = แจ้งเตือนร้องเรียน</span>
      <label for="yr" class="sub">ปี</label><select id="yr"></select>
    </div>
  </header>
  <div class="grid">
    <div class="col" id="L"></div>
    <div class="col">
      <div class="panel mappanel">
        <div class="ph" style="margin-bottom:0"><div class="tabs" role="group" aria-label="ตัวชี้วัดบนแผนที่" id="mtabs"></div><button class="reset" id="reset" hidden>ล้างการเลือก ✕</button></div>
        <div id="note"></div>
        <div class="mapbox">
          <div class="glow-bg"></div>
          <div class="zhint">ลาก = เลื่อน · เลื่อนลูกกลิ้ง = ซูม</div>
          <div class="zc"><button id="zin" aria-label="ซูมเข้า">+</button><button id="zout" aria-label="ซูมออก">−</button><button id="zrs" aria-label="รีเซ็ตมุมมอง" title="รีเซ็ต">⟲</button></div>
          <svg id="map" viewBox="0 0 560 760" preserveAspectRatio="xMidYMid meet" role="img" aria-label="แผนที่ประเทศไทยรายจังหวัด"></svg>
          <div class="tip" id="tip"></div><div class="callout" id="callout" hidden></div>
        </div>
        <div class="legend"><span id="lgMin"></span><i class="lg"></i><span id="lgMax"></span><span style="margin-left:auto;display:flex;gap:6px;align-items:center"><i class="dot red"></i>ร้องเรียนพุ่งสูงสุด 5 อันดับเทียบปีก่อน</span></div>
        <div class="ref" id="mapRef"></div>
      </div>
    </div>
    <div class="col" id="R"></div>
  </div>
</div><div class="modal" id="modal" hidden><div class="mbox" role="dialog" aria-label="แหล่งข้อมูล"><div style="display:flex;justify-content:space-between;align-items:center"><h2>แหล่งข้อมูลที่ใช้ในแดชบอร์ด</h2><button class="reset" id="mclose">ปิด ✕</button></div><div class="sub" id="mmeta"></div><div id="mtable"></div></div></div></div>`;

const $=s=>document.querySelector(s);
const Y=DATA.years, CY=[2020,2021,2022,2023];
const REG={Central:"ภาคกลาง",North:"ภาคเหนือ",Northeast:"ภาคตะวันออกเฉียงเหนือ",South:"ภาคใต้",East:"ภาคตะวันออก",West:"ภาคตะวันตก"};
const DN=DATA.domains, SH={1:"การศึกษา",2:"สาธารณสุข",3:"โครงสร้างพื้นฐาน",4:"เกษตร-สิ่งแวดล้อม",5:"บริหารทั่วไป",6:"เศรษฐกิจ-สังคม"}, SS={1:"ศึกษา",2:"สธ.",3:"โครงสร้าง",4:"เกษตร",5:"บริหาร",6:"เศรษฐกิจ"};
const DCOL={4:"#4cc9ff",5:"#ff3b4e",6:"#3d8bff"};
const fmt=(n,d=0)=>n==null||isNaN(n)?"–":n.toLocaleString("en-US",{maximumFractionDigits:d,minimumFractionDigits:d});
const money=bn=>bn>=1000?[fmt(bn/1000,2),"ล้านล้านบาท"]:[fmt(bn,0),"พันล้านบาท"];
const popu=n=>n>=1e6?[fmt(n/1e6,2),"ล้านคน"]:[fmt(n/1e5,1),"แสนคน"];
const axisCol="rgba(140,170,255,.18)";
const FL=DATA.flags||{}, ANY_SYN=!(FL.budget&&FL.outcome);
const REAL='<span class="badge real">ข้อมูลจริง</span>', SYN=ANY_SYN?'<span class="badge syn">ข้อมูลสังเคราะห์</span>':REAL;
const ST={tab:1,year:2023,metric:"gpc",sel:null};
const P=DATA.prov, byId=Object.fromEntries(P.map(p=>[p.id,p]));
const yi=()=>Y.indexOf(ST.year);
const comp=(p,y=ST.year)=>{const c=p.cdy[y]; return c?(c[4]??0)+(c[5]??0)+(c[6]??0):null;};
const crate=(p,y=ST.year)=>{const c=comp(p,y); return c==null?null:c/p.pop[Y.indexOf(y)]*1e5;};
const mmAvg=p=>d3.mean(Object.values(p.dom[ST.year]),d=>d.mm), oAvg=p=>d3.mean(Object.values(p.dom[ST.year]),d=>d.o);
const M={
  gpc:{label:"GPP ต่อหัว",get:p=>p.gpp[yi()]*1e9/p.pop[yi()],f:v=>fmt(v/1000)+"k",full:v=>fmt(v)+" บาท/คน",unit:"บาท/คน",ref:()=>REAL+"สศช. GPP ÷ ประชากร · "+ST.year},
  crate:{label:"ร้องเรียนต่อ 1 แสนคน",get:p=>crate(p),f:v=>fmt(v),full:v=>fmt(v,1)+" เรื่อง/แสนคน",unit:"เรื่อง/แสนคน",ref:()=>REAL+"1111 ด้าน 4–6 ÷ ประชากร สศช. · "+ST.year},
  bpc:{label:"งบประมาณต่อหัว",get:p=>p.b[yi()]*1e9/p.pop[yi()],f:v=>fmt(v/1000,1)+"k",full:v=>fmt(v)+" บาท/คน",unit:"บาท/คน",ref:()=>SYN+"ยังไม่มีชุดข้อมูลจริงของงบประมาณรายจังหวัด"},
  mm:{label:"Mismatch",get:p=>mmAvg(p),f:v=>fmt(v),full:v=>fmt(v,1)+" / 100",unit:"คะแนน",ref:()=>SYN+"งบ/ผลลัพธ์ + GPP จริง + ร้องเรียนจริงเมื่อมี · "+ST.year}
};
function alerts(){
  if(ST.year<2021) return [];
  return P.map(p=>{const a=comp(p),b=comp(p,ST.year-1);return {p,a,b,pct:b>0?(a/b-1)*100:null};}).filter(x=>x.pct!=null&&x.a>=30).sort((x,y)=>y.pct-x.pct).slice(0,5);
}

/* ---------- map ---------- */
const W=560,H=760, svg=d3.select("#map"), proj=d3.geoMercator().fitExtent([[8,8],[W-8,H-8]],DATA.geo), path=d3.geoPath(proj);
const gZ=svg.append("g"), gP=gZ.append("g"), gM=gZ.append("g"); let K=1, lastSel=undefined;
const RM=matchMedia("(prefers-reduced-motion: reduce)").matches, DUR=RM?0:750;
const paths=gP.selectAll("path").data(DATA.geo.features).join("path").attr("class","prov").attr("d",path).attr("tabindex",0).attr("role","button")
  .attr("aria-label",d=>byId[d.id]?.th).on("click",(e,d)=>pick(d.id)).on("keydown",(e,d)=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();pick(d.id)}})
  .on("mousemove",(e,d)=>tip(e,d.id)).on("mouseleave",()=>$("#tip").style.opacity=0);
gM.selectAll("circle.mk").data(P).join("circle").attr("class",(p,i)=>"mk"+(i%6===0?" tw":"")).style("animation-delay",(p,i)=>(i%11)*0.3+"s").attr("r",1.3).attr("cx",p=>proj([p.lon,p.lat])[0]).attr("cy",p=>proj([p.lon,p.lat])[1]);
let SC=1;
const placeHot=()=>gM.selectAll("g.hot").attr("transform",p=>`translate(${proj([p.lon,p.lat])}) scale(${1/K})`);
const zoom=d3.zoom().scaleExtent([1,9]).translateExtent([[-40,-40],[W+40,H+40]]).on("zoom",e=>{
  gZ.attr("transform",e.transform);K=e.transform.k;gM.selectAll("circle.mk").attr("r",1.3/Math.sqrt(K));placeHot();gM.selectAll("g.rip").attr("transform",function(){const d=d3.select(this).datum();return `translate(${proj([d.lon,d.lat])}) scale(${1/K})`;});});
svg.call(zoom).on("dblclick.zoom",null);
const flyTo=(t)=>svg.transition().duration(DUR).ease(d3.easeCubicInOut).call(zoom.transform,t);
$("#zin").onclick=()=>svg.transition().duration(DUR/2).call(zoom.scaleBy,1.6);
$("#zout").onclick=()=>svg.transition().duration(DUR/2).call(zoom.scaleBy,1/1.6);
$("#zrs").onclick=()=>flyTo(d3.zoomIdentity);
function fly(){
  if(!ST.sel){flyTo(d3.zoomIdentity);return;}
  const f=DATA.geo.features.find(d=>d.id===ST.sel); if(!f) return;
  const [[x0,y0],[x1,y1]]=path.bounds(f), k=Math.min(5,.42/Math.max((x1-x0)/W,(y1-y0)/H)), cx=(x0+x1)/2, cy=(y0+y1)/2;
  flyTo(d3.zoomIdentity.translate(W/2-k*cx,H/2-k*cy).scale(k));
}
function tip(e,id){
  const p=byId[id],t=$("#tip"),r=$(".mapbox").getBoundingClientRect(),m=M[ST.metric],v=m.get(p);
  t.innerHTML=`<b>${p.th}</b>${m.label}<br><span>${v==null?"ไม่มีข้อมูล":m.full(v)}</span><br>ประชากร <span>${fmt(p.pop[yi()]/1e6,2)} ล้าน</span>`;
  const W0=r.width/SC,H0=r.height/SC;let x=(e.clientX-r.left)/SC+14,y=(e.clientY-r.top)/SC+14; if(x>W0-170)x-=185; if(y>H0-90)y-=95;
  t.style.left=x+"px";t.style.top=y+"px";t.style.opacity=1;
}
function drawMap(){
  const m=M[ST.metric], vals=P.map(m.get).filter(v=>v!=null).sort(d3.ascending);
  const lo=d3.quantile(vals,.03),hi=d3.quantile(vals,.94);
  const col=d3.scaleLinear().domain([lo,(lo+hi)/2,hi]).range(["#0d2a5c","#1f64d6","#4cc9ff"]).clamp(true);
  paths.attr("fill",d=>{const v=m.get(byId[d.id]);return v==null?"#101828":col(v)}).classed("sel",d=>d.id===ST.sel);
  paths.filter(d=>d.id===ST.sel).raise();
  $("#lgMin").textContent=m.f(lo); $("#lgMax").textContent=m.f(hi)+" "+m.unit;
  const al=alerts().map(x=>x.p);
  const g=gM.selectAll("g.hot").data(al,d=>d.id).join(e=>{const g=e.append("g").attr("class","hot");
    g.append("circle").attr("class","pulse").attr("r",8);g.append("circle").attr("class","core").attr("r",3);g.append("text").attr("class","mlabel").attr("dx",8).attr("dy",3);return g;});
  g.select("text").text(p=>p.th);placeHot();gM.selectAll("g.hot").raise();
  const sp=ST.sel?[byId[ST.sel]]:[];gM.selectAll("g.rip").data(sp,d=>d.id).join(e=>{const g=e.append("g").attr("class","rip");g.append("circle").attr("class","ripple").attr("r",14);return g;},u=>u,x=>x.remove()).attr("transform",d=>`translate(${proj([d.lon,d.lat])}) scale(${1/K})`);
  $("#mapRef").innerHTML=m.ref()+'<span>· ขอบเขตจังหวัด: GeoJSON ข้อมูลเปิด</span>';
  $("#mtabs").querySelectorAll(".tab").forEach(b=>b.setAttribute("aria-pressed",b.dataset.k===ST.metric));
  const c=$("#callout"); if(!ST.sel){c.hidden=true}else{const p=byId[ST.sel];c.hidden=false;
    c.innerHTML=`<div class="n">${p.th}</div><div class="m">${p.en} · ${REG[p.region]}<br>GPP ต่อหัว <b>${fmt(M.gpc.get(p))}</b> บาท<br>ประชากร <b>${fmt(p.pop[yi()])}</b><br>ร้องเรียน <b>${comp(p)==null?"ไม่มีข้อมูล":fmt(comp(p))+" เรื่อง"}</b></div>`;}
}

/* ---------- helpers ---------- */
const panel=(title,body,ref,cls="",extra="")=>`<div class="panel ${extra}"><div class="ph"><div class="pt ${cls}">${title}</div></div>${body}<div class="ref">${ref||""}</div></div>`;
const chart=(id,vb)=>`<div class="chart"><svg id="${id}" viewBox="${vb}" preserveAspectRatio="xMidYMid meet"></svg></div>`;
function cu(v){const m=String(v).match(/^(#?)([\d,]+(?:\.\d+)?)(.*)$/);if(!m)return v;const to=+m[2].replace(/,/g,""),dec=(m[2].split(".")[1]||"").length;
  return `<span class="cu" data-pre="${m[1]}" data-to="${to}" data-dec="${dec}" data-suf="${m[3].replace(/"/g,"")}">${v}</span>`;}
function countUp(){document.querySelectorAll(".cu").forEach(el=>{if(RM)return;const to=+el.dataset.to,dec=+el.dataset.dec,pre=el.dataset.pre,suf=el.dataset.suf;
  d3.select(el).transition().duration(900).ease(d3.easeCubicOut).tween("t",()=>{const i=d3.interpolateNumber(0,to);return t=>{el.textContent=pre+i(t).toLocaleString("en-US",{minimumFractionDigits:dec,maximumFractionDigits:dec})+suf;};});});}
function kpiHtml(list){return `<div class="kpis">`+list.map(x=>`<div class="kpi ${x.alert?"alert":""}"><div class="l"><span>${x.l}</span>${x.syn&&ANY_SYN?'<span class="badge syn">สังเคราะห์</span>':""}</div><div class="v">${cu(x.v)}<small>${x.u||""}</small></div><div class="d ${x.bad?"bad":""}">${x.d||"&nbsp;"}</div></div>`).join("")+`</div>`}
function rankList(items,fv,fmtv,mx,al){return items.map((p,i)=>`<button class="rk ${al?"al":""}" data-id="${p.id}"><span class="i">${String(i+1).padStart(2,"0")}</span><span class="nm"><div>${p.th}</div><div class="bar"><i style="width:${Math.max(3,fv(p)/mx*100)}%"></i></div></span><span class="val">${fmtv(p)}</span></button>`).join("")}
const bindRk=()=>document.querySelectorAll(".rk").forEach(b=>b.onclick=()=>pick(b.dataset.id,true));
const nat=(i=yi())=>({gpp:d3.sum(P,p=>p.gpp[i])/1000,pop:d3.sum(P,p=>p.pop[i]),b:d3.sum(P,p=>p.b[i])/1000});
const natComp=y=>y<2020?null:d3.sum(P,p=>comp(p,y));
const domComp=(list,y)=>[4,5,6].map(d=>d3.sum(list,p=>(p.cdy[y]||{})[d]??0));
const delta=(a,b)=>b?((a/b-1)*100):null;
const dTxt=(a,b)=>{const d=delta(a,b);return d==null?"":`${d>=0?"▲":"▼"} ${fmt(Math.abs(d),1)}% vs ${ST.year-1}`};

/* ---------- charts ---------- */
function line(id,series,opt={}){
  const s=d3.select(id).html(""),w=320,h=170,m={l:34,r:14,t:16,b:20};
  const all=series.flatMap(x=>x.v).filter(v=>v!=null),x=d3.scalePoint().domain(Y).range([m.l,w-m.r]),y=d3.scaleLinear().domain([0,d3.max(all)*1.12]).nice().range([h-m.b,m.t]);
  s.append("g").selectAll("line").data(y.ticks(4)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y).attr("y2",y).attr("stroke",axisCol);
  s.append("g").selectAll("text").data(y.ticks(4)).join("text").attr("class","axis").attr("x",m.l-5).attr("y",d=>y(d)+3).attr("text-anchor","end").text(d=>d);
  s.append("g").selectAll("text").data(Y).join("text").attr("class","axis").attr("x",x).attr("y",h-5).attr("text-anchor","middle").text(d=>d).style("fill",d=>d===ST.year?"#eef3ff":"");
  s.append("line").attr("x1",x(ST.year)).attr("x2",x(ST.year)).attr("y1",m.t).attr("y2",h-m.b).attr("stroke","rgba(238,243,255,.25)").attr("stroke-dasharray","2 3");
  const cid="c"+Math.random().toString(36).slice(2,6);const cr=s.append("clipPath").attr("id",cid).append("rect").attr("x",0).attr("y",0).attr("height",h).attr("width",RM?w:0);cr.transition().duration(DUR*1.4).ease(d3.easeCubicOut).attr("width",w);
  const gC=s.append("g").attr("clip-path",`url(#${cid})`);
  series.forEach(se=>{
    gC.append("path").attr("d",d3.line().x((_,i)=>x(Y[i])).y(d=>y(d)).curve(d3.curveMonotoneX)(se.v)).attr("fill","none").attr("stroke",se.c).attr("stroke-width",2).attr("stroke-dasharray",se.dash||null).style("filter",`drop-shadow(0 0 4px ${se.c}88)`);
    gC.selectAll(null).data(se.v).join("circle").attr("cx",(_,i)=>x(Y[i])).attr("cy",y).attr("r",(_,i)=>Y[i]===ST.year?3.8:2).attr("fill",se.c);
    gC.append("text").attr("class","axis").attr("x",x(ST.year)).attr("y",y(se.v[yi()])-8).attr("text-anchor","middle").style("fill","#eef3ff").text(fmt(se.v[yi()],opt.d??1));
  });
}
function donut(id,legId,vals){
  const s=d3.select(id).html(""),tot=d3.sum(vals);
  if(!tot){s.append("text").attr("x",60).attr("y",64).attr("text-anchor","middle").attr("class","axis").text("ไม่มีข้อมูล");$(legId).innerHTML="";return;}
  const arcs=d3.pie().sort(null).padAngle(.03)(vals),ar=d3.arc().innerRadius(38).outerRadius(56).cornerRadius(3),g=s.append("g").attr("transform","translate(60,60)");
  g.selectAll("path").data(arcs).join("path").attr("fill",(d,i)=>DCOL[[4,5,6][i]]).transition().duration(DUR).ease(d3.easeCubicOut).attrTween("d",d=>{const i=d3.interpolate({startAngle:d.startAngle,endAngle:d.startAngle,padAngle:d.padAngle},d);return t=>ar(i(t));});
  g.append("text").attr("text-anchor","middle").attr("y",3).style("fill","#eef3ff").style("font-size","15px").text(fmt(tot));
  g.append("text").attr("text-anchor","middle").attr("y",16).attr("class","axis").text("เรื่อง");
  $(legId).innerHTML=[4,5,6].map((d,i)=>`<span><i style="background:${DCOL[d]}"></i>${SH[d]} <b style="font-family:var(--mono);color:var(--white)">${fmt(vals[i]/tot*100,1)}%</b></span>`).join("");
}
function hbars(id,rows,o={}){
  const s=d3.select(id).html(""),w=320,h=o.h||170,lw=o.lw||104;
  const x=d3.scaleLinear().domain([0,d3.max(rows,d=>d[1])||1]).range([0,w-lw-44]),y=d3.scaleBand().domain(rows.map(d=>d[0])).range([4,h-4]).padding(.3);
  const g=s.selectAll("g").data(rows).join("g").attr("transform",d=>`translate(${lw},${y(d[0])})`);
  g.append("rect").attr("width",0).attr("height",y.bandwidth()).attr("rx",3).attr("fill",d=>d[2]||"#3d8bff").style("filter",d=>`drop-shadow(0 0 4px ${(d[2]||"#3d8bff")}66)`).transition().duration(DUR).delay((d,i)=>i*60).ease(d3.easeCubicOut).attr("width",d=>x(d[1]));
  g.append("text").attr("class","axis").attr("x",-6).attr("y",y.bandwidth()/2+3).attr("text-anchor","end").text(d=>d[0]);
  g.append("text").attr("class","axis").attr("x",d=>x(d[1])+5).attr("y",y.bandwidth()/2+3).style("fill","#eef3ff").text(d=>fmt(d[1],o.d??1));
}
function area(id,vals){
  const s=d3.select(id).html(""),w=320,h=130,m={l:36,r:12,t:14,b:18};
  const x=d3.scalePoint().domain(CY).range([m.l,w-m.r]),y=d3.scaleLinear().domain([0,d3.max(vals)*1.15||1]).nice().range([h-m.b,m.t]);
  const gid="g"+Math.random().toString(36).slice(2,6);
  const df=s.append("defs").append("linearGradient").attr("id",gid).attr("x1",0).attr("y1",0).attr("x2",0).attr("y2",1);
  df.append("stop").attr("offset","0%").attr("stop-color","#ff3b4e").attr("stop-opacity",.45);df.append("stop").attr("offset","100%").attr("stop-color","#ff3b4e").attr("stop-opacity",0);
  s.append("g").selectAll("line").data(y.ticks(3)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y).attr("y2",y).attr("stroke",axisCol);
  s.append("g").selectAll("text").data(y.ticks(3)).join("text").attr("class","axis").attr("x",m.l-5).attr("y",d=>y(d)+3).attr("text-anchor","end").text(d=>d>=1000?d/1000+"k":d);
  s.append("g").selectAll("text").data(CY).join("text").attr("class","axis").attr("x",x).attr("y",h-4).attr("text-anchor","middle").text(d=>d).style("fill",d=>d===ST.year?"#eef3ff":"");
  const cid="c"+gid;s.append("clipPath").attr("id",cid).append("rect").attr("x",0).attr("y",0).attr("height",h).attr("width",RM?w:0).transition().duration(DUR*1.4).ease(d3.easeCubicOut).attr("width",w);
  const gC=s.append("g").attr("clip-path",`url(#${cid})`);
  gC.append("path").attr("d",d3.area().x((_,i)=>x(CY[i])).y0(h-m.b).y1(d=>y(d)).curve(d3.curveMonotoneX)(vals)).attr("fill",`url(#${gid})`);
  gC.append("path").attr("d",d3.line().x((_,i)=>x(CY[i])).y(d=>y(d)).curve(d3.curveMonotoneX)(vals)).attr("fill","none").attr("stroke","#ff3b4e").attr("stroke-width",2);
  gC.selectAll("circle").data(vals).join("circle").attr("cx",(_,i)=>x(CY[i])).attr("cy",y).attr("r",(_,i)=>CY[i]===ST.year?3.8:2).attr("fill","#ff3b4e");
  s.append("text").attr("class","axis").attr("x",x(2023)).attr("y",y(vals[3])-8).attr("text-anchor","end").style("fill","#eef3ff").text(fmt(vals[3]));
}
function radar(id,p){
  const s=d3.select(id).html(""),cx=160,cy=95,R=64;
  const pct=f=>{const arr=P.map(f).filter(v=>v!=null).sort(d3.ascending);return q=>{const v=f(q);return v==null?0:d3.bisectRight(arr,v)/arr.length*100;}};
  const ax=[["GPP ต่อหัว",pct(M.gpc.get)],["GPP รวม",pct(q=>q.gpp[yi()])],["ประชากร",pct(q=>q.pop[yi()])],["งบ/หัว*",pct(M.bpc.get)],["ผลลัพธ์*",pct(oAvg)],["ร้องเรียนต่ำ",pct(q=>{const r=crate(q);return r==null?null:-r})]];
  const n=ax.length,ang=i=>-Math.PI/2+i*2*Math.PI/n,pt=(i,v)=>[cx+Math.cos(ang(i))*R*v/100,cy+Math.sin(ang(i))*R*v/100];
  [25,50,75,100].forEach(r=>s.append("polygon").attr("points",d3.range(n).map(i=>pt(i,r)).join(" ")).attr("fill","none").attr("stroke",axisCol));
  d3.range(n).forEach(i=>{const e=pt(i,100);s.append("line").attr("x1",cx).attr("y1",cy).attr("x2",e[0]).attr("y2",e[1]).attr("stroke",axisCol);
    const l=pt(i,128);s.append("text").attr("class","axis").attr("x",l[0]).attr("y",l[1]+3).attr("text-anchor",Math.abs(l[0]-cx)<6?"middle":l[0]>cx?"start":"end").text(ax[i][0]);});
  s.append("polygon").attr("points",d3.range(n).map(i=>pt(i,50)).join(" ")).attr("fill","none").attr("stroke","#8a98b8").attr("stroke-dasharray","3 3");
  const vals=ax.map(a=>a[1](p));
  s.append("polygon").attr("points",vals.map((v,i)=>pt(i,0)).join(" ")).attr("fill","rgba(76,201,255,.22)").attr("stroke","#4cc9ff").attr("stroke-width",2).style("filter","drop-shadow(0 0 5px #4cc9ff88)").transition().duration(DUR).ease(d3.easeBackOut.overshoot(1.2)).attr("points",vals.map((v,i)=>pt(i,v)).join(" "));
  vals.forEach((v,i)=>s.append("circle").attr("cx",pt(i,v)[0]).attr("cy",pt(i,v)[1]).attr("r",0).attr("fill","#4cc9ff").transition().delay(DUR*.6).duration(300).attr("r",2.8));
}
function scatter(id,xf,yf,o){
  const s=d3.select(id).html(""),w=320,h=o.h||190,m={l:38,r:12,t:10,b:30};
  const pts=P.map(p=>({p,x:xf(p),y:yf(p)})).filter(d=>d.x!=null&&d.y!=null);
  if(!pts.length){s.append("text").attr("x",w/2).attr("y",h/2).attr("text-anchor","middle").attr("class","axis").text("ไม่มีข้อมูลในปีที่เลือก");return;}
  const x=(o.log?d3.scaleLog():d3.scaleLinear()).domain(d3.extent(pts,d=>d.x)).nice().range([m.l,w-m.r]),y=d3.scaleLinear().domain([0,d3.max(pts,d=>d.y)*1.08]).nice().range([h-m.b,m.t]);
  const r=d3.scaleSqrt().domain(d3.extent(P,p=>p.pop[yi()])).range([2.2,9]), al=new Set(alerts().map(a=>a.p.id));
  s.append("g").selectAll("line").data(y.ticks(4)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y).attr("y2",y).attr("stroke",axisCol);
  s.append("g").selectAll("text").data(y.ticks(4)).join("text").attr("class","axis").attr("x",m.l-5).attr("y",d=>y(d)+3).attr("text-anchor","end").text(d=>d);
  s.append("g").selectAll("text").data(o.log?[1e4,3e4,1e5,3e5,1e6].filter(v=>v>=x.domain()[0]&&v<=x.domain()[1]):x.ticks(4)).join("text").attr("class","axis").attr("x",x).attr("y",h-m.b+13).attr("text-anchor","middle").text(d=>o.xf?o.xf(d):d);
  s.append("text").attr("class","axis").attr("x",(m.l+w-m.r)/2).attr("y",h-3).attr("text-anchor","middle").text(o.xl);
  s.append("text").attr("class","axis").attr("x",4).attr("y",8).text(o.yl);
  s.selectAll("circle").data(pts).join("circle").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.y)).attr("r",0)
    .attr("fill",d=>o.alert&&al.has(d.p.id)?"rgba(255,59,78,.75)":"rgba(61,139,255,.55)").attr("stroke",d=>d.p.id===ST.sel?"#fff":(o.alert&&al.has(d.p.id)?"#ff3b4e":"#4cc9ff")).attr("stroke-width",d=>d.p.id===ST.sel?2:.8)
    .style("cursor","pointer").on("click",(e,d)=>pick(d.p.id,true)).call(c=>c.append("title").text(d=>d.p.th)).transition().duration(DUR).delay((d,i)=>i*8).ease(d3.easeBackOut).attr("r",d=>r(d.p.pop[yi()]));
}
function heat(id,list){
  const s=d3.select(id).html(""),w=320,h=190,lw=84,top=26,cw=(w-lw-6)/6,ch=(h-top-4)/list.length;
  const mx=d3.max(list,p=>d3.max(Object.values(p.dom[ST.year]),d=>d.mm)),col=d3.scaleLinear().domain([0,mx/2,mx]).range(["#0a1a3a","#1f64d6","#4cc9ff"]);
  [1,2,3,4,5,6].forEach((d,i)=>s.append("text").attr("class","axis").attr("x",lw+i*cw+cw/2).attr("y",16).attr("text-anchor","middle").text(SS[d]));
  list.forEach((p,j)=>{s.append("text").attr("class","axis").attr("x",lw-6).attr("y",top+j*ch+ch/2+3).attr("text-anchor","end").style("fill","#eef3ff").text(p.th);
    [1,2,3,4,5,6].forEach((d,i)=>{const v=p.dom[ST.year][d].mm;
      s.append("rect").attr("x",lw+i*cw+1).attr("y",top+j*ch+1).attr("width",cw-2).attr("height",ch-2).attr("rx",3).attr("fill",col(v)).attr("opacity",0).transition().delay((j*6+i)*18).duration(400).attr("opacity",1);
      s.append("text").attr("class","axis").attr("x",lw+i*cw+cw/2).attr("y",top+j*ch+ch/2+3).attr("text-anchor","middle").style("fill",v>mx*.55?"#04060b":"#eef3ff").text(fmt(v));});});
}

/* ---------- tabs ---------- */
const provSelect=()=>`<label class="sub" for="ps">เลือกจังหวัด</label><select id="ps" style="width:100%;margin:3px 0 8px">${[...P].sort((a,b)=>a.th.localeCompare(b.th,"th")).map(p=>`<option value="${p.id}" ${p.id===ST.sel?"selected":""}>${p.th}</option>`).join("")}</select>`;
function provLeft(withSelect){
  const p=byId[ST.sel],i=yi(),cc=comp(p),cp=comp(p,ST.year-1),cd=cc!=null&&cp?delta(cc,cp):null,m=M[ST.metric];
  const rk=[...P].filter(q=>m.get(q)!=null).sort((a,b)=>m.get(b)-m.get(a)).findIndex(q=>q.id===p.id)+1;
  const g=money(p.gpp[i]),pp=popu(p.pop[i]);
  const html=
   panel(withSelect?"เลือกจังหวัด":"จังหวัดที่เลือก · "+p.th,(withSelect?provSelect():"")+kpiHtml([
     {l:"GPP จังหวัด",v:g[0],u:g[1],d:i>0?dTxt(p.gpp[i],p.gpp[i-1]):"",bad:i>0&&p.gpp[i]<p.gpp[i-1]},
     {l:"ประชากร",v:pp[0],u:pp[1],d:i>0?dTxt(p.pop[i],p.pop[i-1]):""},
     {l:"เรื่องร้องเรียน",v:cc==null?"ไม่มีข้อมูล":fmt(cc),u:cc==null?"":"เรื่อง",d:cd==null?"":dTxt(cc,cp),bad:cd>0,alert:cd>0},
     {l:"อันดับ · "+m.label,v:m.get(p)==null?"–":"#"+rk,u:"/ 77",d:m.get(p)==null?"":(m.get(p)>=d3.median(P,m.get)?"สูงกว่า":"ต่ำกว่า")+"ค่ากลาง",syn:ST.metric==="bpc"}]),REAL+"สศช. · 1111","","fix")+
   panel("GPP จังหวัด · พันล้านบาท",chart("line","0 0 320 170"),REAL+"สศช. GPP 2019–2023")+
   panel("ร้องเรียนตามด้าน · "+ST.year,`<div class="row2"><svg id="donut" viewBox="0 0 120 120"></svg><div class="legend2" id="dl" style="flex-direction:column;gap:6px;margin:0"></div></div>`,REAL+"1111 · ด้าน 4–6 เท่านั้น");
  return html;
}
function provLeftDraw(){const p=byId[ST.sel];line("#line",[{c:"#4cc9ff",v:p.gpp}],{d:0});donut("#donut","#dl",ST.year<2020?[0,0,0]:domComp([p],ST.year));}
function tab1(){
  if(ST.sel){ $("#L").innerHTML=provLeft(false); provLeftDraw(); }
  else{
    const n=nat(),n0=nat(yi()-1),cc=natComp(ST.year),cp=natComp(ST.year-1),cd=cc!=null&&cp?delta(cc,cp):null;
    $("#L").innerHTML=
     panel("ภาพรวมทั้งประเทศ · 77 จังหวัด",kpiHtml([
       {l:"GDP (ผลรวม GPP)",v:fmt(n.gpp,1),u:"ล้านล้านบาท",d:yi()>0?dTxt(n.gpp,n0.gpp):"",bad:yi()>0&&n.gpp<n0.gpp},
       {l:"ประชากร",v:fmt(n.pop/1e6,1),u:"ล้านคน",d:"ประมาณการ สศช."},
       {l:"เรื่องร้องเรียน",v:cc==null?"ไม่มีข้อมูล":fmt(cc),u:cc==null?"":"เรื่อง",d:cd==null?"":dTxt(cc,cp),bad:cd>0,alert:cd>0},
       {l:"งบประมาณ ÷ GDP",v:fmt(n.b/n.gpp*100,1)+"%",d:"",syn:true}]),REAL+"สศช. · 1111","","fix")+
     panel("GDP vs งบประมาณ · ล้านล้านบาท",chart("line","0 0 320 170")+`<div class="legend2"><span><i style="background:#4cc9ff"></i>GDP</span><span><i style="background:#8a98b8"></i>งบประมาณ ${SYN}</span></div>`,REAL+"สศช. GPP 2019–2023")+
     panel("สัดส่วนเรื่องร้องเรียนตามด้าน · "+ST.year,`<div class="row2"><svg id="donut" viewBox="0 0 120 120"></svg><div class="legend2" id="dl" style="flex-direction:column;gap:6px;margin:0"></div></div>`,REAL+"1111 · จัดกลุ่มด้าน 4–6");
    line("#line",[{c:"#4cc9ff",v:Y.map((_,i)=>nat(i).gpp)},{c:"#8a98b8",v:Y.map((_,i)=>nat(i).b),dash:"4 3"}]);
    donut("#donut","#dl",ST.year<2020?[0,0,0]:domComp(P,ST.year));
  }
  const m=M[ST.metric],list=P.filter(p=>m.get(p)!=null).sort((a,b)=>m.get(b)-m.get(a)).slice(0,5),mx=m.get(list[0])||1,al=alerts();
  $("#R").innerHTML=
   panel("Top 5 · "+m.label,list.length?rankList(list,m.get,p=>m.f(m.get(p)),mx):'<div class="empty">ไม่มีข้อมูล</div>',m.ref(),"","fix")+
   panel("⚠ แจ้งเตือนร้องเรียน · เพิ่มขึ้นเทียบปีก่อน",al.length?rankList(al.map(x=>x.p),p=>al.find(x=>x.p===p).pct,p=>"+"+fmt(al.find(x=>x.p===p).pct)+"%",al[0].pct,true):'<div class="empty">'+(ST.year<2021?"ต้องมีข้อมูลปีก่อนหน้า (เลือกปี 2021 ขึ้นไป)":"ไม่มีจังหวัดที่เข้าเกณฑ์")+"</div>",REAL+"1111 · ≥30 เรื่อง","alert","fix")+
   panel("GPP ต่อหัว vs ร้องเรียนต่อแสนคน · "+ST.year,chart("sc","0 0 320 200"),REAL+"ขนาดวง = ประชากร · แดง = จังหวัดแจ้งเตือน");
  scatter("#sc",p=>M.gpc.get(p),p=>ST.year<2020?null:crate(p),{log:true,xl:"GPP ต่อหัว (บาท, log)",yl:"ร้องเรียน/แสนคน",xf:d=>d3.format("~s")(d),h:200,alert:true});
}
function tab2(){
  const p=byId[ST.sel];
  $("#L").innerHTML=provLeft(true); provLeftDraw();
  $("#R").innerHTML=
   panel("เทียบกับจังหวัดอื่น (เปอร์เซ็นไทล์) · "+p.th,chart("radar","0 0 320 190"),REAL+"สศช. · 1111 &nbsp;"+SYN+"* งบ/ผลลัพธ์ · เส้นประ = ค่ากลาง")+
   panel("งบประมาณรายด้าน · พันล้านบาท · 2023",chart("bars","0 0 320 150"),SYN+"รอข้อมูลจริงงบประมาณรายจังหวัด")+
   panel("เรื่องร้องเรียน 2020–2023",chart("area","0 0 320 130"),REAL+"1111 · ด้าน 4–6 (ปีปฏิทิน)","alert");
  radar("#radar",p);
  hbars("#bars",Object.entries(p.dom[ST.year]).map(([k,v])=>[SH[k],v.b,"#3d8bff"]),{h:150,lw:104,d:1});
  area("#area",CY.map(y=>comp(p,y)));
}
function tab3(){
  const p=ST.sel?byId[ST.sel]:null, avg=d3.mean(P,mmAvg), hi=P.filter(q=>mmAvg(q)>=20);
  const dAvg=[1,2,3,4,5,6].map(d=>[SH[d],d3.mean(P,q=>q.dom[ST.year][d].mm),d>=4?"#ff3b4e":"#3d8bff"]);
  const rk=p?[...P].sort((a,b)=>mmAvg(b)-mmAvg(a)).findIndex(q=>q.id===p.id)+1:null;
  $("#L").innerHTML=
   panel("สรุปความไม่สอดคล้อง · "+ST.year,kpiHtml([
     {l:"Mismatch เฉลี่ยประเทศ",v:fmt(avg,1),u:"/100",syn:true,d:"ยิ่งสูงยิ่งไม่สอดคล้อง"},
     {l:"จังหวัดคะแนน ≥ 20",v:fmt(hi.length),u:"จาก 77",syn:true,d:""},
     {l:p?p.th:"เลือกจังหวัด",v:p?fmt(mmAvg(p),1):"–",u:p?"/100":"",syn:true,d:p?"อันดับ #"+rk:"คลิกบนแผนที่"},
     {l:"ด้านร้องเรียนมีข้อมูล",v:"3/6",d:"ด้าน 4–6 · 2020–2023"}]),SYN+"งบ/ผลลัพธ์ &nbsp;"+REAL+"GPP · ร้องเรียน","","fix")+
   panel(p?"Mismatch รายด้าน · "+p.th:"Mismatch รายด้าน",p?chart("bars","0 0 320 170"):'<div class="empty">คลิกจังหวัดบนแผนที่เพื่อดูคะแนนรายด้าน</div>',SYN+"ด้านที่ไม่มีข้อมูลร้องเรียน ถ่วงน้ำหนักใหม่")+
   panel("Mismatch เฉลี่ยรายด้าน · ทั้งประเทศ",chart("bars2","0 0 320 170"),SYN+"แถบแดง = ด้านที่มีข้อมูลร้องเรียนจริง");
  if(p) hbars("#bars",Object.entries(p.dom[ST.year]).map(([k,v])=>[SH[k],v.mm,+k>=4?"#ff3b4e":"#3d8bff"]),{h:170});
  hbars("#bars2",dAvg,{h:170});
  const sorted=[...P].sort((a,b)=>mmAvg(b)-mmAvg(a)), list=sorted.slice(0,5);
  $("#R").innerHTML=
   panel("Top 5 · Mismatch สูงสุด",rankList(list,mmAvg,q=>fmt(mmAvg(q),1),mmAvg(list[0])),M.mm.ref(),"","fix")+
   panel("Heatmap · 7 จังหวัดที่ไม่สอดคล้องสูงสุด × 6 ด้าน",chart("heat","0 0 320 190"),SYN+"ตัวเลข = คะแนน Mismatch 0–100")+
   panel("งบประมาณต่อหัว vs ผลลัพธ์เฉลี่ย",chart("sc","0 0 320 190"),SYN+"ขนาดวง = ประชากร");
  heat("#heat",sorted.slice(0,7));
  scatter("#sc",p=>M.bpc.get(p),p=>oAvg(p),{xl:"งบประมาณต่อหัว (บาท)",yl:"ผลลัพธ์ (0–100)",xf:d=>fmt(d/1000)+"k",h:190});
}
let lastTab=null;
function render(){
  if(ST.tab===2&&!ST.sel) ST.sel=P.find(q=>q.th==="ขอนแก่น").id;
  if(ST.metric==="crate"&&ST.year<2020) ST.metric="gpc";
  if(ST.tab===3){ST.metric="mm";} else if(ST.metric==="mm") ST.metric="gpc";
  $("#yr").value=ST.year; 
  $("#mtabs").innerHTML=ST.tab===3?'<span class="chip">Mismatch เฉลี่ย 6 ด้าน · ปี '+ST.year+'</span>':Object.entries(M).filter(([k])=>k!=="mm").map(([k,m])=>`<button class="tab" data-k="${k}" aria-pressed="${k===ST.metric}">${m.label}${k==="bpc"&&!FL.budget?" · สังเคราะห์":""}</button>`).join("");
  $("#reset").hidden=!(ST.sel&&ST.tab!==2);
  $("#note").innerHTML=ST.tab===3&&ANY_SYN?'<div class="banner">Mismatch คำนวณจากงบประมาณ/ผลลัพธ์ที่ยังเป็นข้อมูลสังเคราะห์ จึงเป็นเพียงตัวอย่างรูปแบบ ยังไม่ใช่ข้อสรุปเชิงนโยบาย</div>':(ST.year<2020?'<div class="banner">ปี 2019 ไม่มีข้อมูลเรื่องร้องเรียนจากชุดข้อมูลเปิด (เริ่มปี 2020)</div>':"");
  document.querySelectorAll(".pill").forEach(b=>b.setAttribute("aria-selected",+b.dataset.t===ST.tab));
  const switched=lastTab!==ST.tab; lastTab=ST.tab;
  ({1:tab1,2:tab2,3:tab3})[ST.tab](); bindRk(); drawMap(); countUp();
  if(switched&&!RM){["#L","#R"].forEach(q=>{const el=$(q);el.classList.remove("enter");void el.offsetWidth;el.classList.add("enter");});}
  if(ST.sel!==lastSel){lastSel=ST.sel;fly();}
  const ps=$("#ps"); if(ps) ps.onchange=()=>{ST.sel=ps.value;render();};
}
function pick(id,fromRank){ if(ST.tab===2) ST.sel=id; else ST.sel=(id===ST.sel&&!fromRank)?null:id; render(); }
$("#yr").innerHTML=Y.map(y=>`<option value="${y}">${y}</option>`).join(""); $("#yr").value=ST.year;
$("#yr").onchange=e=>{ST.year=+e.target.value;render();};
$("#mtabs").addEventListener("click",e=>{const b=e.target.closest(".tab");if(b){ST.metric=b.dataset.k;render();}});
$("#reset").onclick=()=>{ST.sel=null;render();};
document.querySelectorAll(".pill").forEach(b=>b.onclick=()=>{ST.tab=+b.dataset.t;render();});
/* fit the 1600x900 stage into the window (no scrolling); narrow screens fall back to a normal scrolling page */
function fit(){
  const f=$("#fit"),st=$("#stage"),narrow=innerWidth<1000;
  document.documentElement.classList.toggle("flow",narrow);
  if(narrow){SC=1;f.style.width=f.style.height="";return;}
  SC=Math.min(innerWidth/1600,innerHeight/900);
  st.style.transform=`scale(${SC})`; f.style.width=1600*SC+"px"; f.style.height=900*SC+"px";
}
if(window.__gdFit) removeEventListener("resize",window.__gdFit); window.__gdFit=fit; addEventListener("resize",fit); fit();
$("#stage").addEventListener("mousemove",e=>{const p=e.target.closest&&e.target.closest(".panel");if(!p)return;const r=p.getBoundingClientRect();p.style.setProperty("--mx",(e.clientX-r.left)/SC+"px");p.style.setProperty("--my",(e.clientY-r.top)/SC+"px");});
const mt=DATA.sources.map(s=>`<tr><td>${s.label}</td><td>${s.links.map(l=>`<a href="${l[1]}" target="_blank" rel="noopener noreferrer">${l[0]}</a>`).join(", ")}</td><td>${s.real?'<span class="badge real">ข้อมูลจริง</span>':'<span class="badge syn">ข้อมูลสังเคราะห์</span>'}</td></tr>`).join("");
$("#mtable").innerHTML=`<table><tr><th>ชุดข้อมูล</th><th>แหล่งที่มา</th><th>สถานะ</th></tr>${mt}</table>`;
$("#mmeta").textContent="เรื่องร้องเรียนครอบคลุมปี "+DATA.meta.complaint_years[0]+"–"+DATA.meta.complaint_years.slice(-1)[0]+" ด้าน 4–6 (ปีปฏิทิน)"+(DATA.meta.complaints_fetched?" · ดึงสดจาก data.go.th เมื่อ "+DATA.meta.complaints_fetched:" · ใช้สำเนาที่บันทึกไว้")+" · ด้านที่ไม่มีข้อมูลแสดง \"ไม่มีข้อมูล\" ไม่มีการประมาณค่า";
$("#srcbtn").onclick=()=>{$("#modal").hidden=false;};$("#mclose").onclick=()=>{$("#modal").hidden=true;};$("#modal").onclick=e=>{if(e.target.id==="modal")$("#modal").hidden=true;};
render();

}};
