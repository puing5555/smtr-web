(globalThis.TURBOPACK||(globalThis.TURBOPACK=[])).push(["object"==typeof document?document.currentScript:void 0,91439,e=>{"use strict";var t=e.i(61429),i=e.i(94806),s=e.i(21447),r=e.i(89211);let n=(0,i.cva)("inline-flex items-center justify-center rounded-full border border-transparent px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",{variants:{variant:{default:"bg-primary text-primary-foreground [a&]:hover:bg-primary/90",secondary:"bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",destructive:"bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",outline:"border-border text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",ghost:"[a&]:hover:bg-accent [a&]:hover:text-accent-foreground",link:"text-primary underline-offset-4 [a&]:hover:underline"}},defaultVariants:{variant:"default"}});function l({className:e,variant:i="default",asChild:l=!1,...a}){let o=l?s.Slot.Root:"span";return(0,t.jsx)(o,{"data-slot":"badge","data-variant":i,className:(0,r.cn)(n({variant:i}),e),...a})}e.s(["Badge",()=>l])},63123,e=>{"use strict";var t=e.i(44372);let i=e=>{let t,i=new Set,s=(e,s)=>{let r="function"==typeof e?e(t):e;if(!Object.is(r,t)){let e=t;t=(null!=s?s:"object"!=typeof r||null===r)?r:Object.assign({},t,r),i.forEach(i=>i(t,e))}},r=()=>t,n={setState:s,getState:r,getInitialState:()=>l,subscribe:e=>(i.add(e),()=>i.delete(e))},l=t=e(s,r,n);return n},s=e=>{let s=e?i(e):i,r=e=>(function(e,i=e=>e){let s=t.default.useSyncExternalStore(e.subscribe,t.default.useCallback(()=>i(e.getState()),[e,i]),t.default.useCallback(()=>i(e.getInitialState()),[e,i]));return t.default.useDebugValue(s),s})(s,e);return Object.assign(r,s),r},r=e=>e?s(e):s;e.s(["create",()=>r],63123)},2576,e=>{"use strict";let t=(0,e.i(84786).default)("arrow-left",[["path",{d:"m12 19-7-7 7-7",key:"1l729n"}],["path",{d:"M19 12H5",key:"x3x0zl"}]]);e.s(["ArrowLeft",()=>t],2576)},23506,e=>{"use strict";var t=e.i(61429),i=e.i(44372),s=e.i(2576),r=e.i(39931),n=e.i(45192),l=e.i(91439),a=e.i(95557),o=e.i(76973);let d=["BTC","ETH","XRP","SOL","ADA","DOT"],c={STRONG_BUY:"#10b981",BUY:"#22c55e",POSITIVE:"#3b82f6",HOLD:"#06b6d4",NEUTRAL:"#6b7280",CONCERN:"#f59e0b",SELL:"#ef4444",STRONG_SELL:"#dc2626"},p={STRONG_BUY:"적극매수",BUY:"매수",POSITIVE:"긍정",HOLD:"보유",NEUTRAL:"중립",CONCERN:"우려",SELL:"매도",STRONG_SELL:"적극매도"};function x({symbol:x}){let u=(0,i.useRef)(null),g=(0,i.useRef)(null),[m,h]=(0,i.useState)([]),[y,f]=(0,i.useState)(!0),[b,v]=(0,i.useState)(null),[w,N]=(0,i.useState)("ALL"),[j,k]=(0,i.useState)("ALL"),{signals:L,loadSignals:T}=(0,o.useInfluencersStore)();(0,i.useEffect)(()=>{T()},[T]);let S=(0,i.useMemo)(()=>L.filter(e=>e.stock===x||e.stockName===x),[L,x]),C=(0,i.useMemo)(()=>{let e=S;return"ALL"!==w&&(e=e.filter(e=>e.influencer===w)),"ALL"!==j&&(e=e.filter(e=>e.signalType===j)),e},[S,w,j]),$=(0,i.useMemo)(()=>[...new Set(S.map(e=>e.influencer))],[S]),E=S[0]?.stockName||x,D=d.includes(x);return((0,i.useEffect)(()=>{D?(async()=>{try{f(!0);let e=await fetch(`https://min-api.cryptocompare.com/data/v2/histoday?fsym=${x}&tsym=USD&limit=730`),t=await e.json();if("Error"===t.Response)throw Error(t.Message);let i=(t.Data?.Data||[]).map(e=>({time:new Date(1e3*e.time).toISOString().split("T")[0],open:e.open,high:e.high,low:e.low,close:e.close}));h(i)}catch(e){v(e.message||"차트 데이터 로드 실패")}finally{f(!1)}})():f(!1)},[x,D]),(0,i.useEffect)(()=>{if(!u.current||0===m.length)return;let t=u.current,i=!1,s=null,r=null,n=null;return(async()=>{g.current&&(g.current.remove(),g.current=null);let l=t.querySelector(".marker-overlay-container");l&&l.remove();let{createChart:a,ColorType:o}=await e.A(22886);if(i)return;let d=t.clientWidth||800,u=Math.max(t.clientHeight,window.innerHeight-300,500),h=a(t,{width:d,height:u,layout:{background:{type:o.Solid,color:"#ffffff"},textColor:"#333"},grid:{vertLines:{color:"#f0f0f0"},horzLines:{color:"#f0f0f0"}},rightPriceScale:{borderColor:"#ddd"},timeScale:{borderColor:"#ddd",timeVisible:!1}}),y=h.addCandlestickSeries({upColor:"#22c55e",downColor:"#ef4444",borderUpColor:"#16a34a",borderDownColor:"#dc2626",wickUpColor:"#16a34a",wickDownColor:"#dc2626"});y.setData(m.map(e=>({time:e.time,open:e.open,high:e.high,low:e.low,close:e.close}))),(s=document.createElement("div")).className="marker-overlay-container",s.style.cssText=`
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 50;
      `;let f=document.createElementNS("http://www.w3.org/2000/svg","svg");f.style.cssText=`
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 49;
      `,s.appendChild(f),t.appendChild(s),(r=document.createElement("div")).className="marker-tooltip",r.style.cssText=`
        position: absolute;
        z-index: 60;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 0;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        pointer-events: auto;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.2s, visibility 0.2s;
      `,t.appendChild(r),h.timeScale().fitContent(),g.current=h;let b=!1,v=null,w=0,N=0,j=null,k=null,L=e=>{let t=new Date(e),i=t.getFullYear(),s=t.getMonth()+1,r=t.getDate();return`${i}년 ${s}월 ${r}일`},T=e=>{let i=e.target;if(i.closest(".marker-dot")||i.closest(".marker-tooltip")||i.closest(".dot-preview"))return;let s=t.getBoundingClientRect(),r=e.clientX-s.left,n=e.clientY-s.top;if(r<60||r>s.width-60||n<20||n>s.height-40)return;let l=h.timeScale().coordinateToTime(r);l&&(b=!0,v=l,w=r,N=n,j&&(j.style.display="none"),k&&(k.style.display="none"),e.preventDefault())},S=e=>{if(!b||!v)return;let i=t.getBoundingClientRect(),s=e.clientX-i.left;e.clientY,i.top;let r=(j||((j=document.createElement("div")).style.cssText=`
          position: absolute;
          background: rgba(66, 165, 245, 0.15);
          border: 1px solid rgba(66, 165, 245, 0.4);
          border-radius: 4px;
          pointer-events: none;
          z-index: 45;
          display: none;
        `,t.appendChild(j)),j),n=Math.min(w,s),l=Math.max(w,s),a=i.height-40;r.style.left=`${n}px`,r.style.top="20px",r.style.width=`${l-n}px`,r.style.height=`${a-20}px`,r.style.display="block",e.preventDefault()},$=e=>{if(!b||!v)return;let i=t.getBoundingClientRect(),s=e.clientX-i.left,r=h.timeScale().coordinateToTime(s);if(!r){b=!1;return}Math.abs(s-w)>10&&v!==r?((e,i,s,r)=>{let n=m.find(t=>t.time===e),l=m.find(e=>e.time===i);if(!n||!l)return;let a=n.close,o=l.close-a,d=o/a*100,c=o>=0,p=(k||((k=document.createElement("div")).style.cssText=`
          position: absolute;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 12px 16px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.15);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          white-space: nowrap;
          z-index: 60;
          pointer-events: auto;
          cursor: pointer;
          display: none;
        `,t.appendChild(k)),k);p.innerHTML=`
          <div style="color: ${c?"#10b981":"#ef4444"}; font-size: 16px; font-weight: 700; line-height: 1.2; margin-bottom: 4px;">
            ${o>=0?"+":""}$${Math.abs(o).toFixed(2)} (${d>=0?"+":""}${d.toFixed(2)}%) ${c?"↑":"↓"}
          </div>
          <div style="color: #6b7280; font-size: 13px;">
            ${L(e)} - ${L(i)}
          </div>
        `;let x=t.getBoundingClientRect(),u=s+10,g=r-60-10;u+300>x.width&&(u=s-300-10),g<0&&(g=r+20),p.style.left=`${Math.max(10,u)}px`,p.style.top=`${Math.max(10,g)}px`,p.style.display="block",p.onclick=()=>{p.style.display="none",j&&(j.style.display="none")}})(v<=r?v:r,v<=r?r:v,(w+s)/2,Math.min(N,e.clientY-i.top)):j&&(j.style.display="none"),b=!1,v=null,e.preventDefault()},E=e=>{let i=e.target;t.contains(i)&&(i.closest(".marker-dot")||i.closest(".marker-tooltip")||i.closest(".dot-preview")||i===k||k?.contains(i))||(j&&(j.style.display="none"),k&&(k.style.display="none"))};t.addEventListener("mousedown",T),t.addEventListener("mousemove",S),t.addEventListener("mouseup",$),document.addEventListener("click",E);let D=()=>{s&&s.querySelectorAll(".marker-dot").forEach(e=>{let t=e._signal,i=e._line;if(t&&t.videoDate)try{let s=h.timeScale().timeToCoordinate(t.videoDate);if(null===s){e.style.display="none",i&&(i.style.display="none");return}let r=m.find(e=>e.time===t.videoDate)||m.find(e=>864e5>Math.abs(new Date(e.time).getTime()-new Date(t.videoDate).getTime()))||m[Math.floor(m.length/2)],n=y.priceToCoordinate(r.close);if(null===n){e.style.display="none",i&&(i.style.display="none");return}let l=n-18-6;e.style.left=`${s-6}px`,e.style.top=`${l}px`,e.style.display="block",i&&(i.setAttribute("x1",`${s}`),i.setAttribute("y1",`${n}`),i.setAttribute("x2",`${s}`),i.setAttribute("y2",`${l+6}`),i.style.display="block")}catch(t){e.style.display="none",i&&(i.style.display="none")}})};s&&f&&(s.querySelectorAll(".marker-dot").forEach(e=>e.remove()),f.innerHTML="",C.forEach((e,i)=>{if(!e.videoDate)return;let n=document.createElement("div");n.className=`marker-dot type-${e.signalType.toLowerCase().replace("_","-")}`,n.style.cssText=`
            position: absolute;
            pointer-events: auto;
            cursor: pointer;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 8px ${c[e.signalType]||"#94a3b8"}80, 0 2px 6px rgba(0,0,0,0.2);
            transition: transform 0.15s, box-shadow 0.15s;
            z-index: 51;
            background: ${c[e.signalType]||"#94a3b8"};
          `;let l=document.createElementNS("http://www.w3.org/2000/svg","line");l.setAttribute("stroke",c[e.signalType]||"#94a3b8"),l.setAttribute("stroke-width","2"),l.setAttribute("stroke-dasharray","4,3"),l.style.opacity="0",l.style.transition="opacity 0.2s",f.appendChild(l);let a=document.createElement("div");a.className="dot-preview",a.style.cssText=`
            position: absolute;
            z-index: 56;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 6px 10px;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s;
            font-size: 12px;
            color: #374151;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          `,a.innerHTML=`<span style="font-weight: 700; color: #3b82f6; margin-right: 6px;">${x}</span><span style="font-weight: 600;">${p[e.signalType]||e.signalType}</span>`,t.appendChild(a),n.addEventListener("mouseenter",()=>{n.style.transform="scale(1.6)",n.style.boxShadow="0 0 12px rgba(59,130,246,0.3)",n.style.zIndex="55",l.style.opacity="0.7";let e=n.getBoundingClientRect(),i=t.getBoundingClientRect();a.style.left=`${e.left-i.left+12}px`,a.style.top=`${e.top-i.top-35}px`,a.style.opacity="1"}),n.addEventListener("mouseleave",()=>{n.style.transform="scale(1)",n.style.boxShadow="0 2px 8px rgba(0,0,0,0.15)",n.style.zIndex="51",l.style.opacity="0",a.style.opacity="0"}),n.addEventListener("click",i=>{if(i.stopPropagation(),!r)return;r.innerHTML=`
              <button onclick="this.parentElement.style.opacity='0'; this.parentElement.style.visibility='hidden';" style="position: absolute; top: 10px; right: 12px; background: rgba(0,0,0,0.06); border: none; color: #6b7280; cursor: pointer; font-size: 14px; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">✕</button>
              <div style="padding: 16px 18px 12px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #f3f4f6;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: ${c[e.signalType]||"#94a3b8"}; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px;">${e.influencer.charAt(0)}</div>
                <div style="flex: 1;">
                  <div style="font-weight: 700; font-size: 15px; color: #111827;">${e.influencer}</div>
                  <div style="font-size: 11px; color: #6b7280; margin-top: 1px;">${e.videoDate}</div>
                </div>
                <span style="padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; color: white; background: ${c[e.signalType]||"#94a3b8"};">${p[e.signalType]||e.signalType}</span>
              </div>
              <div style="padding: 14px 18px;">
                <div style="color: #374151; font-size: 13px; line-height: 1.6; margin-bottom: 14px; padding-left: 14px; border-left: 3px solid #3b82f6; border-radius: 2px;">${e.content||"내용 없음"}</div>
                ${e.youtubeLink?`<a href="${e.youtubeLink}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #dc2626; font-size: 13px; text-decoration: none; padding: 8px 14px; background: rgba(220,38,38,0.08); border-radius: 10px; font-weight: 600;">▶ YouTube에서 보기</a>`:""}
              </div>
            `;let s=n.getBoundingClientRect(),a=t.getBoundingClientRect();r.style.left=`${s.left-a.left+15}px`,r.style.top=`${s.top-a.top-10}px`,r.style.opacity="1",r.style.visibility="visible",l.style.opacity="1"}),s.appendChild(n),n._signal=e,n._line=l,n._preview=a})),D(),h.timeScale().subscribeVisibleLogicalRangeChange(D);let A=e=>{r&&!r.contains(e.target)&&(r.style.opacity="0",r.style.visibility="hidden",f.querySelectorAll("line").forEach(e=>{"1"===e.style.opacity&&(e.style.opacity="0")}))};return document.addEventListener("click",A),(n=new ResizeObserver(()=>{g.current&&t.clientWidth>0&&(g.current.applyOptions({width:t.clientWidth,height:Math.max(t.clientHeight,window.innerHeight-300,500)}),setTimeout(D,100))})).observe(t),()=>{document.removeEventListener("click",A),t.removeEventListener("mousedown",T),t.removeEventListener("mousemove",S),t.removeEventListener("mouseup",$),document.removeEventListener("click",E),j&&(j.remove(),j=null),k&&(k.remove(),k=null)}})(),()=>{i=!0,g.current&&(g.current.remove(),g.current=null),s&&s.remove(),r&&r.remove(),n&&n.disconnect()}},[m,C]),D)?(0,t.jsxs)("div",{className:"max-w-7xl mx-auto space-y-6",children:[(0,t.jsxs)("div",{className:"flex items-center justify-between",children:[(0,t.jsxs)("div",{className:"flex items-center gap-4",children:[(0,t.jsxs)(a.default,{href:"/influencers",className:"flex items-center gap-2 text-gray-600 hover:text-gray-900",children:[(0,t.jsx)(s.ArrowLeft,{className:"w-4 h-4"}),"뒤로가기"]}),(0,t.jsxs)("div",{children:[(0,t.jsx)("h1",{className:"text-2xl font-bold text-gray-900",children:E}),(0,t.jsxs)("p",{className:"text-sm text-gray-500",children:[x,"/USD"]})]})]}),(0,t.jsxs)("div",{className:"flex items-center gap-3",children:[(0,t.jsxs)("div",{className:"flex items-center gap-2 text-sm text-gray-600",children:[(0,t.jsx)(n.Users,{className:"w-4 h-4"}),S.length,"개 시그널"]}),(0,t.jsxs)("div",{className:"flex items-center gap-2 text-sm text-gray-600",children:[(0,t.jsx)(r.TrendingUp,{className:"w-4 h-4"}),$.length,"명 인플루언서"]})]})]}),(0,t.jsx)("div",{className:"bg-white rounded-xl border border-gray-200 p-4",children:(0,t.jsx)("div",{className:"flex flex-wrap gap-4",children:(0,t.jsxs)("div",{className:"space-y-2",children:[(0,t.jsx)("label",{className:"text-sm font-medium text-gray-700",children:"인플루언서"}),(0,t.jsxs)("div",{className:"flex flex-wrap gap-2",children:[(0,t.jsxs)("button",{onClick:()=>N("ALL"),className:`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${"ALL"===w?"bg-blue-500 text-white":"bg-gray-100 text-gray-700 hover:bg-gray-200"}`,children:["전체 (",S.length,")"]}),$.map(e=>{let i=S.filter(t=>t.influencer===e).length;return(0,t.jsxs)("button",{onClick:()=>N(e),className:`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${w===e?"bg-blue-500 text-white":"bg-gray-100 text-gray-700 hover:bg-gray-200"}`,children:[e," (",i,")"]},e)})]})]})})}),(0,t.jsx)("div",{className:"bg-white rounded-xl border border-gray-200 overflow-hidden",children:y?(0,t.jsx)("div",{style:{height:"calc(100vh - 280px)",minHeight:400},className:"flex items-center justify-center",children:(0,t.jsxs)("div",{className:"text-center",children:[(0,t.jsx)("div",{className:"animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"}),(0,t.jsx)("p",{className:"text-gray-500",children:"차트 로딩중..."})]})}):b?(0,t.jsx)("div",{style:{height:"calc(100vh - 280px)",minHeight:400},className:"flex items-center justify-center",children:(0,t.jsx)("p",{className:"text-red-500",children:b})}):(0,t.jsx)("div",{ref:u,style:{width:"100%",height:"calc(100vh - 280px)",minHeight:400,position:"relative"}})}),(0,t.jsx)("div",{className:"bg-white rounded-xl border border-gray-200 p-4",children:(0,t.jsxs)("div",{className:"space-y-2",children:[(0,t.jsx)("label",{className:"text-sm font-medium text-gray-700",children:"시그널 타입"}),(0,t.jsxs)("div",{className:"flex flex-wrap gap-2",children:[(0,t.jsx)("button",{onClick:()=>k("ALL"),className:`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${"ALL"===j?"bg-purple-500 text-white":"bg-gray-100 text-gray-700 hover:bg-gray-200"}`,children:"전체"}),Object.entries(p).map(([e,i])=>{let s=S.filter(t=>t.signalType===e).length;return 0===s?null:(0,t.jsxs)("button",{onClick:()=>k(e),className:`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${j===e?"text-white":"text-gray-700 hover:bg-gray-200"}`,style:{backgroundColor:j===e?c[e]:void 0},children:[i," (",s,")"]},e)})]})]})}),(0,t.jsxs)("div",{className:"bg-white rounded-xl border border-gray-200 p-4",children:[(0,t.jsxs)("h3",{className:"text-lg font-semibold mb-4",children:["시그널 목록 (",C.length,"개)"]}),(0,t.jsx)("div",{className:"space-y-3 max-h-80 overflow-y-auto",children:C.sort((e,t)=>new Date(t.videoDate).getTime()-new Date(e.videoDate).getTime()).map(e=>(0,t.jsxs)("div",{className:"flex items-start gap-3 p-3 bg-gray-50 rounded-lg",children:[(0,t.jsx)(l.Badge,{className:"text-white text-xs font-bold shrink-0",style:{backgroundColor:c[e.signalType]},children:p[e.signalType]}),(0,t.jsxs)("div",{className:"flex-1",children:[(0,t.jsxs)("div",{className:"flex items-center gap-2 mb-1",children:[(0,t.jsx)("span",{className:"font-medium text-gray-900",children:e.influencer}),(0,t.jsx)("span",{className:"text-sm text-gray-500",children:e.videoDate}),(0,t.jsx)("span",{className:"text-xs text-gray-400",children:e.timestamp})]}),(0,t.jsx)("p",{className:"text-sm text-gray-700 mb-2",children:e.content}),e.youtubeLink&&(0,t.jsx)("a",{href:e.youtubeLink,target:"_blank",rel:"noopener noreferrer",className:"text-red-600 hover:text-red-700 text-xs font-medium",children:"YouTube에서 보기 →"})]})]},e.id))})]})]}):(0,t.jsxs)("div",{className:"max-w-6xl mx-auto p-6",children:[(0,t.jsxs)(a.default,{href:"/influencers",className:"flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6",children:[(0,t.jsx)(s.ArrowLeft,{className:"w-4 h-4"}),"뒤로가기"]}),(0,t.jsx)("div",{className:"text-center py-12",children:(0,t.jsx)("p",{className:"text-gray-500",children:"지원하지 않는 종목입니다."})})]})}e.s(["default",()=>x])},22886,e=>{e.v(t=>Promise.all(["static/chunks/af1bdbfcb2157648.js"].map(t=>e.l(t))).then(()=>t(53051)))}]);