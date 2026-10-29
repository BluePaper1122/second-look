'use strict';
const $ = id => document.getElementById(id);
let current = null, layout = null, provenance = 'Uploaded data; provenance not verified';
let downloadUrl = null;
function clearDownload(){if(downloadUrl)URL.revokeObjectURL(downloadUrl);downloadUrl=null;$('downloadReady').replaceChildren();$('downloadReady').hidden=true;}
const noteDrafts = new ReviewDrafts();
const fields = ['plate_id','well','sample_id','value','control'];
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function notice(text,error=false){$('notice').textContent=text;$('notice').classList.toggle('error',error);$('notice').setAttribute('role',error?'alert':'status');if(error)$('notice').focus();}
async function request(path,data){
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),50000);
 try{const r=await fetch(path,data===undefined?{signal:controller.signal}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),signal:controller.signal});
 let v;try{v=await r.json();}catch{throw Error('The application returned an unreadable response. Your input is unchanged. Save it before restarting the application.');}
 if(!r.ok){const e=Error(v.error||v.message||'This step could not be completed. Your input is unchanged.');e.code=v.code;e.reference=v.request_id;e.retryable=v.retryable;throw e;}return v;
 }catch(e){if(e.name==='AbortError')throw Error('The request took too long. Your input is unchanged. Check the connection before retrying.');if(e instanceof TypeError)throw Error('The application could not be reached. Keep this tab open and restart the local server, then retry.');throw e;}finally{clearTimeout(timer);}
}
const api=(path,data)=>request(path,data);
function input(){return {csv:$('csv').value,mapping:Object.fromEntries(fields.map(f=>[f,$('map_'+f)?$('map_'+f).value:f]))};}
function invalidate(){clearDownload();current=null;layout=null;$('results').hidden=true;$('modelStatus').textContent='No live review has been performed.';$('priorities').replaceChildren();$('planResult').replaceChildren();}
function csvHeaders(text){
 const cells=[];let cell='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
 else if(c===','&&!quoted){cells.push(cell);cell='';}else if((c==='\n'||c==='\r')&&!quoted){cells.push(cell);return cells;}else cell+=c;}
 if(quoted)throw Error('The CSV header has an unclosed quote. Export the file again as CSV.');cells.push(cell);return cells;
}
function mapping(){invalidate();let names;try{names=csvHeaders($('csv').value.replace(/^\uFEFF/,''));}catch(e){$('mapping').replaceChildren();notice(e.message,true);return;}
 $('mapping').innerHTML=fields.map(f=>`<label>${esc(f)}<select id="map_${f}"><option value="">Choose a column</option>${names.map(n=>`<option ${n===f?'selected':''} value="${esc(n)}">${esc(n)}</option>`).join('')}</select></label>`).join('');for(const f of fields)$('map_'+f).onchange=invalidate;
}
function download(name,text,type){
 clearDownload();downloadUrl=URL.createObjectURL(new Blob([text],{type}));
 const link=document.createElement('a');link.href=downloadUrl;link.download=name;
 link.textContent='Download '+name;
 const explanation=document.createElement('p');explanation.textContent='Your file is ready. If the download did not start, use this link. It is replaced by the next export and cleared when the plate or follow-up settings change.';
 $('downloadReady').append(explanation,link);$('downloadReady').hidden=false;
 // Keep an attached, keyboard-accessible link for browsers that block an
 // automatic download following the asynchronous export validation request.
 link.click();
}
async function busy(id,fn){const controls=[...document.querySelectorAll('button,input,select,textarea')];const states=controls.map(e=>e.disabled);controls.forEach(e=>e.disabled=true);try{await fn();}catch(e){notice(e.message,true);}finally{controls.forEach((e,i)=>e.disabled=states[i]);if(current)$('plan').disabled=!current.report.samples.length||['negative','positive'].some(role=>!current.report.control_ids[role].length);}}
$('load').onclick=()=>busy('load',async()=>{const v=await request('/api/example?kind='+encodeURIComponent($('example').value));$('csv').value=v.csv;provenance=v.synthetic?'Synthetic demonstration · '+$('example').selectedOptions[0].textContent:v.description+' License: '+v.license;$('provenance').textContent=provenance;mapping();if(v.source_url){const link=document.createElement('a');link.href=v.source_url;link.textContent=' Upstream source';link.target='_blank';link.rel='noopener noreferrer';$('provenance').append(link);}notice(v.synthetic?'Synthetic plate loaded. Inspect it when you’re ready.':'Real calibration readings loaded. This case tests compatibility and missing-control handling, not biological validity.');});
$('file').onchange=()=>busy('inspect',async()=>{const file=$('file').files[0];if(!file)return;if(file.size>1e6)throw Error('Choose a CSV smaller than 1 MB.');try{$('csv').value=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());}catch{throw Error('This file is not readable UTF-8 CSV. Export it with UTF-8 encoding and retry.');}provenance='Uploaded data · '+file.name+' · provenance not verified';$('provenance').textContent=provenance;mapping();notice('Your plate is ready. Confirm the columns, then inspect.');});
$('csv').oninput=()=>{provenance='Manually edited data · provenance not verified';$('provenance').textContent=provenance;mapping();};
$('playful').onchange=()=>{document.querySelector('.pip').hidden=!$('playful').checked;};
function drawPlate(rows){
 const byWell=new Map(rows.map(r=>[r.well,r]));
 const values=rows.map(r=>r.value),min=Math.min(...values),max=Math.max(...values);
 let html='<div role="row" class="plate-row"><span role="columnheader" class="axis">Row</span>'+
  Array.from({length:12},(_,i)=>`<span role="columnheader" class="axis">${i+1}</span>`).join('')+'</div>';
 for(const row of 'ABCDEFGH'){
  html+=`<div role="row" class="plate-row"><span role="rowheader" class="axis">${row}</span>`;
  for(let c=1;c<=12;c++){
   const well=row+String(c).padStart(2,'0'),r=byWell.get(well);
   const label=r?`${well}, ${r.sample_id}, ${r.value}, ${r.control}`:`${well}, unmeasured`;
   html+=`<div role="gridcell" aria-selected="false"><button class="well ${r?(r.control!=='sample'?'control':''):'empty'}" data-well="${well}" tabindex="${well==='A01'?0:-1}" aria-label="${esc(label)}">${r?esc(well):'·'}</button></div>`;
  }
  html+='</div>';
 }
 $('plate').innerHTML=html;
 function inspectWell(well){
  for(const button of $('plate').querySelectorAll('[data-well]')){
   const active=button.dataset.well===well;
   button.tabIndex=active?0:-1;button.parentElement.setAttribute('aria-selected',String(active));
  }
  const r=byWell.get(well);
  $('wellDetail').textContent=r?`${r.well} · ${r.sample_id} · ${r.control} · raw measurement ${r.value}`:`${well} · No measurement was recorded. This position is not treated as zero.`;
 }
 for(const button of $('plate').querySelectorAll('[data-well]')){
  const r=byWell.get(button.dataset.well);
  if(r){const n=(r.value-min)/(max-min||1);button.style.backgroundColor=`rgb(${Math.round(234-155*n)},${Math.round(240-83*n)},${Math.round(200-68*n)})`;}
  button.onclick=()=>inspectWell(button.dataset.well);button.onfocus=()=>inspectWell(button.dataset.well);
 }
 $('plate').onkeydown=event=>{
  const button=event.target.closest('button[data-well]');if(!button)return;
  let row=button.dataset.well.charCodeAt(0)-65,col=Number(button.dataset.well.slice(1))-1;
  const whole=event.ctrlKey||event.metaKey;
  switch(event.key){
   case 'ArrowRight':col=Math.min(11,col+1);break;
   case 'ArrowLeft':col=Math.max(0,col-1);break;
   case 'ArrowDown':row=Math.min(7,row+1);break;
   case 'ArrowUp':row=Math.max(0,row-1);break;
   case 'Home':col=0;if(whole)row=0;break;
   case 'End':col=11;if(whole)row=7;break;
   case 'PageDown':row=Math.min(7,row+4);break;
   case 'PageUp':row=Math.max(0,row-4);break;
   default:return;
  }
  event.preventDefault();
  const well=String.fromCharCode(65+row)+String(col+1).padStart(2,'0');
  $('plate').querySelector(`[data-well="${well}"]`).focus();
 };
}
function findingHtml(f,facts){return `<article class="finding"><h3><span class="badge">${esc(f.level)}</span>${esc(f.title)}</h3><p>${esc(f.detail)}</p><details><summary>See supporting measurements</summary><div class="evidence">${f.evidence.map(id=>{const x=facts[id];return esc(`${id}: ${typeof x.value==='number'?Number(x.value.toPrecision(6)):x.value} ${x.units}\nWells: ${x.wells.join(', ')||'none'}`);}).join('\n\n')}</div></details></article>`;}
function renderInspection(value){current=value;$('notes').value=noteDrafts.select(value.workflow.report_id);$('results').hidden=false;drawPlate(current.rows);const flow=current.workflow;const labels={controls_only:'Control measurements only',control_review_needed:'Control information needs review',position_check_suggested:'A position check may help',researcher_review:'Ready for researcher review'};$('decision').innerHTML=`<h3>${esc(labels[flow.state]||'Review the evidence')}</h3><p>${esc(flow.message)}</p><p class="small">Report ${esc(flow.report_id)} · Analysis ${esc(flow.analysis_version)}</p><details><summary>Suggested next steps</summary><ol>${flow.actions.map(a=>`<li><strong>${esc(a.title)}</strong><p>${esc(a.detail)}</p></li>`).join('')}</ol></details>`;const {facts,findings,samples}=current.report;$('findings').innerHTML=findings.map(f=>findingHtml(f,facts)).join('');$('replicateTable').innerHTML='<table><thead><tr><th scope="col">Sample / control</th><th scope="col">Role</th><th scope="col">Zone</th><th scope="col">Wells</th><th scope="col">Mean</th><th scope="col">SD</th></tr></thead><tbody>'+(current.report.replicate_summaries||[]).map(g=>{const values=g.evidence.map(k=>facts[k].value);return '<tr><th scope="row">'+esc(g.sample_id)+'</th><td>'+esc(g.role)+'</td><td>'+esc(g.zone)+'</td><td>'+values[0]+'</td><td>'+Number(values[1].toPrecision(5))+'</td><td>'+(values.length>2?Number(values[2].toPrecision(5)):'Not estimable')+'</td></tr>';}).join('')+'</tbody></table>';$('metrics').innerHTML=[['well_count','Measured wells'],['z_prime','Z-prime · exploratory'],['uncrossed_sample_count','Sample IDs in one zone']].filter(([k])=>facts[k]).map(([k,label])=>`<div class="metric"><strong>${Number(facts[k].value.toFixed(3))}</strong><span>${label}</span></div>`).join('');$('samples').innerHTML='<legend>Samples for follow-up</legend>'+samples.map((s,i)=>`<label class="sample-choice"><input type="checkbox" value="${esc(s)}" >${esc(s)}</label>`).join('');for(const box of $('samples').querySelectorAll('input'))box.onchange=clearPlan;$('controlSelection').innerHTML=['negative','positive'].map(role=>`<label>${role==='negative'?'Negative':'Positive'} control material<select id="control_${role}"><option value="">${current.report.control_ids[role].length?'Choose a control':'No measured control in input'}</option>${current.report.control_ids[role].map(s=>`<option value="${esc(s)}" ${current.report.control_ids[role].length===1?'selected':''}>${esc(s)}</option>`).join('')}</select></label>`).join('');for(const select of $('controlSelection').querySelectorAll('select'))select.onchange=clearPlan;$('planResult').replaceChildren();notice('Inspection complete. Observations are exploratory; no measurements were corrected.');$('wellDetail').textContent='Select a measured well to inspect it.';}
$('inspect').onclick=()=>busy('inspect',async()=>{invalidate();renderInspection(await api('/api/inspect',input()));});
$('review').onclick=()=>busy('review',async()=>{$('priorities').replaceChildren();$('modelStatus').textContent='Requesting a live review…';try{const v=await api('/api/review',{...input(),objective:$('objective').value,settings:followupSettings()});$('modelStatus').textContent=v.message+(v.model?' Model: '+v.model:'');$('priorities').innerHTML='<p class="small">Source report '+esc(v.source_report_id)+' · '+v.runtime_calls+' runtime calls</p>'+(v.analyses||[]).map(a=>'<article class="finding"><h3>'+esc(a.title)+'</h3><p>'+esc(a.explanation)+'</p><p class="small">'+esc(a.limitations)+'</p><details><summary>Computed evidence · '+esc(a.id)+'</summary><pre class="evidence">'+esc(JSON.stringify(a,null,2))+'</pre></details></article>').join('')+'<h3>'+esc(v.next_action.title)+'</h3><p>'+esc(v.next_action.detail)+'</p><p class="small">Model-selected evidence: '+esc(v.selected_evidence.join(', '))+'</p>'+(v.priorities||[]).map(c=>findingHtml(current.report.findings.find(f=>f.code===c),current.report.facts)).join('');}catch(e){$('modelStatus').textContent='Live review unavailable. Deterministic findings remain available.';throw e;}});
$('plan').onclick=()=>busy('plan',async()=>{layout=null;$('planResult').replaceChildren();const samples=[...$('samples').querySelectorAll('input:checked')].map(x=>x.value);layout=await api('/api/plan',{...input(),samples,budget:Number($('budget').value),seed:Number($('seed').value),controls:Object.fromEntries(['negative','positive'].map(role=>[role,$('control_'+role).value]))});$('planResult').innerHTML=`<p class="small">Layout ${esc(layout.layout_id)} · Source report ${esc(layout.source_report_id)}</p><p><strong>${layout.used} wells allocated · ${layout.unused} budgeted wells unused</strong></p><p>${esc(layout.explanation)}</p>${coverageHtml(layout.coverage)}<label><input type="checkbox" id="approve"> I have reviewed this proposed layout for assay compatibility.</label><p><button id="layoutDownload" disabled>Export reviewed layout CSV</button></p><details><summary>View allocated wells</summary><pre class="evidence">${esc(layout.csv)}</pre></details>`;$('approve').onchange=()=>{$('layoutDownload').disabled=!$('approve').checked;};$('layoutDownload').onclick=()=>busy('layoutDownload',async()=>{
 if(!layout||!$('approve').checked)throw Error('Review the current layout before exporting it.');
 const result=await api('/api/export-plan',{...input(),...followupSettings(),reviewed:true,source_report_id:layout.source_report_id,layout_id:layout.layout_id});
 download(result.filename,result.csv,'text/csv');notice('Reviewed layout prepared for download with its source report, layout ID, seed, and review attestation.');
});notice('Follow-up layout ready for your review.');});
$('reportDownload').onclick=()=>busy('reportDownload',async()=>{
 if(!current)throw Error('Inspect a plate before exporting its handoff note.');
 const reviewed=Boolean(layout&&$('approve')?.checked);
 const result=await api('/api/export-handoff',{...input(),...followupSettings(),notes:$('notes').value,provenance,
   layout_present:Boolean(layout),include_layout:reviewed,reviewed,
   source_report_id:layout?.source_report_id,layout_id:layout?.layout_id});
 download(result.filename,result.text,'text/plain');
 notice(result.includes_reviewed_layout?'Handoff prepared with the reviewed proposal and source identifiers.':'Handoff prepared. Unreviewed well assignments are not included.');
});

function clearPlan(){clearDownload();layout=null;$('planResult').replaceChildren();$('priorities').replaceChildren();$('modelStatus').textContent='Settings changed. Request a new model review if needed.';}
$('budget').oninput=clearPlan;

request('/api/status').then(s=>{if(!s.model_configured){$('modelStatus').textContent='Live model review is not configured. Local analysis and follow-up design are available.';}}).catch(()=>{});

$('seed').oninput=clearPlan;

function followupSettings(){return {samples:[...$('samples').querySelectorAll('input:checked')].map(x=>x.value),budget:Number($('budget').value),seed:Number($('seed').value),controls:Object.fromEntries(['negative','positive'].map(role=>[role,$('control_'+role).value]))};}
$('saveReview').onclick=()=>busy('saveReview',async()=>{
 if(!current)throw Error('Inspect a plate before saving a review file.');
 const session={format:'second-look-review',version:1,analysis_version:current.workflow.analysis_version,report_id:current.workflow.report_id,saved_at:new Date().toISOString(),input:input(),notes:$('notes').value,settings:followupSettings()};
 // Validate the exact portable payload before offering a file that must reopen.
 await api('/api/open-review',{session});
 const json=JSON.stringify(session,null,2);if(new TextEncoder().encode(json).length>1000000)throw Error('The review file would exceed 1 MB. Reduce unused CSV columns or notes before saving.');
 download('second-look-'+current.workflow.report_id+'.secondlook.json',json,'application/json');notice('Review file prepared for download. It includes the original measurements and your notes.');
});
$('reviewFile').onchange=()=>busy('reviewFile',async()=>{
 const file=$('reviewFile').files[0];if(!file)return;if(file.size>1000000)throw Error('Choose a saved review file smaller than 1 MB.');
 let session;try{session=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer()));}catch{throw Error('This file is not readable UTF-8 JSON. Your current review has not been replaced.');}
 // The current page is changed only after server validation and recomputation.
 const result=await api('/api/open-review',{session});const restored=result.session;
 $('csv').value=restored.input.csv;mapping();for(const f of fields)$('map_'+f).value=restored.input.mapping[f];
 renderInspection(result);$('notes').value=restored.notes;noteDrafts.setNotes(restored.notes);$('budget').value=String(restored.settings.budget);$('seed').value=String(restored.settings.seed);
 for(const box of $('samples').querySelectorAll('input'))box.checked=restored.settings.samples.includes(box.value);
 for(const role of ['negative','positive'])$('control_'+role).value=restored.settings.controls[role];
 clearPlan();provenance='Imported review · original source attribution is not verified';$('provenance').textContent=provenance;
 notice([result.message,...result.warnings].join(' '));$('reviewFile').value='';
});

$('objective').onchange=()=>{$('priorities').replaceChildren();$('modelStatus').textContent='Review objective changed. No model review has been performed for this objective.';};

$('notes').oninput=()=>{noteDrafts.setNotes($('notes').value);clearDownload();};

function coverageHtml(coverage){
 if(!coverage)return '';
 return '<section class="decision" aria-label="Observed versus proposed position coverage"><h3>What changes in this repeat?</h3><p>'+esc(coverage.summary)+'</p><div class="table-wrap"><table><caption>'+esc(coverage.question)+'</caption><thead><tr><th scope="col">Material</th><th scope="col">Role</th><th scope="col">Observed edge / interior</th><th scope="col">Proposed edge / interior</th></tr></thead><tbody>'+coverage.materials.map(m=>'<tr><th scope="row">'+esc(m.sample_id)+'</th><td>'+esc(m.role)+'</td><td>'+m.observed.edge+' / '+m.observed.interior+'</td><td>'+m.proposed.edge+' / '+m.proposed.interior+'</td></tr>').join('')+'</tbody></table></div><p class="small">'+esc(coverage.limits)+'</p><details><summary>Check the supporting well assignments</summary><pre class="evidence">'+esc(JSON.stringify(coverage.materials,null,2))+'</pre></details></section>';
}
