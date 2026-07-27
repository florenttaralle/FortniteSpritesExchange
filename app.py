"""Sprite Exchange - application FastAPI monofichier.

Installation :
    pip install fastapi uvicorn curl_cffi

Alternative si curl_cffi ne suffit pas :
    pip install playwright
    playwright install chromium

Lancement :
    python sprite_exchange_app.py
Puis ouvrir http://127.0.0.1:8000
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Sprite Exchange", docs_url=None, redoc_url=None)

HTML = '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="color-scheme" content="dark">\n<title>Sprite Exchange</title>\n<style>\n:root{--bg:#080b14;--panel:#101625;--panel2:#151d30;--line:#26324d;--text:#f5f7ff;--muted:#9aa7c2;--accent:#8b5cf6;--accent2:#22d3ee;--good:#34d399;--warn:#f59e0b;--bad:#fb7185;--radius:20px;--shadow:0 18px 50px #0007}\n*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;background:radial-gradient(circle at 15% -10%,#37216a 0,transparent 33%),radial-gradient(circle at 100% 0,#073d57 0,transparent 28%),var(--bg);color:var(--text);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}\nbutton,input,select,textarea{font:inherit}button{cursor:pointer}.shell{width:min(1200px,calc(100% - 28px));margin:auto;padding:30px 0 70px}.top{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:24px}.brand{display:flex;align-items:center;gap:14px}.logo{width:50px;height:50px;border-radius:17px;display:grid;place-items:center;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 10px 35px #7c3aed66;font-size:24px}.brand h1{font-size:clamp(22px,4vw,34px);margin:0;letter-spacing:-.04em}.brand p{margin:2px 0 0;color:var(--muted)}\n.panel{background:linear-gradient(180deg,#121a2bd9,#0d1320e8);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);backdrop-filter:blur(14px)}.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 24px;padding:5px;width:max-content;max-width:100%;background:#0c1220;border:1px solid var(--line);border-radius:15px}.tabs .tab-btn{flex:0 0 auto}.tab-btn{border:0;border-radius:11px;padding:10px 16px;background:transparent;color:var(--muted);font-weight:850;cursor:pointer;transition:.2s}.tab-btn:hover{color:var(--text);background:#161f33}.tab-btn.active{color:white;background:linear-gradient(135deg,var(--accent),#6366f1);box-shadow:0 8px 22px #7c3aed44}.tab-panel{display:none}.tab-panel.active{display:block}.toolbar{display:block;max-width:720px;margin-bottom:22px}.field{display:flex;gap:10px;align-items:center;background:#090e19;border:1px solid var(--line);border-radius:14px;padding:4px 5px 4px 14px}.field input{width:100%;border:0;outline:0;background:transparent;color:var(--text);min-height:38px}.btn{border:0;border-radius:13px;padding:11px 15px;color:white;background:#202a40;font-weight:750;transition:.2s transform,.2s opacity,.2s background}.btn:hover{transform:translateY(-1px);background:#2a3652}.btn.primary{background:linear-gradient(135deg,var(--accent),#6366f1);box-shadow:0 9px 24px #7c3aed44}.btn.good{background:linear-gradient(135deg,#059669,#22c55e)}.btn.ghost{background:transparent;border:1px solid var(--line)}.btn.danger{color:#fecdd3}.btn:disabled{opacity:.45;cursor:not-allowed;transform:none}\n.section-head{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:25px 2px 14px}.section-head h2{margin:0;font-size:20px}.section-head p{margin:3px 0 0;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(265px,1fr));gap:14px}.empty{grid-column:1/-1;text-align:center;padding:50px 18px;color:var(--muted);border:1px dashed var(--line);border-radius:var(--radius)}\n.player{position:relative;padding:17px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(155deg,#182137,#101625);transition:.2s;border-color:.2s,transform:.2s;overflow:hidden}.player:hover{transform:translateY(-2px)}.player.selected{border-color:#8b5cf6;box-shadow:0 0 0 2px #8b5cf633,0 15px 35px #0005}.player.loading:after{content:"";position:absolute;inset:0;background:#101625aa;backdrop-filter:blur(2px)}.spinner{display:none;position:absolute;z-index:3;inset:50% auto auto 50%;width:36px;height:36px;margin:-18px;border:3px solid #ffffff22;border-top-color:var(--accent2);border-radius:50%;animation:spin .8s linear infinite}.player.loading .spinner{display:block}@keyframes spin{to{transform:rotate(360deg)}}\n.player-top{display:flex;gap:12px;align-items:center}.avatar{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#273451,#1b2340);font-weight:900;color:#c4b5fd}.player-name{font-size:17px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.player-id,.small{font-size:12px;color:var(--muted)}.selectbox{margin-left:auto;width:23px;height:23px;border:2px solid #65708a;border-radius:8px;display:grid;place-items:center}.selected .selectbox{background:var(--accent);border-color:var(--accent)}.selected .selectbox:after{content:"✓";font-weight:900}.state{margin:14px 0 10px;color:var(--muted);font-size:13px}.state.ok{color:#a7f3d0}.state.err{color:#fecdd3}.progress-row{margin-top:10px}.progress-meta{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:5px}.bar{height:7px;background:#070b13;border-radius:99px;overflow:hidden}.bar span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,var(--accent),var(--accent2))}.bar.master span{background:linear-gradient(90deg,#f59e0b,#fde047)}.actions{display:flex;gap:7px;margin-top:15px}.actions .btn{padding:8px 10px;font-size:12px;flex:1}\n.generate{margin-top:24px;padding:19px;display:flex;justify-content:space-between;align-items:center;gap:16px}.generate strong{font-size:17px}.generate-actions{display:flex;align-items:center;gap:11px}.generate-spinner{display:none;width:22px;height:22px;border:3px solid #ffffff22;border-top-color:#fff;border-radius:50%;animation:spin .75s linear infinite}.generating .generate-spinner{display:block}.generate p{margin:4px 0 0;color:var(--muted)}.results{margin-top:18px}.summary{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:13px}.pill{padding:7px 11px;border-radius:999px;border:1px solid var(--line);background:#11192a;color:#cbd5e1;font-size:13px}.cycle{padding:17px;margin-bottom:12px}.cycle h3{margin:0 0 13px;font-size:16px}.trade-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:13px}.trade-card{display:grid;grid-template-columns:112px 1fr;min-height:150px;overflow:hidden;border:1px solid #293650;border-radius:18px;background:linear-gradient(145deg,#19233a,#101625);box-shadow:0 10px 28px #0003}.trade-visual{min-height:150px;background:#090e18;position:relative;overflow:hidden;border-right:1px solid #293650}.trade-visual img{width:100%;height:100%;position:absolute;inset:0;object-fit:cover}.trade-visual:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent 55%,#10162599)}.trade-visual .sprite-img-fallback{width:100%;height:100%;border:0;border-radius:0;display:grid;place-items:center;background:linear-gradient(145deg,#121a2b,#090e18);color:#7f8aa3;font-size:34px}.trade-info{padding:16px;display:flex;flex-direction:column;justify-content:center;gap:9px;min-width:0}.trade-line{display:grid;grid-template-columns:34px 1fr;gap:8px;align-items:baseline}.trade-label{color:var(--muted);font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.trade-name{font-size:16px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.trade-sprite-name{margin-top:5px;padding-top:11px;border-top:1px solid #293650;color:#dbeafe;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.trade-exchanged-btn{margin-top:4px;width:100%;padding:9px 12px;border:0;border-radius:11px;background:linear-gradient(135deg,#059669,#22c55e);color:white;font-weight:850;cursor:pointer}.trade-exchanged-btn:hover{filter:brightness(1.08)}.trade-exchanged-btn:disabled{cursor:default;opacity:.75;filter:none}.trade-card.exchanged{border-color:#22c55e88;box-shadow:0 0 0 1px #22c55e33,0 10px 28px #0003}.trade-card.exchanged .trade-exchanged-btn{background:#174c3b;color:#a7f3d0}.no-result{padding:30px;text-align:center;color:var(--muted)}\n.modal{position:fixed;inset:0;z-index:20;background:#03050bcc;display:none;align-items:center;justify-content:center;padding:18px}.modal.open{display:flex}.modal-card{width:min(760px,100%);max-height:88vh;overflow:auto;padding:22px}.modal-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.modal h2{margin:0}.modal label{display:block;color:#cbd5e1;font-weight:700;margin:17px 0 7px}.modal input,.modal textarea{width:100%;background:#080d18;border:1px solid var(--line);border-radius:12px;color:white;padding:11px;outline:0}.modal textarea{min-height:190px;font-family:ui-monospace,monospace;font-size:12px}.hint{font-size:12px;color:var(--muted)}.toast{position:fixed;right:18px;bottom:18px;z-index:50;background:#182137;border:1px solid var(--line);padding:12px 15px;border-radius:13px;box-shadow:var(--shadow);transform:translateY(90px);opacity:0;transition:.25s}.toast.show{transform:none;opacity:1}\n.matrix-wrap{overflow:auto;padding:4px}.matrix-table{width:100%;border-collapse:separate;border-spacing:0;min-width:620px}.matrix-table th,.matrix-table td{padding:12px 14px;text-align:center;border-right:1px solid var(--line);border-bottom:1px solid var(--line);white-space:nowrap}.matrix-table th{position:sticky;top:0;background:#121a2b;color:#cbd5e1;font-size:13px;font-weight:850;z-index:2}.matrix-table th:first-child{left:0;z-index:4;text-align:left}.matrix-table td:first-child{position:sticky;left:0;background:#11192a;text-align:left;font-weight:850;z-index:1}.matrix-table tr:last-child td{border-bottom:0}.matrix-table th:last-child,.matrix-table td:last-child{border-right:0}.matrix-table .diagonal{background:#241a42;color:#ddd6fe;font-weight:900}.matrix-table .unknown{color:var(--muted);font-weight:800}.matrix-table .positive{color:#a7f3d0;font-weight:900}.matrix-table td.matrix-clickable{padding:0}.matrix-cell-btn{display:block;width:100%;min-height:46px;padding:12px 14px;border:0;background:transparent;color:inherit;font-weight:inherit;cursor:pointer}.matrix-cell-btn:hover{background:#ffffff0b}.matrix-cell-btn.active{background:#8b5cf633;box-shadow:inset 0 0 0 2px #8b5cf6}.matrix-empty{padding:38px 20px;text-align:center;color:var(--muted)}.matrix-detail{margin-top:22px}.matrix-detail-head{display:flex;justify-content:space-between;gap:14px;align-items:end;margin:0 2px 13px;flex-wrap:wrap}.matrix-filter{display:flex;gap:7px;padding:4px;background:#0c1220;border:1px solid var(--line);border-radius:12px}.matrix-filter-btn{border:0;border-radius:9px;padding:8px 11px;background:transparent;color:var(--muted);font-weight:800;cursor:pointer}.matrix-filter-btn:hover{color:var(--text);background:#161f33}.matrix-filter-btn.active{color:white;background:linear-gradient(135deg,var(--accent),#6366f1)}.matrix-detail-head h3{margin:0;font-size:18px}.matrix-detail-head p{margin:3px 0 0;color:var(--muted)}.sprite-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:13px}.sprite-card{overflow:hidden;border:1px solid var(--line);border-radius:17px;background:linear-gradient(150deg,#182137,#101625)}.sprite-card-image{aspect-ratio:1/1;background:#090e18;display:grid;place-items:center;overflow:hidden}.sprite-card-image img{width:100%;height:100%;object-fit:cover}.sprite-card-image .sprite-img-fallback{font-size:34px;color:#7f8aa3}.sprite-card-title{padding:11px 12px 7px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sprite-card-origin{margin:0 10px 11px;width:max-content;max-width:calc(100% - 20px);padding:4px 8px;border-radius:999px;border:1px solid #f59e0b66;background:#f59e0b18;color:#fcd34d;font-size:11px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sprite-grid-empty{padding:34px 18px;border:1px dashed var(--line);border-radius:17px;text-align:center;color:var(--muted)}\n@media(max-width:700px){.toolbar{grid-template-columns:1fr}.top{align-items:flex-start}.brand p{display:none}.generate{align-items:stretch;flex-direction:column}.trade-grid{grid-template-columns:1fr}.trade-card{grid-template-columns:96px 1fr;min-height:132px}.trade-visual{min-height:132px}.hide-mobile{display:none}}\n</style>\n</head>\n<body>\n<div class="shell">\n  <header class="top">\n    <div class="brand"><div class="logo">✦</div><div><h1>Sprite Exchange</h1><p>Composez des cycles d’échanges valides et équitables.</p></div></div>\n    <button class="btn ghost" id="settingsBtn">⚙ Réglages</button>\n  </header>\n\n  <nav class="tabs" aria-label="Navigation principale">\n    <button class="tab-btn active" type="button" data-tab="playersTab">Joueurs</button>\n    <button class="tab-btn" type="button" data-tab="matrixTab">Matrice</button>\n    <button class="tab-btn" type="button" data-tab="tradesTab">Échanges</button>\n  </nav>\n\n  <section class="tab-panel active" id="playersTab">\n    <section class="toolbar">\n      <div class="field"><span>#</span><input id="playerId" inputmode="numeric" placeholder="ID Fortnite.GG du joueur"><button class="btn primary" id="addBtn">Ajouter</button></div>\n    </section>\n\n    <div class="section-head"><div><h2>Joueurs</h2><p id="playersSubtitle">0 joueur enregistré</p></div><div style="display:flex;gap:10px;align-items:center"><div class="small hide-mobile">Les données restent dans ce navigateur.</div><button class="btn ghost" id="refreshAllBtn">↻ Tout actualiser</button></div></div>\n    <main class="cards" id="players"></main>\n  </section>\n\n  <section class="tab-panel" id="tradesTab">\n    <section class="panel generate">\n      <div><strong>Générer les échanges</strong><p id="generateHint">Sélectionnez au moins deux joueurs. Chaque joueur peut donner et recevoir au maximum un sprite.</p></div>\n      <div class="generate-actions"><span class="generate-spinner" aria-hidden="true"></span><button class="btn good" id="generateBtn">✦ Générer une proposition</button></div>\n    </section>\n    <section class="results" id="results"></section>\n  </section>\n\n  <section class="tab-panel" id="matrixTab">\n    <div class="section-head">\n      <div><h2>Matrice des possibilités</h2><p>La ligne possède, la colonne ne possède pas. La diagonale indique le total possédé.</p></div>\n    </div>\n    <div class="matrix-wrap panel"><div id="matrixTable"></div></div>\n    <section class="matrix-detail" id="matrixDetail"></section>\n  </section>\n</div>\n\n<div class="modal" id="settingsModal"><div class="panel modal-card">\n  <div class="modal-head"><h2>Réglages et données</h2><button class="btn ghost" data-close>Fermer</button></div>\n  <p class="hint">Les données Fortnite.GG sont récupérées par le serveur FastAPI local. Aucun proxy CORS externe n’est utilisé.</p>\n  <label>Importer une sauvegarde ou les données d’un joueur</label>\n  <textarea id="importText" placeholder=\'Sauvegarde complète, ou {"fortnite_gg_id":"3908468","username":"…","sprites":[…]}\'></textarea>\n  <div class="actions"><button class="btn primary" id="importBtn">Importer</button><button class="btn danger" id="clearBtn">Effacer toutes les données</button></div>\n</div></div>\n\n<div class="toast" id="toast"></div>\n<script>\n\'use strict\';\nconst STORE=\'sprite-exchange-v1\';\nconst DEFAULT_PLAYERS=[\n  {id:\'3908666\',name:\'Joueur 3908666\'},\n  {id:\'3908468\',name:\'Adellame\'}\n];\nconst $=s=>document.querySelector(s);\nlet state=load();\nlet refreshAllRunning=false;\nlet generationRunning=false;\nlet matrixSelection=null;\nlet matrixSpriteFilter=\'all\';\nfunction load(){\n const base={players:[],lastResult:null};\n try{Object.assign(base,JSON.parse(localStorage.getItem(STORE)||\'{}\'))}catch{}\n // Ajoute les joueurs connus sans écraser les données déjà stockées.\n for(const d of DEFAULT_PLAYERS){if(!base.players.some(p=>String(p.id)===d.id))base.players.push({id:d.id,name:d.name,sprites:null,selected:true,loading:false,error:\'\'})}\n // Écarte les anciens instantanés incohérents créés par les versions précédentes.\n for(const p of base.players){\n  p.loading=false;\n  if(Array.isArray(p.sprites)&&p.sprites.length&&!isSnapshotCoherent(p)){p.sprites=null;p.stats=null;p.error=\'Données locales invalides : actualisez ce joueur\';}\n }\n return base\n}\nfunction save(){localStorage.setItem(STORE,JSON.stringify(state));renderMatrix()}\nfunction toast(msg){const t=$(\'#toast\');t.textContent=msg;t.classList.add(\'show\');clearTimeout(t._x);t._x=setTimeout(()=>t.classList.remove(\'show\'),2600)}\nfunction esc(s=\'\'){return String(s).replace(/[&<>"\']/g,c=>({\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#039;\'}[c]))}\nfunction statusNorm(s=\'\'){s=s.toLowerCase().trim();if(s.includes(\'master\'))return\'mastered\';if(s===\'owned\'||s.includes(\'posséd\'))return\'owned\';if(s.includes(\'not owned\')||s.includes(\'missing\')||s.includes(\'manqu\'))return\'missing\';if(s.includes(\'unreleased\'))return\'unreleased\';return s}\nfunction reconcileLocalOwnedOverrides(player){\n const overrides=Array.isArray(player?.localOwnedOverrides)?player.localOwnedOverrides:[];\n if(!Array.isArray(player?.sprites))return;\n for(const sprite of player.sprites){\n  delete sprite.localOnlyOwned;\n  delete sprite.ownershipSource;\n }\n if(!overrides.length){player.localOwnedOverrides=[];return}\n let added=0;\n const remaining=[];\n for(const spriteName of overrides){\n  const sprite=player.sprites.find(s=>s.name===spriteName);\n  if(!sprite){remaining.push(spriteName);continue}\n  // If Fortnite.GG now reports the sprite as owned/mastered, the remote source\n  // has caught up: remove the local override and mark the origin as remote.\n  if(sprite.status===\'owned\'||sprite.status===\'mastered\'){\n   sprite.ownershipSource=\'origin\';\n   continue;\n  }\n  if(sprite.status===\'missing\'){\n   sprite.status=\'owned\';\n   sprite.localOnlyOwned=true;\n   sprite.ownershipSource=\'local\';\n   remaining.push(spriteName);\n   added++;\n  }else{\n   remaining.push(spriteName);\n  }\n }\n player.localOwnedOverrides=remaining;\n if(added&&player.stats)player.stats.owned=Number(player.stats.owned||0)+added;\n}\nfunction isLocallyDeclaredOwned(player,sprite){\n return !!sprite?.localOnlyOwned||(Array.isArray(player?.localOwnedOverrides)&&player.localOwnedOverrides.includes(sprite?.name));\n}\nfunction isSnapshotCoherent(p){\n const sprites=Array.isArray(p?.sprites)?p.sprites:[];\n const stats=p?.stats||{};\n if(!sprites.length||!Number.isFinite(Number(stats.total))||!Number.isFinite(Number(stats.owned))||!Number.isFinite(Number(stats.mastered)))return false;\n const released=sprites.filter(s=>s.status!==\'unreleased\');\n const owned=released.filter(s=>s.status===\'owned\'||s.status===\'mastered\').length;\n const mastered=released.filter(s=>s.status===\'mastered\').length;\n return released.length===Number(stats.total)&&owned===Number(stats.owned)&&mastered===Number(stats.mastered);\n}\nfunction releasedCatalog(){const names=new Set();for(const p of state.players)for(const s of (p.sprites||[]))if(s.status!==\'unreleased\'&&s.name)names.add(s.name);return names}\nfunction counts(p){const released=(p.sprites||[]).filter(s=>s.status!==\'unreleased\'),derivedOwned=released.filter(s=>[\'owned\',\'mastered\'].includes(s.status)).length,derivedMastered=released.filter(s=>s.status===\'mastered\').length,stats=p.stats||{};return {total:Number(stats.total)||released.length,owned:Number.isFinite(Number(stats.owned))?Number(stats.owned):derivedOwned,mastered:Number.isFinite(Number(stats.mastered))?Number(stats.mastered):derivedMastered,detected:released.length,official:!!(stats.total&&Number.isFinite(Number(stats.owned))&&Number.isFinite(Number(stats.mastered)))}}\nfunction isPlayerValid(p){return isSnapshotCoherent(p)&&!p.loading}\nfunction updateGenerateState(){\n const selected=state.players.filter(p=>p.selected),valid=selected.filter(isPlayerValid),invalid=selected.filter(p=>!isPlayerValid(p)),btn=$(\'#generateBtn\'),hint=$(\'#generateHint\');\n const ready=selected.length>=2&&valid.length>=2&&invalid.length===0&&!generationRunning;\n btn.disabled=!ready;\n document.querySelector(\'.generate\')?.classList.toggle(\'generating\',generationRunning);\n if(generationRunning){hint.textContent=\'Génération en cours… recherche des meilleurs cycles.\';btn.textContent=\'Génération…\';btn.title=\'\';return}else btn.textContent=\'✦ Générer une proposition\';\n if(selected.length<2){\n  const missing=2-selected.length;\n  hint.textContent=`Sélectionnez encore ${missing} joueur${missing>1?\'s\':\'\'} pour générer une proposition.`;\n  btn.title=\'Sélectionnez au moins deux joueurs\';\n }else if(invalid.length){\n  const loading=invalid.filter(p=>p.loading).length;\n  const unavailable=invalid.length-loading;\n  const parts=[];\n  if(loading)parts.push(`${loading} actualisation${loading>1?\'s\':\'\'} en cours`);\n  if(unavailable)parts.push(`${unavailable} joueur${unavailable>1?\'s\':\'\'} sans données valides`);\n  hint.textContent=`Génération bloquée : ${parts.join(\' et \')}.`;\n  btn.title=\'Tous les joueurs sélectionnés doivent disposer de données valides et ne pas être en cours d’actualisation\';\n }else{\n  hint.textContent=`${valid.length} joueurs valides sélectionnés. Chaque participant donne une fois et reçoit une fois.`;\n  btn.title=\'\';\n }\n}\nfunction render(){const root=$(\'#players\');const refreshBtn=$(\'#refreshAllBtn\');if(refreshBtn){const loading=state.players.filter(p=>p.loading).length;refreshBtn.disabled=refreshAllRunning||!state.players.length||loading>0;refreshBtn.textContent=refreshAllRunning?`↻ Actualisation…`:\'↻ Tout actualiser\';}$(\'#playersSubtitle\').textContent=`${state.players.length} joueur${state.players.length>1?\'s\':\'\'} enregistré${state.players.length>1?\'s\':\'\'}`;updateGenerateState();if(!state.players.length){root.innerHTML=\'<div class="empty"><b>Aucun joueur pour le moment.</b><br>Ajoutez un identifiant Fortnite.GG pour commencer.</div>\';return}root.innerHTML=state.players.map(p=>{const c=counts(p),has=Array.isArray(p.sprites)&&p.sprites.length,op=c.total?Math.round(c.owned/c.total*100):0,mp=c.total?Math.round(c.mastered/c.total*100):0,partial=has&&c.detected<c.total;return `<article class="player ${p.selected?\'selected\':\'\'} ${p.loading?\'loading\':\'\'}" data-id="${esc(p.id)}"><div class="spinner"></div><div class="player-top"><div class="avatar">${esc((p.name||\'?\').slice(0,2).toUpperCase())}</div><div style="min-width:0"><div class="player-name">${esc(p.name||\'Joueur inconnu\')}</div><div class="player-id">ID ${esc(p.id)}</div></div><div class="selectbox" title="Sélectionner"></div></div><div class="state ${has&&isSnapshotCoherent(p)?\'ok\':p.error?\'err\':\'\'}">${p.error&&has&&isSnapshotCoherent(p)?esc(p.error):p.error?esc(p.error):has?`Données à jour${c.official?\' · compteurs Fortnite.GG\':\' · compteurs calculés\'}${partial?` · liste détaillée incomplète (${c.detected}/${c.total})`:\'\'}`:\'Données non récupérées\'}</div>${has?`<div class="progress-row"><div class="progress-meta"><span>Possédés</span><b>${c.owned} / ${c.total}</b></div><div class="bar"><span style="width:${op}%"></span></div></div><div class="progress-row"><div class="progress-meta"><span>Masterisés</span><b>${c.mastered} / ${c.total}</b></div><div class="bar master"><span style="width:${mp}%"></span></div></div>`:\'\'}<div class="actions"><button class="btn update">↻ Actualiser</button><a class="btn ghost external" href="https://fortnite.gg/sprites?id=${encodeURIComponent(p.id)}" target="_blank" rel="noopener noreferrer">Fortnite.GG ↗</a><button class="btn ghost danger remove">Supprimer</button></div></article>`}).join(\'\')}\n\nasync function fetchPlayer(id){\n const controller=new AbortController();\n const timer=setTimeout(()=>controller.abort(),45000);\n try{\n  const r=await fetch(`/api/player/${encodeURIComponent(id)}?force=true`,{cache:\'no-store\',signal:controller.signal});\n  let payload=null;\n  try{payload=await r.json()}catch{}\n  if(!r.ok)throw new Error(payload?.detail||`HTTP ${r.status}`);\n  if(!payload?.player)throw new Error(\'Réponse serveur invalide\');\n  return payload.player;\n }catch(e){\n  if(e.name===\'AbortError\')throw new Error(\'délai serveur dépassé\');\n  throw e;\n }finally{clearTimeout(timer)}\n}\nfunction parsePage(id,html){\n const looksLikeMarkdown=/^Title:\\s/m.test(html)||/^Markdown Content:\\s*$/m.test(html)||/\\[[^\\]]+\\]\\(https?:\\/\\//.test(html);\n const doc=new DOMParser().parseFromString(html,\'text/html\');\n // Jina renvoie du Markdown brut. DOMParser peut en fusionner les lignes :\n // dans ce cas il faut impérativement parser la réponse originale.\n const text=looksLikeMarkdown?html:(doc.body.innerText||doc.body.textContent||html||\'\');\n const lines=text.split(/\\r?\\n/).map(x=>x.trim()).filter(Boolean);\n\n let name=\'\';\n const nameText=lines.slice(0,80).join(\'\\n\');\n const nm=nameText.match(/(?:#+\\s*)?(?:!?\\[[^\\]]*\\]\\([^)]*\\)\\s*)?([^\\n]+?)(?:\'s|’s)\\s+Sprites/i);\n if(nm)name=nm[1].replace(/^Title:\\s*/i,\'\').replace(/^#+\\s*/,\'\').trim();\n if(!name&&doc.title)name=doc.title.replace(/^Title:\\s*/i,\'\').replace(/[\'’]s Sprites.*$/i,\'\').trim();\n if(!name)throw new Error(\'Nom du joueur introuvable\');\n\n // Compteurs officiels : "45 / 91", puis "Owned", puis "14 / 91", puis "Mastered".\n let owned=null,mastered=null,total=null;\n for(let i=0;i<Math.min(lines.length,180);i++){\n  const label=lines[i].replace(/[*_`#]/g,\'\').trim();\n  if(!/^(Owned|Mastered)$/i.test(label))continue;\n  for(let j=i-1;j>=Math.max(0,i-6);j--){\n   const cm=lines[j].replace(/[*_`]/g,\'\').match(/^(\\d+)\\s*\\/\\s*(\\d+)$/);\n   if(!cm)continue;\n   if(/^Owned$/i.test(label))owned=Number(cm[1]);else mastered=Number(cm[1]);\n   total=Number(cm[2]);\n   break;\n  }\n }\n if(!Number.isFinite(owned)||!Number.isFinite(mastered)||!Number.isFinite(total)){\n  throw new Error(\'Compteurs Fortnite.GG introuvables\');\n }\n\n const validStatus=/^(Not owned|Owned|Mastered|Unreleased)$/i;\n const cleanStatus=v=>statusNorm(v.replace(/[*_`]/g,\'\').trim());\n const sprites=[];\n const seen=new Set();\n // On commence après les filtres, pour ne pas confondre le bouton "Owned" avec un statut.\n let contentStart=lines.findIndex(l=>/Show unreleased/i.test(l));\n if(contentStart<0)contentStart=0;\n\n for(let i=contentStart+1;i<lines.length;i++){\n  const rawStatus=lines[i].replace(/[*_`]/g,\'\').trim();\n  if(!validStatus.test(rawStatus))continue;\n\n  let spriteName=\'\',imageUrl=\'\';\n  // Le nom est le lien Markdown le plus proche placé avant le statut.\n  for(let j=i-1;j>=Math.max(contentStart,i-12);j--){\n   const image=lines[j].match(/^!\\[([^\\]]*)\\]\\((https?:\\/\\/[^)\\s]+)(?:\\s+[^)]*)?\\)$/);\n   if(image&&!imageUrl){imageUrl=image[2];continue}\n   const link=lines[j].match(/^\\[([^\\]]+)\\]\\((https?:\\/\\/[^)\\s]+)(?:\\s+[^)]*)?\\)$/);\n   if(link&&!/^Image$/i.test(link[1])){spriteName=link[1].trim();break}\n  }\n  // Certaines réponses Jina mettent le lien et la rareté sur la même ligne.\n  if(!spriteName){\n   for(let j=i-1;j>=Math.max(contentStart,i-12);j--){\n    const link=lines[j].match(/(?:^|\\s)\\[([^\\]]+)\\]\\((https?:\\/\\/[^)\\s]+)(?:\\s+[^)]*)?\\)/);\n    if(link&&!/^Image$/i.test(link[1])){spriteName=link[1].trim();break}\n   }\n  }\n  if(!spriteName||seen.has(spriteName))continue;\n  seen.add(spriteName);\n  sprites.push({name:spriteName,imageUrl,status:cleanStatus(rawStatus)});\n }\n\n if(!sprites.length)throw new Error(\'Aucun sprite détecté dans la page\');\n const released=sprites.filter(s=>s.status!==\'unreleased\');\n const derivedOwned=released.filter(s=>s.status===\'owned\'||s.status===\'mastered\').length;\n const derivedMastered=released.filter(s=>s.status===\'mastered\').length;\n\n // Ne jamais stocker une réponse partielle ou mal interprétée.\n if(released.length!==total)throw new Error(`liste détaillée incohérente (${released.length}/${total} sprites publiés)`);\n if(derivedOwned!==owned)throw new Error(`compteur possédé incohérent (${derivedOwned}/${owned})`);\n if(derivedMastered!==mastered)throw new Error(`compteur masterisé incohérent (${derivedMastered}/${mastered})`);\n\n return {id:String(id),name,sprites,stats:{owned,mastered,total},updatedAt:new Date().toISOString()}\n}\nasync function updatePlayer(id,{silent=false}={}){const p=state.players.find(x=>x.id===String(id));if(!p)return false;const hadValid=isSnapshotCoherent(p);const localOwnedOverrides=[...(p.localOwnedOverrides||[])];p.loading=true;p.error=\'\';render();try{const fresh=await fetchPlayer(id);Object.assign(p,fresh);p.localOwnedOverrides=localOwnedOverrides;reconcileLocalOwnedOverrides(p);p.error=\'\';if(!silent)toast(`${p.name} actualisé`);return true}catch(e){p.error=hadValid?`Actualisation échouée · dernières données valides conservées`:`Échec de récupération : ${e.message}`;if(!silent)toast(hadValid?\'Actualisation échouée — anciennes données conservées\':\'Actualisation impossible\');return false}finally{p.loading=false;save();render()}}\nasync function refreshAllPlayers(){if(refreshAllRunning||!state.players.length)return;refreshAllRunning=true;render();let ok=0;for(let i=0;i<state.players.length;i++){const p=state.players[i];const btn=$(\'#refreshAllBtn\');if(btn)btn.textContent=`↻ ${i+1} / ${state.players.length}`;if(await updatePlayer(p.id,{silent:true}))ok++}refreshAllRunning=false;render();toast(`${ok} joueur${ok>1?\'s\':\'\'} actualisé${ok>1?\'s\':\'\'} sur ${state.players.length}`)}\n\nfunction addPlayer(){const id=$(\'#playerId\').value.trim();if(!/^\\d+$/.test(id))return toast(\'Saisissez un identifiant numérique\');if(state.players.some(p=>p.id===id))return toast(\'Ce joueur existe déjà\');state.players.push({id,name:\'Joueur inconnu\',sprites:null,selected:true,loading:false,error:\'\'});$(\'#playerId\').value=\'\';save();render();updatePlayer(id)}\nfunction adjacency(players){const map=new Map(players.map((p,i)=>[p.id,i]));return players.map(g=>players.map(r=>g.id!==r.id&&(g.sprites||[]).some(s=>[\'owned\',\'mastered\'].includes(s.status)&&r.sprites?.some(t=>t.name===s.name&&t.status===\'missing\'))))}\nfunction shuffledCopy(value){const out=Array.isArray(value)?value.slice():Array.from(value||[]);for(let i=out.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));const tmp=out[i];out[i]=out[j];out[j]=tmp}return out}\n// Affectation maximale en O(n³). Chaque joueur est à la fois donneur (ligne) et receveur (colonne).\n// Une diagonale i→i signifie « joueur exclu ». Toute autre arête valide vaut beaucoup plus,\n// donc l\'affectation maximise d\'abord le nombre de participants. Un léger bruit aléatoire\n// départage les solutions optimales pour varier les propositions.\nfunction hungarianMin(cost){const n=cost.length,u=Array(n+1).fill(0),v=Array(n+1).fill(0),p=Array(n+1).fill(0),way=Array(n+1).fill(0);for(let i=1;i<=n;i++){p[0]=i;let j0=0,minv=Array(n+1).fill(Infinity),used=Array(n+1).fill(false);do{used[j0]=true;const i0=p[j0];let delta=Infinity,j1=0;for(let j=1;j<=n;j++)if(!used[j]){const cur=cost[i0-1][j-1]-u[i0]-v[j];if(cur<minv[j]){minv[j]=cur;way[j]=j0}if(minv[j]<delta){delta=minv[j];j1=j}}for(let j=0;j<=n;j++)if(used[j]){u[p[j]]+=delta;v[j]-=delta}else minv[j]-=delta;j0=j1}while(p[j0]!==0);do{const j1=way[j0];p[j0]=p[j1];j0=j1}while(j0)}const rowToCol=Array(n).fill(-1);for(let j=1;j<=n;j++)if(p[j])rowToCol[p[j]-1]=j-1;return rowToCol}\nfunction maximumMatching(adj){\n const giverCount=adj.length,receiverCount=adj.length,receiverToGiver=Array(receiverCount).fill(-1);\n function tryAssign(giverIndex,visitedReceivers){\n  const possibleReceivers=shuffledCopy(Array.from({length:receiverCount},(_,receiverIndex)=>receiverIndex).filter(receiverIndex=>adj[giverIndex][receiverIndex]));\n  for(const receiverIndex of possibleReceivers){\n   if(visitedReceivers.has(receiverIndex))continue;\n   visitedReceivers.add(receiverIndex);\n   const previousGiver=receiverToGiver[receiverIndex];\n   if(previousGiver===-1||tryAssign(previousGiver,visitedReceivers)){receiverToGiver[receiverIndex]=giverIndex;return true}\n  }\n  return false\n }\n const giverOrder=shuffledCopy(Array.from({length:giverCount},(_,index)=>index));\n for(const giverIndex of giverOrder)tryAssign(giverIndex,new Set());\n const matches=[];\n for(let receiverIndex=0;receiverIndex<receiverToGiver.length;receiverIndex++){\n  const giverIndex=receiverToGiver[receiverIndex];\n  if(giverIndex!==-1)matches.push({giverIndex,receiverIndex})\n }\n return shuffledCopy(matches)\n}\nfunction spriteImageUrl(sprite){const raw=String(sprite?.imageUrl||sprite?.image_url||\'\').trim();if(!raw)return \'\';if(raw.startsWith(\'//\'))return \'https:\'+raw;if(raw.startsWith(\'/\'))return \'https://fortnite.gg\'+raw;return raw}function chooseSprite(g,r){const options=(g.sprites||[]).filter(s=>[\'owned\',\'mastered\'].includes(s.status)&&r.sprites?.some(t=>t.name===s.name&&t.status===\'missing\'));return options[Math.floor(Math.random()*options.length)]}\nasync function generate(){\n const selected=state.players.filter(player=>player.selected);\n if(selected.length<2)return toast(\'Sélectionnez au moins deux joueurs\');\n if(selected.some(player=>player.loading))return toast(\'Attendez la fin des actualisations\');\n if(selected.some(player=>!isPlayerValid(player)))return toast(\'Tous les joueurs sélectionnés doivent avoir des données valides\');\n if(generationRunning)return;\n generationRunning=true;updateGenerateState();\n await new Promise(resolve=>setTimeout(resolve,40));\n try{\n  const players=selected,adj=adjacency(players),matches=maximumMatching(adj);\n  const trades=matches.map(({giverIndex,receiverIndex})=>{\n   const giver=players[giverIndex],receiver=players[receiverIndex],sprite=chooseSprite(giver,receiver);\n   if(!sprite)return null;\n   return {giver:giver.name,giverId:giver.id,receiver:receiver.name,receiverId:receiver.id,sprite}\n  }).filter(Boolean);\n  const participatingIds=new Set();\n  for(const trade of trades){participatingIds.add(trade.giverId);participatingIds.add(trade.receiverId)}\n  const result={createdAt:new Date().toISOString(),trades,excluded:players.filter(player=>!participatingIds.has(player.id)).map(player=>player.name)};\n  state.lastResult=result;save();renderResult(result);\n  if(!trades.length)toast(\'Aucun échange compatible trouvé\')\n }catch(error){console.error(\'Generation failed\',error);toast(`Échec de génération : ${error?.message||error}`)}\n finally{generationRunning=false;updateGenerateState()}\n}\nfunction markTradeExchanged(tradeIndex){\n const result=state.lastResult;\n const trades=Array.isArray(result?.trades)?result.trades:Array.isArray(result?.cycles)?result.cycles.flat():[];\n const trade=trades[tradeIndex];\n if(!trade||trade.exchanged)return;\n const receiver=state.players.find(player=>player.id===String(trade.receiverId));\n if(!receiver||!isPlayerValid(receiver))return toast(\'Les données du joueur destinataire ne sont pas disponibles\');\n const spriteName=trade.sprite?.name;\n const sprite=receiver.sprites.find(item=>item.name===spriteName);\n if(!sprite)return toast(`Sprite introuvable dans la collection de ${receiver.name}`);\n if(sprite.status===\'missing\'){\n  sprite.status=\'owned\';\n  sprite.localOnlyOwned=true;\n  sprite.ownershipSource=\'local\';\n  receiver.stats={...(receiver.stats||{})};\n  receiver.stats.owned=Number(receiver.stats.owned||0)+1;\n }\n receiver.localOwnedOverrides=Array.from(new Set([...(receiver.localOwnedOverrides||[]),spriteName]));\n trade.exchanged=true;\n trade.exchangedAt=new Date().toISOString();\n receiver.updatedAt=new Date().toISOString();\n save();\n render();\n renderResult(result);\n toast(`${spriteName} ajouté à la collection de ${receiver.name}`);\n}\nfunction renderResult(result=state.lastResult){\n const root=$(\'#results\');\n if(!result){root.innerHTML=\'\';return}\n const trades=Array.isArray(result.trades)?result.trades:Array.isArray(result.cycles)?result.cycles.flat():[];\n const participants=new Set();\n for(const trade of trades){participants.add(trade.giverId||trade.giver);participants.add(trade.receiverId||trade.receiver)}\n const tradeCards=trades.map((trade,index)=>{\n  const imageUrl=spriteImageUrl(trade.sprite),spriteName=trade.sprite?.name||\'Sprite\';\n  const image=imageUrl?`<img src="${esc(imageUrl)}" alt="${esc(spriteName)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.outerHTML=\'<span class=&quot;sprite-img-fallback&quot; aria-hidden=&quot;true&quot;>◇</span>\'">`:`<span class="sprite-img-fallback" aria-hidden="true">◇</span>`;\n  return `<article class="trade-card ${trade.exchanged?\'exchanged\':\'\'}"><div class="trade-visual">${image}</div><div class="trade-info"><div class="trade-line"><span class="trade-label">De</span><span class="trade-name">${esc(trade.giver)}</span></div><div class="trade-line"><span class="trade-label">À</span><span class="trade-name">${esc(trade.receiver)}</span></div><div class="trade-sprite-name" title="${esc(spriteName)}">${esc(spriteName)}</div><button type="button" class="trade-exchanged-btn" data-trade-index="${index}" ${trade.exchanged?\'disabled\':\'\'}>${trade.exchanged?\'✓ Exchanged\':\'Exchanged\'}</button></div></article>`\n }).join(\'\');\n const exchangedCount=trades.filter(trade=>trade.exchanged).length;\n root.innerHTML=`<div class="summary"><span class="pill">${trades.length} échange${trades.length>1?\'s\':\'\'}</span><span class="pill">${participants.size} joueur${participants.size>1?\'s\':\'\'} impliqué${participants.size>1?\'s\':\'\'}</span>${exchangedCount?`<span class="pill">${exchangedCount} confirmé${exchangedCount>1?\'s\':\'\'}</span>`:\'\'}${result.excluded?.length?`<span class="pill">${result.excluded.length} sans échange</span>`:\'\'}</div>${trades.length?`<div class="trade-grid">${tradeCards}</div>`:`<div class="panel no-result">Aucun échange valide n’a été trouvé pour cette sélection.</div>`}${result.excluded?.length?`<div class="small" style="padding:12px 3px">Sans échange : ${result.excluded.map(esc).join(\', \')}</div>`:\'\'}`\n}\n\nfunction playerOwnedNames(player){\n if(!isPlayerValid(player))return null;\n return new Set((player.sprites||[]).filter(sprite=>[\'owned\',\'mastered\'].includes(sprite.status)).map(sprite=>sprite.name));\n}\nfunction matrixSprites(rowPlayer,columnPlayer){\n if(!isPlayerValid(rowPlayer)||!isPlayerValid(columnPlayer))return null;\n const owned=(rowPlayer.sprites||[]).filter(s=>s.status===\'owned\'||s.status===\'mastered\');\n if(rowPlayer.id===columnPlayer.id)return owned.slice().sort((a,b)=>a.name.localeCompare(b.name,\'fr\'));\n const columnStatuses=new Map((columnPlayer.sprites||[]).map(s=>[s.name,s.status]));\n return owned.filter(s=>columnStatuses.get(s.name)===\'missing\').sort((a,b)=>a.name.localeCompare(b.name,\'fr\'));\n}\nfunction renderMatrixDetail(){\n const root=$(\'#matrixDetail\'); if(!root)return;\n if(!matrixSelection){root.innerHTML=\'<div class="sprite-grid-empty">Cliquez sur une cellule de la matrice pour afficher les sprites correspondants.</div>\';return}\n const rowPlayer=state.players.find(p=>p.id===matrixSelection.rowId),columnPlayer=state.players.find(p=>p.id===matrixSelection.columnId);\n if(!rowPlayer||!columnPlayer){matrixSelection=null;renderMatrixDetail();return}\n const sprites=matrixSprites(rowPlayer,columnPlayer);\n if(sprites===null){root.innerHTML=`<div class="sprite-grid-empty">Les données de ${esc(rowPlayer.name)} ou ${esc(columnPlayer.name)} ne sont pas encore disponibles.</div>`;return}\n const description=rowPlayer.id===columnPlayer.id?`Sprites possédés par ${esc(rowPlayer.name)}`:`Sprites possédés par ${esc(rowPlayer.name)} et manquants à ${esc(columnPlayer.name)}`;\n const localCount=sprites.filter(sprite=>isLocallyDeclaredOwned(rowPlayer,sprite)).length;\n const visibleSprites=matrixSpriteFilter===\'local\'?sprites.filter(sprite=>isLocallyDeclaredOwned(rowPlayer,sprite)):sprites;\n const cards=visibleSprites.map(sprite=>{const imageUrl=spriteImageUrl(sprite),media=imageUrl?`<img src="${esc(imageUrl)}" alt="${esc(sprite.name)}" loading="lazy" referrerpolicy="no-referrer">`:\'<span class="sprite-img-fallback" aria-hidden="true">◇</span>\';const localBadge=isLocallyDeclaredOwned(rowPlayer,sprite)?\'<div class="sprite-card-origin" title="Possession déclarée dans cette application, pas encore confirmée par Fortnite.GG">Local uniquement</div>\':\'\';return `<article class="sprite-card"><div class="sprite-card-image">${media}</div><div class="sprite-card-title" title="${esc(sprite.name)}">${esc(sprite.name)}</div>${localBadge}</article>`}).join(\'\');\n root.innerHTML=`<div class="matrix-detail-head"><div><h3>${description}</h3><p>${visibleSprites.length} sprite${visibleSprites.length>1?\'s\':\'\'} affiché${visibleSprites.length>1?\'s\':\'\'} sur ${sprites.length}${localCount?` · ${localCount} déclaré${localCount>1?\'s\':\'\'} localement`:\'\'}</p></div><div class="matrix-filter" role="group" aria-label="Filtrer les sprites"><button type="button" class="matrix-filter-btn ${matrixSpriteFilter===\'all\'?\'active\':\'\'}" data-matrix-filter="all">Tous</button><button type="button" class="matrix-filter-btn ${matrixSpriteFilter===\'local\'?\'active\':\'\'}" data-matrix-filter="local">Locaux uniquement</button></div></div>${visibleSprites.length?`<div class="sprite-grid">${cards}</div>`:`<div class="sprite-grid-empty">${matrixSpriteFilter===\'local\'?\'Aucun sprite déclaré uniquement en local.\':\'Aucun sprite correspondant.\'}</div>`}`;\n}\nfunction renderMatrix(){\n const root=$(\'#matrixTable\'); if(!root)return; const players=state.players;\n if(!players.length){root.innerHTML=\'<div class="matrix-empty">Ajoutez des joueurs pour afficher la matrice.</div>\';matrixSelection=null;renderMatrixDetail();return}\n const ownedSets=players.map(player=>playerOwnedNames(player));\n const header=players.map(player=>`<th scope="col" title="${esc(player.name)}">${esc(player.name)}</th>`).join(\'\');\n const rows=players.map((linePlayer,i)=>{const cells=players.map((columnPlayer,j)=>{const lineOwned=ownedSets[i],columnOwned=ownedSets[j];if(!lineOwned||!columnOwned)return \'<td class="unknown" title="Données indisponibles">?</td>\';let count,className=\'\',title;if(i===j){count=lineOwned.size;className=\'diagonal\';title=`Sprites possédés par ${linePlayer.name}`}else{count=0;for(const spriteName of lineOwned)if(!columnOwned.has(spriteName))count++;className=count>0?\'positive\':\'\';title=`${linePlayer.name} possède ${count} sprite(s) que ${columnPlayer.name} ne possède pas`}const active=matrixSelection?.rowId===linePlayer.id&&matrixSelection?.columnId===columnPlayer.id;return `<td class="matrix-clickable ${className}"><button type="button" class="matrix-cell-btn ${active?\'active\':\'\'}" data-row-id="${esc(linePlayer.id)}" data-column-id="${esc(columnPlayer.id)}" title="${esc(title)}">${count}</button></td>`}).join(\'\');return `<tr><td title="${esc(linePlayer.name)}">${esc(linePlayer.name)}</td>${cells}</tr>`}).join(\'\');\n root.innerHTML=`<table class="matrix-table"><thead><tr><th scope="col">Possède ↓ / Manque à →</th>${header}</tr></thead><tbody>${rows}</tbody></table>`;renderMatrixDetail();\n}\n\nfunction activateTab(tabId){document.querySelectorAll(\'.tab-btn\').forEach(b=>b.classList.toggle(\'active\',b.dataset.tab===tabId));document.querySelectorAll(\'.tab-panel\').forEach(p=>p.classList.toggle(\'active\',p.id===tabId));localStorage.setItem(STORE+\'-tab\',tabId);if(tabId===\'matrixTab\')renderMatrix()}\ndocument.querySelectorAll(\'.tab-btn\').forEach(b=>b.onclick=()=>activateTab(b.dataset.tab));const validTabs=new Set([\'playersTab\',\'matrixTab\',\'tradesTab\']);let savedTab=localStorage.getItem(STORE+\'-tab\')||\'playersTab\';if(savedTab===\'exchangeTab\')savedTab=\'tradesTab\';if(!validTabs.has(savedTab))savedTab=\'playersTab\';activateTab(savedTab);\n$(\'#matrixTable\').onclick=e=>{const button=e.target.closest(\'.matrix-cell-btn\');if(!button)return;matrixSelection={rowId:button.dataset.rowId,columnId:button.dataset.columnId};renderMatrix();};\n$(\'#matrixDetail\').onclick=e=>{const button=e.target.closest(\'[data-matrix-filter]\');if(!button)return;matrixSpriteFilter=button.dataset.matrixFilter===\'local\'?\'local\':\'all\';renderMatrixDetail();};\n$(\'#addBtn\').onclick=addPlayer;$(\'#playerId\').onkeydown=e=>{if(e.key===\'Enter\')addPlayer()};$(\'#generateBtn\').onclick=generate;$(\'#refreshAllBtn\').onclick=refreshAllPlayers;\n$(\'#results\').onclick=e=>{const button=e.target.closest(\'.trade-exchanged-btn\');if(!button)return;markTradeExchanged(Number(button.dataset.tradeIndex));};\n$(\'#players\').onclick=e=>{const card=e.target.closest(\'.player\');if(!card)return;const p=state.players.find(x=>x.id===card.dataset.id);if(e.target.closest(\'.update\'))return updatePlayer(p.id);if(e.target.closest(\'.external\'))return;if(e.target.closest(\'.remove\')){state.players=state.players.filter(x=>x!==p);save();render();return}p.selected=!p.selected;save();render()};\nfunction openSettings(){$(\'#settingsModal\').classList.add(\'open\')}$(\'#settingsBtn\').onclick=openSettings;document.querySelector(\'[data-close]\').onclick=()=>{$(\'#settingsModal\').classList.remove(\'open\')};\n$(\'#settingsModal\').onclick=e=>{if(e.target===$(\'#settingsModal\'))$(\'#settingsModal\').classList.remove(\'open\')};\n$(\'#importBtn\').onclick=()=>{try{const d=JSON.parse($(\'#importText\').value);if(Array.isArray(d.players)){state=Object.assign(state,d)}else{const id=String(d.fortnite_gg_id||d.id||\'\');if(!id)throw Error(\'ID absent\');const sprites=(d.sprites||[]).map(s=>({name:s.name,imageUrl:s.image_url||s.imageUrl||\'\',status:statusNorm(s.status)}));const p=state.players.find(x=>x.id===id),data={id,name:d.username||d.name||\'Joueur inconnu\',sprites,selected:true,updatedAt:new Date().toISOString()};p?Object.assign(p,data):state.players.push(data)}save();render();$(\'#settingsModal\').classList.remove(\'open\');toast(\'Import terminé\')}catch(e){toast(`JSON invalide : ${e.message}`)}};\n$(\'#clearBtn\').onclick=()=>{if(confirm(\'Effacer tous les joueurs et résultats ?\')){localStorage.removeItem(STORE);state=load();save();render();renderResult();$(\'#settingsModal\').classList.remove(\'open\')}};\nsave();render();renderResult();renderMatrix();\n</script>\n</body>\n</html>\n'

# Petit cache mémoire pour éviter de solliciter Fortnite.GG à répétition.
_CACHE: dict[str, tuple[float, str]] = {}
_CACHE_TTL_SECONDS = 120
_ID_RE = re.compile(r"^[0-9]{1,20}$")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(HTML, headers={"Cache-Control": "no-store"})


def _validate_fortnite_html(body: str, player_id: str) -> None:
    """Refuse les pages de challenge et les réponses manifestement partielles."""
    if len(body) < 5_000:
        raise RuntimeError(f"réponse trop courte ({len(body)} octets)")
    lowered = body.lower()
    challenge_markers = (
        "cf-chl-", "cloudflare ray id", "just a moment", "attention required",
        "verify you are human", "captcha"
    )
    if any(marker in lowered for marker in challenge_markers):
        raise RuntimeError("Fortnite.GG a renvoyé une page anti-bot")
    if "sprites" not in lowered:
        raise RuntimeError("la page reçue ne contient pas les données de sprites")


def _fetch_with_curl_cffi(url: str, headers: dict[str, str]) -> str:
    """Requête avec une empreinte TLS de navigateur réel."""
    try:
        from curl_cffi import requests as curl_requests
    except ImportError as exc:
        raise RuntimeError(
            "curl_cffi n'est pas installé. Exécutez : pip install curl_cffi"
        ) from exc

    response = curl_requests.get(
        url,
        headers=headers,
        impersonate="chrome",
        timeout=30,
        allow_redirects=True,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code} via curl_cffi")
    return response.text


async def _fetch_with_playwright(url: str) -> str:
    """Secours facultatif : charge la page dans un véritable Chromium."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright n'est pas installé (secours facultatif)"
        ) from exc

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="fr-FR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            if response is None:
                raise RuntimeError("aucune réponse du navigateur")
            if response.status >= 400:
                raise RuntimeError(f"HTTP {response.status} via Chromium")
            await page.wait_for_timeout(1200)
            return await page.content()
        finally:
            await browser.close()


