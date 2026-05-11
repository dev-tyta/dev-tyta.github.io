/**
 * Testimony's Digital Double — Chat Widget v2
 *
 * Features:
 * - Real profile image avatar
 * - Messages persist across page navigation (sessionStorage)
 * - Page-aware greeting + context sent to agent
 * - Agent-driven page navigation with navigation cards
 * - Text-to-speech on every bot message (Web Speech API)
 * - Blog post read-aloud mode
 * - Quick-reply suggestion chips
 * - Proactive suggestions per page
 */

(function () {
  'use strict';

  // ── Config ──────────────────────────────────────────────────────────────────
  const AVATAR_IMG = 'img/_DSC4243.JPG';

  // localhost → always local dev server; production → stored Railway URL
  function _apiBase() {
    if (['localhost', '127.0.0.1'].includes(location.hostname)) {
      return 'http://127.0.0.1:8000';
    }
    return (localStorage.getItem('_chat_api') || localStorage.getItem('_blog_api') || '').replace(/\/$/, '');
  }
  const AGENT_URL = (() => { const b = _apiBase(); return b ? b + '/agent' : null; })();

  const SESSION_KEY  = '_chat_session_id';
  const MSGS_KEY     = '_chat_messages';    // persisted across pages

  // ── Page-aware data ─────────────────────────────────────────────────────────
  const CURRENT_PAGE = location.pathname + location.search;

  const PAGE_GREETINGS = {
    '/projects/mmibc.html':
      "I see you're on the MMIBC case study! I built this framework to make breast cancer diagnosis more accessible in low-resource clinical settings. Happy to walk you through the architecture, the Grad-CAM explainability layer, or the results. What do you want to know?",
    '/projects/afrivton.html':
      "You're on the AfriVTON-Bench case study — one of my favourite pieces of research. It benchmarks how badly VTON systems fail on African textiles, and why. Want me to explain the methodology, the failure modes we found, or why this matters beyond academia?",
    '/now.html':
      "This is my now page — an honest snapshot of what I'm building, reading, and thinking about. FAUE is the big side project right now. Curious about anything here?",
    '/blog.html':
      "You're on my blog. I've written about building the Synthik synthetic data pipeline, AfriVTON-Bench, and the MMIBC research. I can summarise any post, read one aloud to you, or dig into a topic. What do you want to explore?",
    '/post.html':
      "Reading one of my posts? I can summarise it, clarify technical sections, or find related content. I can also read it aloud if you'd prefer to listen. What would help?",
  };

  const PAGE_QUICK_REPLIES = {
    '/projects/mmibc.html': [
      'Walk me through the ViT architecture',
      'How does the data pairing strategy work?',
      'What are the main limitations?',
    ],
    '/projects/afrivton.html': [
      'Explain the 3 failure modes',
      'How did you build the dataset?',
      'Why does the g/p ratio matter?',
    ],
    '/blog.html': [
      'Summarise the Synthik post',
      'What did AfriVTON-Bench find?',
      'Read me the MMIBC post',
    ],
    '/now.html': [
      'Tell me more about FAUE',
      "What's the status of AfriVTON-Bench?",
      'What are you reading right now?',
    ],
    default: [
      "What are you currently working on?",
      "Tell me about your most interesting project",
      "How can I reach you?",
    ],
  };

  function getDefaultGreeting() {
    const page = location.pathname;
    for (const [key, msg] of Object.entries(PAGE_GREETINGS)) {
      if (page.includes(key) || (key === '/post.html' && page.includes('post.html'))) {
        return msg;
      }
    }
    return "Hey! I'm Testimony's digital double — an AI trained to represent me. I can tell you about my projects, research, blog posts, and current work. I can also read content aloud or help you navigate the portfolio. What's on your mind?";
  }

  function getPageQuickReplies() {
    const page = location.pathname;
    for (const [key, replies] of Object.entries(PAGE_QUICK_REPLIES)) {
      if (key !== 'default' && page.includes(key)) return replies;
    }
    return PAGE_QUICK_REPLIES.default;
  }

  // ── Message persistence ─────────────────────────────────────────────────────
  function loadMessages() {
    try { return JSON.parse(sessionStorage.getItem(MSGS_KEY) || '[]'); }
    catch { return []; }
  }

  function saveMessages(msgs) {
    try { sessionStorage.setItem(MSGS_KEY, JSON.stringify(msgs.slice(-60))); } // cap at 60
    catch {}
  }

  let storedMessages = loadMessages();

  function pushMessage(entry) {
    storedMessages.push({ ...entry, ts: Date.now() });
    saveMessages(storedMessages);
  }

  // ── TTS ─────────────────────────────────────────────────────────────────────
  const TTS = window.speechSynthesis || null;
  let currentUtterance = null;
  let activeTTSBtn = null;

  function speak(text, btn) {
    if (!TTS) return;
    if (TTS.speaking) {
      TTS.cancel();
      if (activeTTSBtn) { activeTTSBtn.dataset.speaking = ''; activeTTSBtn.title = 'Read aloud'; activeTTSBtn.innerHTML = TTS_ICON; }
      if (activeTTSBtn === btn) { activeTTSBtn = null; return; }
    }
    const plain = text.replace(/\*\*|__|\*|_|`|#/g, '').replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
    currentUtterance = new SpeechSynthesisUtterance(plain);
    currentUtterance.rate  = 0.95;
    currentUtterance.pitch = 1.0;
    currentUtterance.lang  = 'en-US';
    currentUtterance.onstart = () => {
      activeTTSBtn = btn;
      btn.dataset.speaking = '1';
      btn.title = 'Stop reading';
      btn.innerHTML = STOP_ICON;
    };
    currentUtterance.onend = currentUtterance.onerror = () => {
      if (activeTTSBtn) { activeTTSBtn.dataset.speaking = ''; activeTTSBtn.title = 'Read aloud'; activeTTSBtn.innerHTML = TTS_ICON; }
      activeTTSBtn = null;
    };
    TTS.speak(currentUtterance);
  }

  const TTS_ICON  = `<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>`;
  const STOP_ICON = `<svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>`;

  // ── CSS ─────────────────────────────────────────────────────────────────────
  const CSS = `
    #ta-chat-btn {
      position: fixed; bottom: 28px; right: 28px; z-index: 900;
      width: 54px; height: 54px; border-radius: 50%;
      border: none; cursor: pointer; padding: 0; overflow: hidden;
      box-shadow: 0 4px 24px rgba(59,130,246,0.45);
      transition: transform 0.2s, box-shadow 0.2s;
      background: linear-gradient(135deg,#3b82f6,#10b981);
    }
    #ta-chat-btn:hover { transform: scale(1.08); box-shadow: 0 6px 32px rgba(59,130,246,0.6); }
    #ta-chat-btn img.ta-btn-avatar {
      width:100%; height:100%; object-fit:cover; object-position:center 15%;
      display:block; transition: opacity 0.2s;
    }
    #ta-chat-btn.open img.ta-btn-avatar { opacity:0.3; }
    #ta-chat-btn .ta-btn-close {
      position:absolute; inset:0; display:none; align-items:center; justify-content:center;
    }
    #ta-chat-btn.open .ta-btn-close { display:flex; }
    #ta-chat-btn .ta-btn-close svg { width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2.5;stroke-linecap:round; }

    #ta-chat-panel {
      position: fixed; bottom: 94px; right: 28px; z-index: 900;
      width: 374px; max-height: 560px;
      background: var(--bg-card, #141414);
      border: 1px solid var(--border-hover, rgba(255,255,255,0.18));
      border-radius: 20px; display: flex; flex-direction: column;
      box-shadow: 0 24px 64px rgba(0,0,0,0.55);
      transform: translateY(14px) scale(0.97); opacity: 0; pointer-events: none;
      transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), opacity 0.24s;
      overflow: hidden;
    }
    #ta-chat-panel.open { transform: none; opacity: 1; pointer-events: all; }

    .ta-head {
      padding: 14px 16px; display: flex; align-items: center; gap: 10px;
      background: linear-gradient(135deg,rgba(59,130,246,0.11),rgba(16,185,129,0.09));
      border-bottom: 1px solid var(--border,rgba(255,255,255,0.07)); flex-shrink: 0;
    }
    .ta-head-avatar {
      width: 36px; height: 36px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
      border: 2px solid rgba(59,130,246,0.4);
    }
    .ta-head-avatar img { width:100%; height:100%; object-fit:cover; object-position:center 15%; display:block; }
    .ta-head-name { font-size: 14px; font-weight: 700; color: var(--text,#f0f0f0); }
    .ta-head-status { font-size: 11px; color: var(--text-3,#5a5a5a); display:flex; align-items:center; gap:5px; }
    .ta-status-dot { width:6px;height:6px;border-radius:50%;background:#10b981;animation:ta-pulse 2s ease-in-out infinite; }
    @keyframes ta-pulse{0%,100%{opacity:1}50%{opacity:0.35}}

    .ta-msgs { flex:1; overflow-y:auto; padding:14px 12px; display:flex; flex-direction:column; gap:10px; scroll-behavior:smooth; }
    .ta-msgs::-webkit-scrollbar { width:4px; }
    .ta-msgs::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1);border-radius:4px; }
    [data-theme="light"] .ta-msgs::-webkit-scrollbar-thumb { background:rgba(0,0,0,0.12); }

    .ta-msg { display:flex; gap:8px; max-width:90%; }
    .ta-msg.usr { align-self:flex-end; flex-direction:row-reverse; }
    .ta-msg-av { width:26px;height:26px;border-radius:50%;flex-shrink:0;overflow:hidden;border:1px solid rgba(59,130,246,0.25); }
    .ta-msg-av img { width:100%;height:100%;object-fit:cover;object-position:center 15%;display:block; }
    .ta-msg-av.usr-av { background:rgba(16,185,129,0.12);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#10b981;border-color:rgba(16,185,129,0.25); }
    .ta-bubble { padding:9px 12px; border-radius:14px; font-size:13px; line-height:1.65; color:var(--text-2,#a3a3a3); position:relative; }
    .ta-bubble.bot { background:var(--bg,#0d0d0d); border:1px solid var(--border,rgba(255,255,255,0.07)); border-bottom-left-radius:4px; }
    .ta-bubble.usr { background:rgba(59,130,246,0.13); border:1px solid rgba(59,130,246,0.22); color:var(--text,#f0f0f0); border-bottom-right-radius:4px; }
    [data-theme="light"] .ta-bubble.bot { background:rgba(0,0,0,0.03);border-color:rgba(0,0,0,0.08); }
    .ta-bubble strong { color:var(--text,#f0f0f0); font-weight:700; }
    .ta-bubble a { color:var(--blue,#3b82f6); }
    .ta-bubble code { background:rgba(255,255,255,0.08);padding:1px 4px;border-radius:4px;font-size:12px;color:#10b981; }
    [data-theme="light"] .ta-bubble code { background:rgba(0,0,0,0.07); }
    .ta-bubble pre { background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;overflow-x:auto;margin:6px 0; }
    [data-theme="light"] .ta-bubble pre { background:rgba(0,0,0,0.06); }

    /* TTS button row */
    .ta-msg-actions { display:flex; gap:6px; margin-top:5px; align-items:center; }
    .ta-tts-btn {
      display:inline-flex; align-items:center; gap:4px; padding:3px 8px;
      border:1px solid var(--border,rgba(255,255,255,0.07)); border-radius:100px;
      background:transparent; cursor:pointer; font-size:10px; color:var(--text-3,#5a5a5a);
      font-family:inherit; transition:all 0.2s;
    }
    .ta-tts-btn:hover { border-color:rgba(59,130,246,0.4);color:var(--blue,#3b82f6); }
    .ta-tts-btn[data-speaking="1"] { border-color:rgba(248,113,113,0.4);color:#f87171; }
    .ta-model-chip { font-size:10px;color:var(--text-3,#5a5a5a);padding:3px 7px;border:1px solid var(--border,rgba(255,255,255,0.07));border-radius:100px;background:transparent; }

    /* Navigation card */
    .ta-nav-card {
      display:flex; align-items:center; gap:10px;
      padding:10px 14px; border:1px solid rgba(59,130,246,0.25);
      border-radius:12px; background:rgba(59,130,246,0.06); cursor:pointer;
      text-decoration:none; transition:background 0.2s; margin-top:6px;
    }
    .ta-nav-card:hover { background:rgba(59,130,246,0.12); }
    .ta-nav-icon { width:28px;height:28px;border-radius:8px;background:rgba(59,130,246,0.12);display:flex;align-items:center;justify-content:center;flex-shrink:0; }
    .ta-nav-icon svg { width:14px;height:14px;stroke:var(--blue,#3b82f6);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round; }
    .ta-nav-label { font-size:12px;font-weight:600;color:var(--blue,#3b82f6); }
    .ta-nav-sub { font-size:10px;color:var(--text-3,#5a5a5a);margin-top:1px; }

    /* Quick reply chips */
    .ta-qr-row { display:flex;flex-wrap:wrap;gap:6px;margin-top:8px; }
    .ta-qr-chip {
      padding:5px 12px; border:1px solid var(--border,rgba(255,255,255,0.07));
      border-radius:100px; font-size:11px; font-weight:500; color:var(--text-2,#a3a3a3);
      cursor:pointer; background:transparent; font-family:inherit; transition:all 0.2s;
    }
    .ta-qr-chip:hover { border-color:rgba(59,130,246,0.4);color:var(--blue,#3b82f6);background:rgba(59,130,246,0.06); }

    /* Typing indicator */
    .ta-typing-dots { display:flex;gap:4px;align-items:center;padding:10px 13px; }
    .ta-dot { width:6px;height:6px;border-radius:50%;background:var(--text-3,#5a5a5a);animation:ta-bounce 1.2s ease-in-out infinite; }
    .ta-dot:nth-child(2){animation-delay:0.2s} .ta-dot:nth-child(3){animation-delay:0.4s}
    @keyframes ta-bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}

    /* Input area */
    .ta-input-row { padding:10px 12px; border-top:1px solid var(--border,rgba(255,255,255,0.07)); display:flex; gap:8px; align-items:flex-end; flex-shrink:0; }
    #ta-input {
      flex:1; background:rgba(255,255,255,0.04); border:1px solid var(--border,rgba(255,255,255,0.07));
      border-radius:10px; padding:9px 12px; font-size:13px; color:var(--text,#f0f0f0);
      font-family:inherit; resize:none; max-height:100px; outline:none;
      transition:border-color 0.2s; line-height:1.5;
    }
    [data-theme="light"] #ta-input { background:rgba(0,0,0,0.04);color:#111; }
    #ta-input:focus { border-color:rgba(59,130,246,0.5); }
    #ta-input::placeholder { color:var(--text-3,#5a5a5a); }
    #ta-send {
      width:34px;height:34px;border-radius:50%;flex-shrink:0;
      background:linear-gradient(135deg,#3b82f6,#10b981);border:none;cursor:pointer;
      display:flex;align-items:center;justify-content:center;align-self:flex-end;
      transition:opacity 0.2s;
    }
    #ta-send:hover:not(:disabled){opacity:0.88} #ta-send:disabled{opacity:0.35;cursor:not-allowed}
    #ta-send svg{width:14px;height:14px;stroke:#fff;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}

    @media(max-width:480px){
      #ta-chat-panel{right:10px;left:10px;width:auto;bottom:76px;}
      #ta-chat-btn{bottom:14px;right:14px;}
    }
  `;

  // ── HTML skeleton ────────────────────────────────────────────────────────────
  const HTML = `
    <button id="ta-chat-btn" aria-label="Chat with Testimony's digital double" aria-expanded="false">
      <img class="ta-btn-avatar" src="${AVATAR_IMG}" alt="Testimony Adekoya">
      <span class="ta-btn-close" aria-hidden="true">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </span>
    </button>
    <div id="ta-chat-panel" role="dialog" aria-label="Chat with Testimony Adekoya">
      <div class="ta-head">
        <div class="ta-head-avatar">
          <img src="${AVATAR_IMG}" alt="Testimony Adekoya" loading="lazy">
        </div>
        <div>
          <div class="ta-head-name">Testimony Adekoya</div>
          <div class="ta-head-status"><span class="ta-status-dot" aria-hidden="true"></span>Digital double — ask me anything</div>
        </div>
      </div>
      <div class="ta-msgs" id="ta-msgs" role="log" aria-live="polite" aria-label="Chat messages"></div>
      <div class="ta-input-row">
        <textarea id="ta-input" placeholder="Ask about my work, research, or anything…" rows="1" aria-label="Your message"></textarea>
        <button id="ta-send" aria-label="Send" disabled>
          <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </div>
  `;

  // ── Init ─────────────────────────────────────────────────────────────────────
  function init() {
    // Inject CSS
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    // Inject HTML
    const wrap = document.createElement('div');
    wrap.innerHTML = HTML;
    document.body.appendChild(wrap);

    const btn   = document.getElementById('ta-chat-btn');
    const panel = document.getElementById('ta-chat-panel');
    const msgs  = document.getElementById('ta-msgs');
    const input = document.getElementById('ta-input');
    const send  = document.getElementById('ta-send');

    let isOpen     = false;
    let isLoading  = false;
    let sessionId  = sessionStorage.getItem(SESSION_KEY);

    // ── Open/close ─────────────────────────────────────────────────────────────
    function openPanel() {
      isOpen = true;
      btn.classList.add('open');
      panel.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
      if (msgs.children.length === 0) {
        if (storedMessages.length > 0) {
          storedMessages.forEach(m => renderStored(m));
        } else {
          addBotMsg(getDefaultGreeting(), null, null, getPageQuickReplies());
          if (!sessionId) ensureSession();
        }
      }
      setTimeout(() => { input.focus(); msgs.scrollTop = msgs.scrollHeight; }, 280);
    }

    function closePanel() {
      isOpen = false;
      btn.classList.remove('open');
      panel.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      if (TTS?.speaking) TTS.cancel();
    }

    btn.addEventListener('click', () => isOpen ? closePanel() : openPanel());
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && isOpen) closePanel();
    });
    if (location.hash === '#chat') openPanel();

    // ── Session ─────────────────────────────────────────────────────────────────
    async function ensureSession() {
      if (sessionId) return sessionId;
      if (!AGENT_URL) {
        sessionId = 'local-' + Date.now();
        sessionStorage.setItem(SESSION_KEY, sessionId);
        return sessionId;
      }
      try {
        const r = await fetch(`${AGENT_URL}/session`, { method: 'POST' });
        const d = await r.json();
        sessionId = d.session_id;
        sessionStorage.setItem(SESSION_KEY, sessionId);
      } catch {
        sessionId = 'fallback-' + Date.now();
        sessionStorage.setItem(SESSION_KEY, sessionId);
      }
      return sessionId;
    }

    // ── Render helpers ──────────────────────────────────────────────────────────
    function esc(s) {
      return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function mdToHtml(text) {
      return esc(text)
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
        .replace(/\n/g, '<br>');
    }

    function makeBotBubble(text, model, navUrl, navLabel, qrs) {
      const wrap = document.createElement('div');
      wrap.className = 'ta-msg';

      // Avatar
      const avWrap = document.createElement('div');
      avWrap.className = 'ta-msg-av';
      const avImg = document.createElement('img');
      avImg.src = AVATAR_IMG;
      avImg.alt = 'Testimony';
      avImg.loading = 'lazy';
      avWrap.appendChild(avImg);

      // Bubble + actions column
      const col = document.createElement('div');

      const bubble = document.createElement('div');
      bubble.className = 'ta-bubble bot';
      bubble.innerHTML = mdToHtml(text);
      col.appendChild(bubble);

      // Action row: TTS + model chip
      const actRow = document.createElement('div');
      actRow.className = 'ta-msg-actions';

      if (TTS) {
        const ttsBtn = document.createElement('button');
        ttsBtn.className = 'ta-tts-btn';
        ttsBtn.title = 'Read aloud';
        ttsBtn.innerHTML = TTS_ICON + ' <span>Read</span>';
        ttsBtn.addEventListener('click', () => speak(text, ttsBtn));
        actRow.appendChild(ttsBtn);
      }

      if (model) {
        const chip = document.createElement('span');
        chip.className = 'ta-model-chip';
        chip.textContent = model;
        actRow.appendChild(chip);
      }

      if (actRow.children.length) col.appendChild(actRow);

      // Navigation card
      if (navUrl) {
        const card = document.createElement('a');
        card.className = 'ta-nav-card';
        card.href = navUrl;
        card.innerHTML = `
          <div class="ta-nav-icon">
            <svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </div>
          <div>
            <div class="ta-nav-label">${esc(navLabel || 'View')}</div>
            <div class="ta-nav-sub">Tap to navigate →</div>
          </div>`;
        col.appendChild(card);
      }

      // Quick reply chips
      if (qrs && qrs.length) {
        const qrRow = document.createElement('div');
        qrRow.className = 'ta-qr-row';
        qrs.forEach(q => {
          const chip = document.createElement('button');
          chip.className = 'ta-qr-chip';
          chip.textContent = q;
          chip.addEventListener('click', () => {
            qrRow.remove(); // remove after use
            sendMessage(q);
          });
          qrRow.appendChild(chip);
        });
        col.appendChild(qrRow);
      }

      wrap.appendChild(avWrap);
      wrap.appendChild(col);
      return wrap;
    }

    function addBotMsg(text, model, navEntry, qrs) {
      const el = makeBotBubble(text, model, navEntry?.url || null, navEntry?.label || null, qrs);
      msgs.appendChild(el);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function addUserMsg(text) {
      const wrap = document.createElement('div');
      wrap.className = 'ta-msg usr';
      wrap.innerHTML = `<div class="ta-msg-av usr-av">You</div><div class="ta-bubble usr">${esc(text)}</div>`;
      msgs.appendChild(wrap);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function showTyping() {
      const wrap = document.createElement('div');
      wrap.className = 'ta-msg';
      wrap.id = 'ta-typing';
      const av = document.createElement('div');
      av.className = 'ta-msg-av';
      const img = document.createElement('img');
      img.src = AVATAR_IMG; img.alt = ''; img.loading = 'lazy';
      av.appendChild(img);
      const bubble = document.createElement('div');
      bubble.className = 'ta-bubble bot';
      bubble.innerHTML = '<div class="ta-typing-dots"><span class="ta-dot"></span><span class="ta-dot"></span><span class="ta-dot"></span></div>';
      wrap.appendChild(av);
      wrap.appendChild(bubble);
      msgs.appendChild(wrap);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function removeTyping() { document.getElementById('ta-typing')?.remove(); }

    // Render a stored message (replay on page load)
    function renderStored(m) {
      if (m.role === 'user') {
        addUserMsg(m.text);
      } else {
        addBotMsg(m.text, m.model, m.nav || null, m.qrs || null);
      }
    }

    // ── Send message ────────────────────────────────────────────────────────────
    async function sendMessage(text) {
      text = (text || '').trim();
      if (!text || isLoading) return;

      addUserMsg(text);
      pushMessage({ role: 'user', text });
      input.value = '';
      input.style.height = 'auto';
      send.disabled = true;
      isLoading = true;

      showTyping();

      if (!AGENT_URL) {
        removeTyping();
        const helpText = "Chat API not configured. Open the browser console and run:\n`localStorage.setItem('_chat_api', 'https://your-api.up.railway.app')`\nthen refresh the page.";
        addBotMsg(helpText, null, null, null);
        isLoading = false;
        send.disabled = !input.value.trim();
        return;
      }

      try {
        const sid = await ensureSession();
        const res = await fetch(`${AGENT_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sid,
            message: text,
            current_page: CURRENT_PAGE,
          }),
          signal: AbortSignal.timeout(90000),
        });

        removeTyping();

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          addBotMsg(err.detail || 'Something went wrong — please try again.', null, null, null);
          return;
        }

        const data = await res.json();
        const nav = data.navigate_url ? { url: data.navigate_url, label: data.navigate_label } : null;
        const qrs = data.quick_replies?.length ? data.quick_replies : null;
        const modelLabel = data.is_fallback ? `${data.model_used} (fallback)` : data.model_used;

        addBotMsg(data.reply, modelLabel, nav, qrs);
        pushMessage({ role: 'bot', text: data.reply, model: modelLabel, nav, qrs });

      } catch (e) {
        removeTyping();
        const msg = e.name === 'TimeoutError'
          ? "That took too long — the server may be waking up. Please try again in a moment."
          : "Couldn't reach the chat API right now. Please try again.";
        addBotMsg(msg, null, null, null);
      } finally {
        isLoading = false;
        send.disabled = !input.value.trim();
        input.focus();
      }
    }

    // ── Input events ────────────────────────────────────────────────────────────
    input.addEventListener('input', () => {
      send.disabled = !input.value.trim() || isLoading;
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input.value); }
    });
    send.addEventListener('click', () => sendMessage(input.value));
  }

  // ── Bootstrap ────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
