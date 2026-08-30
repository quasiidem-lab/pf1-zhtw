# -*- coding: utf-8 -*-
"""FVTT 中文翻譯缺口總盤點（介面層 A/B/C + 合集層 D）。"""
import json, os, sys, glob

sys.stdout.reconfigure(encoding='utf-8')

DATA = r'C:\Users\User\AppData\Local\FoundryVTT\Data'
APP = r'C:\Program Files\Foundry Virtual Tabletop\resources\app\public'
XGG = os.path.join(DATA, 'modules', 'xgg-mod-chn', 'lang')
CHN = os.path.join(DATA, 'modules', 'pf1e_compendium_chn')


def load(p):
    with open(p, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def flatten(node, prefix=''):
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            key = f'{prefix}.{k}' if prefix else k
            out.update(flatten(v, key))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.update(flatten(v, f'{prefix}[{i}]'))
    else:
        if prefix:
            out[prefix] = node if isinstance(node, str) else str(node)
    return out


def cmp_lang(en_path, tr_path):
    en = flatten(load(en_path))
    tr = flatten(load(tr_path)) if tr_path and os.path.exists(tr_path) else {}
    missing = [k for k in en if k not in tr]
    same = [k for k in en if k in tr and tr[k] == en[k]]
    done = len(en) - len(missing) - len(same)
    return len(en), done, len(missing), len(same)


def line(label, total, done, missing, same):
    pct = round(done / total * 100, 1) if total else 0.0
    print(f'{label:<44}{total:>7}{done:>8}{str(pct)+"%":>8}{missing:>8}{same:>7}')


print('=' * 82)
print('介面層（i18n）缺口盤點')
print('=' * 82)
print(f'{"層 / 對象":<44}{"英文鍵":>7}{"已譯":>8}{"覆蓋":>8}{"缺鍵":>8}{"同英文":>7}')
print('-' * 82)

# B層：Foundry 核心
t, d, m, s = cmp_lang(os.path.join(APP, 'lang', 'en.json'),
                      os.path.join(DATA, 'modules', 'foundry-core-zh-tw', 'lang', 'zh-tw.json'))
line('B 核心介面 / foundry-core-zh-tw (正體)', t, d, m, s)
core_tw = (t, d, m, s)

# A層：PF1 系統
pf1_en = os.path.join(DATA, 'systems', 'pf1', 'lang', 'en.json')
t, d, m, s = cmp_lang(pf1_en, os.path.join(DATA, 'systems', 'pf1', 'lang', 'cn.json'))
line('A PF1 系統介面 / 系統內建 cn.json', t, d, m, s)
t, d, m, s = cmp_lang(pf1_en, os.path.join(XGG, 'pf1-system.json'))
line('A PF1 系統介面 / xgg-mod-chn (簡體)', t, d, m, s)
pf1_sys = (t, d, m, s)

# A層：兩者合併後的實際覆蓋
en = flatten(load(pf1_en))
cn1 = flatten(load(os.path.join(DATA, 'systems', 'pf1', 'lang', 'cn.json')))
cn2 = flatten(load(os.path.join(XGG, 'pf1-system.json')))
merged_done = sum(1 for k in en
                  if (k in cn2 and cn2[k] != en[k]) or (k in cn1 and cn1[k] != en[k]))
line('A PF1 系統介面 / 兩者合併實際覆蓋', len(en), merged_done,
     len(en) - merged_done, 0)

print()
print('=' * 82)
print('C層 已裝模組介面：xgg-mod-chn 譯檔逐一對照')
print('=' * 82)

# 反向：以 xgg 譯檔為主，找本機對應模組
mod_en = {}
for name in os.listdir(os.path.join(DATA, 'modules')):
    md = os.path.join(DATA, 'modules', name)
    mj = os.path.join(md, 'module.json')
    if not os.path.exists(mj):
        continue
    try:
        m = load(mj)
    except Exception:
        continue
    for L in (m.get('languages') or []):
        if L.get('lang', '').startswith('en'):
            p = os.path.join(md, L.get('path', '').replace('/', os.sep))
            if os.path.exists(p):
                try:
                    mod_en[name] = flatten(load(p))
                except Exception:
                    pass
            break

print(f'{"xgg 譯檔":<30}{"鍵數":>7}  {"對應本機模組":<32}{"可驗證":>8}')
print('-' * 82)
xgg_total = 0
for fn in sorted(os.listdir(XGG)):
    if not fn.lower().endswith('.json'):
        continue
    try:
        tr = flatten(load(os.path.join(XGG, fn)))
    except Exception as e:
        print(f'{fn:<30}{"解析失敗":>7}  {"("+type(e).__name__+")":<32}{"—":>8}')
        continue
    xgg_total += len(tr)
    best, hit = None, 0
    for name, en2 in mod_en.items():
        h = sum(1 for k in tr if k in en2)
        if h > hit:
            best, hit = name, h
    if best and hit > 0:
        print(f'{fn:<30}{len(tr):>7}  {best:<32}{str(hit):>8}')
    else:
        print(f'{fn:<30}{len(tr):>7}  {"(本機未安裝，無法驗證)":<32}{"—":>8}')
print('-' * 82)
print(f'xgg-mod-chn 譯檔鍵總數: {xgg_total}')

print()
print('=' * 82)
print('D層 合集資料（Babele）：pf1e_compendium_chn 對照表')
print('=' * 82)
tr_dir = os.path.join(CHN, 'translations')
print(f'{"對照表檔案":<40}{"條目數":>8}{"MB":>8}')
print('-' * 82)
grand = 0
files = sorted(glob.glob(os.path.join(tr_dir, '*.json')))
for p in files:
    try:
        j = load(p)
    except Exception as e:
        print(f'{os.path.basename(p):<40}{"解析失敗":>8}')
        continue
    entries = j.get('entries')
    n = len(entries) if isinstance(entries, (dict, list)) else 0
    grand += n
    mb = round(os.path.getsize(p) / 1024 / 1024, 2)
    print(f'{os.path.basename(p):<40}{n:>8}{mb:>8}')
print('-' * 82)
print(f'對照表檔案數: {len(files)}   條目總數: {grand}')