def _parse_player_html(body: str, player_id: str) -> dict[str, Any]:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("beautifulsoup4 n'est pas installé. Exécutez : pip install beautifulsoup4") from exc
    soup = BeautifulSoup(body, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    m = re.search(r"(.+?)(?:'s|’s)\s+Sprites", title, re.I)
    name = m.group(1).strip() if m else f"Joueur {player_id}"
    text = soup.get_text("\n", strip=True)
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*\n\s*Owned\s*\n\s*(\d+)\s*/\s*(\d+)\s*\n\s*Mastered", text, re.I)
    if not m:
        m = re.search(r"(\d+)\s*/\s*(\d+)\s+Owned\s+(\d+)\s*/\s*(\d+)\s+Mastered", re.sub(r"\s+", " ", text), re.I)
    if not m:
        raise RuntimeError("Compteurs Fortnite.GG introuvables dans le HTML reçu")
    owned, total, mastered, total2 = map(int, m.groups())
    if total != total2:
        raise RuntimeError(f"Totaux incohérents ({total} et {total2})")
    statuses = {"not owned":"missing", "owned":"owned", "mastered":"mastered", "unreleased":"unreleased"}
    sprites, seen = [], set()

    # Un statut doit être rattaché à une carte de sprite locale. Les anciennes
    # versions remontaient jusqu'à 10 ancêtres : le bouton de filtre "Owned"
    # pouvait alors atteindre le conteneur de toute la page et être associé au
    # premier sprite, créant typiquement un faux 46/45.
    for node in soup.find_all(string=lambda x: isinstance(x, str) and x.strip().lower() in statuses):
        raw = node.strip().lower()
        anchor = None
        img = None
        parent = node.parent

        for _ in range(6):
            if parent is None:
                break

            local_imgs = parent.find_all("img")
            local_links = parent.find_all("a", href=True)
            sprite_links = []
            for a in local_links:
                label = a.get_text(" ", strip=True)
                href = str(a.get("href", ""))
                if not label or label.lower() in {"owned", "missing", "all", "image"}:
                    continue
                if "sprite" in href.lower():
                    sprite_links.append(a)

            # Une vraie carte contient normalement un seul lien de sprite et
            # au moins une image. Refuser les grands conteneurs évite les
            # contrôles globaux de filtre/navigation.
            if len(sprite_links) == 1 and local_imgs and len(local_links) <= 4:
                anchor = sprite_links[0]
                img = local_imgs[0]
                break

            # Dès que le conteneur devient large, ne pas remonter davantage.
            if len(local_links) > 8 or len(local_imgs) > 4:
                break
            parent = parent.parent

        if not anchor:
            continue

        sprite_name = anchor.get_text(" ", strip=True)
        if not sprite_name or sprite_name in seen:
            continue

        image_url = ""
        if img:
            for attr in ("src", "data-src", "data-lazy-src", "data-original"):
                value = img.get(attr)
                if value:
                    image_url = urljoin("https://fortnite.gg", value)
                    break

        seen.add(sprite_name)
        sprites.append({"name": sprite_name, "imageUrl": image_url, "status": statuses[raw]})
    released = [x for x in sprites if x["status"] != "unreleased"]
    d_owned = sum(x["status"] in {"owned", "mastered"} for x in released)
    d_mastered = sum(x["status"] == "mastered" for x in released)

    # Le catalogue et la possession doivent être exacts : ils déterminent les
    # échanges possibles. En revanche, Fortnite.GG peut représenter un badge
    # "Mastered" d'une manière différente sur une carte isolée. Le compteur
    # officiel de la page reste alors correct tandis que le parseur détaillé
    # trouve parfois un élément de moins. Cela ne change pas l'algorithme,
    # puisque "owned" et "mastered" signifient tous deux que le sprite est
    # possédé et peut être donné.
    if len(released) != total or d_owned != owned:
        raise RuntimeError(
            f"Liste détaillée incohérente : {len(released)}/{total} sprites, "
            f"{d_owned}/{owned} possédés"
        )

    warnings = []
    if d_mastered != mastered:
        warnings.append(
            f"Le détail HTML indique {d_mastered} sprite(s) masterisé(s), "
            f"mais le compteur officiel en indique {mastered}. "
            "Le compteur officiel est utilisé."
        )

    from datetime import datetime, timezone
    return {
        "id": player_id,
        "name": name,
        "sprites": sprites,
        "stats": {"owned": owned, "mastered": mastered, "total": total},
        "parseStats": {
            "owned": d_owned,
            "mastered": d_mastered,
            "total": len(released),
        },
        "warnings": warnings,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/player/{player_id}")
async def player_page(player_id: str, force: bool = False) -> JSONResponse:
    if not _ID_RE.fullmatch(player_id):
        raise HTTPException(status_code=400, detail="Identifiant joueur invalide")

    now = time.monotonic()
    cached = _CACHE.get(player_id)
    if not force and cached and now - cached[0] < _CACHE_TTL_SECONDS:
        return JSONResponse({"id": player_id, "player": _parse_player_html(cached[1], player_id), "cached": True})

    # Ne pas ajouter de paramètre aléatoire : Fortnite.GG peut considérer ces URL
    # répétées et atypiques comme du trafic automatisé.
    target = f"https://fortnite.gg/sprites?id={player_id}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Referer": "https://fortnite.gg/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
    }

    errors: list[str] = []

    # Méthode principale : curl_cffi reproduit l'empreinte TLS d'un navigateur,
    # contrairement à httpx qui peut être bloqué avant même l'analyse des headers.
    for attempt in range(1, 4):
        try:
            body = await asyncio.to_thread(_fetch_with_curl_cffi, target, headers)
            _validate_fortnite_html(body, player_id)
            _CACHE[player_id] = (time.monotonic(), body)
            return JSONResponse({"id": player_id, "player": _parse_player_html(body, player_id), "cached": False, "method": "curl_cffi"})
        except Exception as exc:
            errors.append(f"curl_cffi {attempt}/3 : {exc}")
            if attempt < 3:
                await asyncio.sleep(0.8 * attempt)

    # Secours facultatif avec Chromium. Il n'est utilisé que si installé.
    try:
        body = await _fetch_with_playwright(target)
        _validate_fortnite_html(body, player_id)
        _CACHE[player_id] = (time.monotonic(), body)
        return JSONResponse({"id": player_id, "player": _parse_player_html(body, player_id), "cached": False, "method": "playwright"})
    except Exception as exc:
        errors.append(f"Chromium : {exc}")

    raise HTTPException(
        status_code=502,
        detail=(
            "Impossible de récupérer ou d’analyser complètement la page Fortnite.GG. "
            "Installez d'abord curl_cffi avec `pip install curl_cffi`. "
            "En secours : `pip install playwright` puis `playwright install chromium`. "
            + " · ".join(errors[-4:])
        ),
    )


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "cached_players": len(_CACHE)}


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )