// --- helpers ---
const qs = (s)=>document.querySelector(s);
const st = (el,msg)=> el.textContent = msg;


// Local config
const cfg = {
get hfToken(){ return localStorage.getItem('hfToken')||''; },
set hfToken(v){ localStorage.setItem('hfToken', v); },
get model(){ return localStorage.getItem('model')||'Qwen/Qwen2.5-1.5B-Instruct'; },
set model(v){ localStorage.setItem('model', v); },
get backendUrl(){ return localStorage.getItem('backendUrl')||''; },
set backendUrl(v){ localStorage.setItem('backendUrl', v); },
get voiceId(){ return localStorage.getItem('voiceId')||''; },
set voiceId(v){ localStorage.setItem('voiceId', v); },
};


window.addEventListener('DOMContentLoaded', ()=>{
qs('#hfToken').value = cfg.hfToken;
qs('#model').value = cfg.model;
qs('#backendUrl').value = cfg.backendUrl;
qs('#voiceId').value = cfg.voiceId;
});


qs('#btnSaveCfg').onclick = ()=>{
cfg.hfToken = qs('#hfToken').value.trim();
cfg.model = qs('#model').value.trim();
cfg.backendUrl = qs('#backendUrl').value.trim();
cfg.voiceId = qs('#voiceId').value.trim();
alert('Settings saved locally.');
};


// --- 1) Speech-to-text (Urdu title) ---
let recognizing = false; let rec;
qs('#btnRecord').onclick = () => {
if (!('webkitSpeechRecognition' in window)) {
alert('Speech recognition not supported. Type the title manually.');
return;
}
if (!rec) {
rec = new webkitSpeechRecognition();
rec.continuous = false; rec.interimResults = false; rec.maxAlternatives = 1;
rec.onresult = (e)=>{ const t = e.results[0][0].transcript; qs('#title').value = t; st(qs('#sttStatus'),'Done'); };
rec.onerror = (e)=> st(qs('#sttStatus'),'Error: '+ e.error);
rec.onend = ()=>{ recognizing = false; st(qs('#sttStatus'),'Stopped'); };
}
if (recognizing) { rec.stop(); recognizing = false; return; }
rec.lang = qs('#lang').value || 'ur-PK';
rec.start(); recognizing = true; st(qs('#sttStatus'),'Listening…');
};


// --- 2) LLM via Hugging Face Inference API ---
async function hfTextGen(model, token, prompt){
const url = `https://api-inference.huggingface.co/models/${encodeURIComponent(model)}`;
const body = { inputs: prompt, parameters: { max_new_tokens: 1100, temperature: 0.9, do_sample: true } };
const r = await fetch(url, { method:'POST', headers:{ 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(body)});
if (!r.ok) throw new Error('HF API error: '+r.status);
const data = await r.json();
const text = Array.isArray(data) ? data[0]?.generated_text || JSON.stringify(data) : (data?.generated_text || JSON.stringify(data));
return text;
}


};