from pathlib import Path

p = Path('templates/crm/dashboard.html')
s = p.read_text(encoding='utf-8')

css = '''
<style id="columns-menu-final-fix">
.columns-box{
  width:260px!important;
  right:16px!important;
  top:118px!important;
  padding:8px 0!important;
  border-radius:8px!important;
  background:#fff!important;
  box-shadow:0 8px 24px rgba(0,0,0,.18)!important;
}
.columns-box label{
  display:flex!important;
  flex-direction:row!important;
  align-items:center!important;
  justify-content:flex-start!important;
  gap:8px!important;
  padding:7px 14px!important;
  margin:0!important;
  font-size:14px!important;
  line-height:18px!important;
  color:#263238!important;
  text-align:left!important;
  white-space:nowrap!important;
}
.columns-box label:hover{
  background:#f3f6f9!important;
}
.columns-box input[type="checkbox"]{
  width:16px!important;
  height:16px!important;
  min-height:16px!important;
  margin:0!important;
  flex:0 0 16px!important;
  accent-color:#1976d2!important;
}
</style>
'''

start = s.find('<style id="columns-menu-final-fix">')
if start != -1:
    end = s.find('</style>', start)
    s = s[:start] + css + s[end + len('</style>'):]
else:
    s = s.replace('</head>', css + '</head>')

# Replace the JS that builds the columns menu so checkbox is left and text is right.
old = "box.innerHTML=cols.map(c=>'<label><input type=\"checkbox\" '+(st[c[0]]===false?'':'checked')+' onchange=\"setCol(\\\''+c[0]+'\\\',this.checked)\"> '+c[1]+'</label>').join('');"
new = "box.innerHTML=cols.map(c=>'<label><input type=\"checkbox\" '+(st[c[0]]===false?'':'checked')+' onchange=\"setCol(\\\''+c[0]+'\\\',this.checked)\"><span>'+c[1]+'</span></label>').join('');"
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('OK: columns menu layout fixed')
