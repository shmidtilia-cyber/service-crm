from pathlib import Path

p = Path('templates/crm/dashboard.html')
s = p.read_text()

fix = r'''
<style id="remove-black-right-strip-hard-final">
/* Убираем полностью скрытые боковые панели, чтобы справа не оставалось черной полосы */
.drawer:not(.show),
.payment-drawer:not(.show),
.customer-card-drawer:not(.show),
.order-side-drawer:not(.show),
.service-add-panel:not(.show){
  display:none!important;
  visibility:hidden!important;
  opacity:0!important;
  box-shadow:none!important;
  pointer-events:none!important;
}

.drawer.show{
  display:grid!important;
  visibility:visible!important;
  opacity:1!important;
}

.payment-drawer.show,
.customer-card-drawer.show,
.order-side-drawer.show,
.service-add-panel.show{
  display:grid!important;
  visibility:visible!important;
  opacity:1!important;
}

.backdrop:not(.show),
.service-add-overlay:not(.show),
.order-side-overlay:not(.show){
  display:none!important;
  opacity:0!important;
  pointer-events:none!important;
}
</style>
<script id="remove-black-right-strip-hard-final">
(function(){
  function cleanHiddenDrawers(){
    document.querySelectorAll('.drawer,.payment-drawer,.customer-card-drawer,.order-side-drawer,.service-add-panel').forEach(function(el){
      if(!el.classList.contains('show')){
        el.style.display = 'none';
        el.style.visibility = 'hidden';
        el.style.opacity = '0';
        el.style.boxShadow = 'none';
        el.style.pointerEvents = 'none';
      }else{
        el.style.display = 'grid';
        el.style.visibility = 'visible';
        el.style.opacity = '1';
        el.style.pointerEvents = '';
      }
    });
  }

  var oldOpenCreate = window.openCreateDrawer;
  window.openCreateDrawer = function(){
    document.querySelectorAll('.drawer').forEach(function(d){d.style.display='none'});
    if(typeof oldOpenCreate === 'function') oldOpenCreate();
    cleanHiddenDrawers();
  };

  var oldOpenOrder = window.openOrderDrawer;
  window.openOrderDrawer = function(id){
    document.querySelectorAll('.drawer').forEach(function(d){d.style.display='none'});
    if(typeof oldOpenOrder === 'function') oldOpenOrder(id);
    cleanHiddenDrawers();
  };

  var oldClose = window.closeDrawer;
  window.closeDrawer = function(){
    if(typeof oldClose === 'function') oldClose();
    cleanHiddenDrawers();
  };

  document.addEventListener('DOMContentLoaded', cleanHiddenDrawers);
  setInterval(cleanHiddenDrawers, 300);
})();
</script>
'''

# Remove older versions of this fix if present
for marker in ['remove-hidden-drawer-shadow-final', 'remove-black-right-strip-hard-final']:
    while marker in s:
        idx = s.find(marker)
        style_start = s.rfind('<style', 0, idx)
        style_end = s.find('</style>', idx)
        script_start = s.rfind('<script', 0, idx)
        script_end = s.find('</script>', idx)
        if style_start != -1 and style_end != -1 and (script_start == -1 or style_start > script_start):
            s = s[:style_start] + s[style_end + len('</style>'):]
        elif script_start != -1 and script_end != -1:
            s = s[:script_start] + s[script_end + len('</script>'):]
        else:
            break

s = s.replace('</body>', fix + '\n</body>')
p.write_text(s)
print('OK: black right strip removed')
