/* GoWithDME: indeks artis (/a/). Cari, filter huruf, urutan. Semua kartu sudah ada di HTML (bisa dibaca bot);
   skrip ini hanya menyembunyikan/mengurutkan ulang. URL tidak diubah. */
(function(){
  var root=document.getElementById("ax"); if(!root) return;
  var grid=root.querySelector(".ax-grid"), q=document.getElementById("ax-q"),
      empty=document.getElementById("ax-empty"), cnt=document.getElementById("ax-count");
  function fold(s){return (s.normalize?s.normalize("NFD").replace(/[\u0300-\u036f]/g,""):s).toLowerCase()}
  function compact(s){return s.replace(/[^a-z0-9]+/g,"")}
  var col=window.Intl&&Intl.Collator?new Intl.Collator("en",{numeric:true,sensitivity:"base"}):null;
  var items=[].map.call(grid.children,function(el){
    var n=fold(el.querySelector(".ax-n").textContent);
    return {el:el,n:n,c:compact(n),l:el.getAttribute("data-l"),t:el.hasAttribute("data-t")};
  });
  var byName=items.slice().sort(function(a,b){
    var x=a.c||a.n,y=b.c||b.n; return col?col.compare(x,y):(x<y?-1:x>y?1:0);
  });
  var st={q:"",l:"",s:"e"}, timer;
  function press(box,attr,val){
    [].forEach.call(box.querySelectorAll("button"),function(b){b.setAttribute("aria-pressed",String(b.getAttribute(attr)===val))});
  }
  function order(){
    var f=document.createDocumentFragment();
    (st.s==="a"?byName:items).forEach(function(it){f.appendChild(it.el)});
    grid.appendChild(f);
  }
  function apply(){
    var term=fold(st.q.trim()), ct=compact(term), words=term?term.split(/\s+/):[], def=!term&&!st.l&&st.s==="e", shown=0;
    items.forEach(function(it){
      var ok=(!st.l||it.l===st.l)&&(!term||(ct&&it.c.indexOf(ct)>-1)||words.every(function(w){return it.n.indexOf(w)>-1}));
      it.el.hidden=!ok;
      if(ok&&!(def&&it.t)) shown++;
    });
    root.classList.toggle("ax-def",def);
    cnt.textContent=(shown===1?root.getAttribute("data-f1"):root.getAttribute("data-fn")).replace("{n}",shown);
    empty.hidden=shown>0;
  }
  q.addEventListener("input",function(){
    clearTimeout(timer); timer=setTimeout(function(){st.q=q.value; apply()},90);
  });
  root.querySelector(".ax-az").addEventListener("click",function(e){
    var b=e.target.closest("button"); if(!b) return;
    st.l=b.getAttribute("data-l"); press(this,"data-l",st.l); apply();
  });
  root.querySelector(".ax-sort").addEventListener("click",function(e){
    var b=e.target.closest("button"); if(!b||b.getAttribute("data-s")===st.s) return;
    st.s=b.getAttribute("data-s"); press(this,"data-s",st.s); order(); apply();
  });
  document.getElementById("ax-reset").addEventListener("click",function(){
    st={q:"",l:"",s:"e"}; q.value="";
    press(root.querySelector(".ax-az"),"data-l",""); press(root.querySelector(".ax-sort"),"data-s","e");
    order(); apply(); q.focus();
  });
})();
