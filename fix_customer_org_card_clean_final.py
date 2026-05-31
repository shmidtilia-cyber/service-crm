from pathlib import Path
import re

p = Path('templates/crm/dashboard.html')
s = p.read_text()

# Remove previous conflicting customer/org UI patches completely.
markers = [
    'customer-org-switch-final',
    'customer-org-full-final',
    'full-company-card-final',
    'company-card-like-screen-final',
    'customer-org-card-clean-final',
    'org-card-exact-final',
]
for marker in markers:
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

fix = r'''
<style id="org-card-clean-one-version-final">
.customer-card-drawer{width:760px!important;right:-760px!important;background:#fff!important}.customer-card-drawer.show{right:0!important}.customer-card-head{height:58px!important;padding:0 18px!important;border-bottom:1px solid #e5e7eb!important;font-size:28px!important;font-weight:400!important}.customer-card-body{padding:0 18px 96px!important;overflow:auto!important}.customer-tabs{height:48px!important;margin:0 0 22px!important;padding:0!important;display:flex!important;align-items:end!important;gap:24px!important;border-bottom:1px solid #e5e7eb!important}.customer-tabs span{padding-bottom:12px!important;font-size:16px!important;color:#263238!important}.customer-tabs .active{color:#1976d2!important;border-bottom:2px solid #1976d2!important}.org-section{display:grid!important;grid-template-columns:300px 1fr!important;gap:24px!important;border-bottom:1px solid #e5e7eb!important;padding:20px 0 26px!important}.org-left{font-size:20px!important;font-weight:800!important;color:#263238!important}.org-right{min-width:0!important}.org-right .customer-field{margin:0 0 16px!important}.org-right .customer-field label{display:block!important;margin:0 0 7px!important;font-size:16px!important;font-weight:700!important;color:#263238!important}.org-right input,.org-right textarea,.org-right select{width:100%!important;min-height:42px!important;border:1px solid #cfd6dc!important;border-radius:5px!important;padding:9px 12px!important;font-size:16px!important;background:#fff!important}.org-right textarea{min-height:88px!important;resize:vertical!important}.customer-type-switch{display:inline-flex!important;width:auto!important;border:1px solid #cfd6dc!important;border-radius:5px!important;overflow:hidden!important}.customer-type-switch label{margin:0!important;padding:0!important}.customer-type-switch input{display:none!important}.customer-type-switch span{display:block!important;padding:10px 22px!important;background:#fff!important;cursor:pointer!important;font-size:16px!important}.customer-type-switch input:checked+span{background:#e9eef3!important;font-weight:700!important;box-shadow:inset 0 1px 4px rgba(0,0,0,.12)!important}.org-row-btn{display:grid!important;grid-template-columns:1fr 58px!important;gap:8px!important}.org-icon-btn{height:42px!important;border:1px solid #cfd6dc!important;background:#fff!important;border-radius:5px!important;cursor:pointer!important}.org-checks{display:flex!important;gap:18px!important;align-items:center!important;margin:8px 0 8px!important}.org-checks label{display:flex!important;align-items:center!important;gap:7px!important;font-size:16px!important}.org-checks input{width:20px!important;height:20px!important;min-height:20px!important}.org-add-phone{display:inline-block!important;color:#1976d2!important;margin:0 0 16px!important;font-size:16px!important;text-decoration:none!important}.customer-card-drawer[data-customer-type="person"] .org-only{display:none!important}.customer-card-drawer[data-customer-type="company"] .person-only{display:none!important}.customer-vars,.customer-org-box,.company-full-fields{display:none!important}
</style>
<script id="org-card-clean-one-version-final">
(function(){
function input(name,value,placeholder){const e=document.createElement('input');e.name=name;e.value=value||'';e.placeholder=placeholder||'';return e}
function textarea(name,value,placeholder){const e=document.createElement('textarea');e.name=name;e.value=value||'';e.placeholder=placeholder||'';return e}
function q(root,sel){return root.querySelector(sel)}
function ensureHidden(form,name,value){let e=form.querySelector('[name="'+name+'"]');if(!e){e=document.createElement('input');e.type='hidden';e.name=name;form.appendChild(e)} if(value!==undefined)e.value=value||'';return e}
function addField(parent,label,el){if(!el)return;const box=document.createElement('div');box.className='customer-field';box.innerHTML='<label>'+label+'</label>';box.appendChild(el);parent.appendChild(box)}
function addSection(body,title,extraClass){const sec=document.createElement('div');sec.className='org-section '+(extraClass||'');sec.innerHTML='<div class="org-left">'+title+'</div><div class="org-right"></div>';body.appendChild(sec);return sec.querySelector('.org-right')}
function rebuild(drawer){
 if(drawer.dataset.cleanOrgBuiltFinal==='1')return; drawer.dataset.cleanOrgBuiltFinal='1';
 const body=q(drawer,'.customer-card-body'); if(!body)return;
 const tabs=q(drawer,'.customer-tabs'); const typeSwitch=q(drawer,'.customer-type-switch'); const supplier=q(drawer,'input[name="is_supplier"]')?.closest('label');
 const name=q(drawer,'input[name="customer_name"]'); const lastName=q(drawer,'input[name="customer_last_name"]'); const phone=q(drawer,'input[name="customer_phone"]'); const email=q(drawer,'input[name="customer_email"]'); const address=q(drawer,'input[name="customer_address"]');
 const allowWhatsapp=q(drawer,'input[name="allow_whatsapp"]'); const allowSms=q(drawer,'input[name="allow_sms"]'); const allowEmail=q(drawer,'input[name="allow_email"]');
 const inn=q(drawer,'input[name="customer_inn"]'); const comment=q(drawer,'textarea[name="customer_comment"]'); const discountCard=q(drawer,'input[name="customer_discount_card"]'); const serviceDiscount=q(drawer,'input[name="customer_service_discount"]'); const productDiscount=q(drawer,'input[name="customer_product_discount"]');
 const ogrn=q(drawer,'input[name="customer_ogrn"]')||input('customer_ogrn'); const kpp=q(drawer,'input[name="customer_kpp"]')||input('customer_kpp'); const legalAddress=q(drawer,'textarea[name="customer_legal_address"]')||textarea('customer_legal_address'); const director=q(drawer,'input[name="customer_director"]')||input('customer_director'); const bankName=q(drawer,'input[name="customer_bank_name"]')||input('customer_bank_name'); const bankAccount=q(drawer,'input[name="customer_bank_account"]')||input('customer_bank_account'); const corr=q(drawer,'input[name="customer_correspondent_account"]')||input('customer_correspondent_account'); const bik=q(drawer,'input[name="customer_bik"]')||input('customer_bik');
 ensureHidden(drawer,'customer_requisites',''); body.innerHTML=''; if(tabs)body.appendChild(tabs);
 const general=addSection(body,'Общие'); if(typeSwitch){const box=document.createElement('div');box.className='customer-field';box.innerHTML='<label>Тип</label>';box.appendChild(typeSwitch);general.appendChild(box)} if(supplier){supplier.style.display='flex';supplier.style.alignItems='center';supplier.style.gap='8px';supplier.style.margin='8px 0 18px';general.appendChild(supplier)} const manager=document.createElement('div');manager.className='customer-field';manager.innerHTML='<label>Менеджер</label><div style="display:flex;align-items:center;gap:10px"><span style="width:34px;height:34px;border-radius:50%;background:#ff7a00;display:inline-grid;place-items:center;color:#fff;font-weight:800">И</span> Илья</div>';general.appendChild(manager);
 const contact=addSection(body,'Контактная информация'); addField(contact,'Название компании <span style="color:#e53935">*</span>',name); if(lastName){const box=document.createElement('div');box.className='customer-field person-only';box.innerHTML='<label>Фамилия</label>';box.appendChild(lastName);contact.appendChild(box)} if(phone){const box=document.createElement('div');box.className='customer-field';box.innerHTML='<label>Домашний⌄</label><div class="org-row-btn"></div>';const row=box.querySelector('.org-row-btn');row.appendChild(phone);const btn=document.createElement('button');btn.type='button';btn.className='org-icon-btn';btn.textContent='⋮';row.appendChild(btn);contact.appendChild(box)} const checks=document.createElement('div');checks.className='org-checks'; if(allowWhatsapp){const l=document.createElement('label');l.appendChild(allowWhatsapp);l.append('WhatsApp');checks.appendChild(l)} if(allowSms){const l=document.createElement('label');l.appendChild(allowSms);l.append('SMS');checks.appendChild(l)} contact.appendChild(checks); const addPhone=document.createElement('a');addPhone.href='javascript:void(0)';addPhone.className='org-add-phone';addPhone.textContent='+ Добавить телефон';contact.appendChild(addPhone); if(email){const box=document.createElement('div');box.className='customer-field';box.innerHTML='<label>Email</label><div class="org-row-btn"></div>';const row=box.querySelector('.org-row-btn');row.appendChild(email);const btn=document.createElement('button');btn.type='button';btn.className='org-icon-btn';btn.textContent='✉';row.appendChild(btn);contact.appendChild(box)} if(allowEmail){const l=document.createElement('label');l.style.display='flex';l.style.alignItems='center';l.style.gap='8px';l.style.margin='-4px 0 16px';l.appendChild(allowEmail);l.append('Согласен получать Email');contact.appendChild(l)} if(address){const box=document.createElement('div');box.className='customer-field';box.innerHTML='<label>Адрес</label><div class="org-row-btn"></div>';const row=box.querySelector('.org-row-btn');row.appendChild(address);const btn=document.createElement('button');btn.type='button';btn.className='org-icon-btn';btn.textContent='⌖';row.appendChild(btn);contact.appendChild(box)} const ad=document.createElement('div');ad.className='customer-field';ad.innerHTML='<label>Рекламная кампания</label><select><option>Яндекс Asus Ноутбуки</option><option>Google</option><option>Наружная реклама</option></select>';contact.appendChild(ad);
 const req=addSection(body,'Реквизиты компании','org-only'); addField(req,'ОГРН',ogrn); addField(req,'ИНН',inn); addField(req,'КПП',kpp); addField(req,'Юридический адрес',legalAddress); addField(req,'Директор',director);
 const bank=addSection(body,'Банковские реквизиты','org-only'); addField(bank,'Название банка',bankName); addField(bank,'Р/с',bankAccount); addField(bank,'К/с',corr); addField(bank,'БИК',bik);
 const other=addSection(body,'Прочее'); addField(other,'Скидочная карта',discountCard); addField(other,'Скидка на услуги, %',serviceDiscount); addField(other,'Скидка на товары, %',productDiscount); addField(other,'Примечание',comment);
}
function updateType(drawer){const checked=drawer.querySelector('input[name="customer_type"]:checked');drawer.dataset.customerType=checked?checked.value:'person'}
function patch(){document.querySelectorAll('.customer-card-drawer').forEach(drawer=>{rebuild(drawer);drawer.querySelectorAll('input[name="customer_type"]').forEach(radio=>{if(radio.dataset.cleanOrgReadyFinal==='1')return;radio.dataset.cleanOrgReadyFinal='1';radio.addEventListener('change',()=>updateType(drawer))});updateType(drawer)})}
document.addEventListener('DOMContentLoaded',patch);setInterval(patch,700);
})();
</script>
'''

s = s.replace('</body>', fix + '\n</body>')
p.write_text(s)
print('OK: dashboard customer organization card fixed')
