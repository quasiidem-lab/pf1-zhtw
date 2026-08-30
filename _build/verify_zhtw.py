# -*- coding: utf-8 -*-
"""驗證轉換後的繁中檔完整性。只輸出統計與異常鍵名，不列出譯文內容。"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = r'C:\Users\User\AppData\Local\FoundryVTT\Data'
SRC = os.path.join(DATA, 'modules', 'xgg-mod-chn', 'lang', 'pf1-system.json')
OUT = os.path.join(HERE, 'pf1-zhtw-preview.json')


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


src = flatten(json.load(open(SRC, encoding='utf-8-sig')))
dst = flatten(json.load(open(OUT, encoding='utf-8-sig')))

VAR = re.compile(r'\{[^}]*\}')
TAG = re.compile(r'<[^>]+>')
AT = re.compile(r'@[A-Za-z][\w.]*')

bad_var, bad_tag, bad_at, bad_cjk = [], [], [], []
# 手寫字元表易誤報，改用 OpenCC 反向驗證：
# 已是繁體的字串再轉一次 s2tw 應為不動點，有變化即代表殘留簡體。
import opencc
_cc = opencc.OpenCC('s2tw')


def has_simplified(text):
    if not isinstance(text, str) or not text:
        return False
    return _cc.convert(text) != text

for k, s in src.items():
    d = dst.get(k)
    if d is None:
        continue
    if sorted(VAR.findall(s)) != sorted(VAR.findall(d)):
        bad_var.append(k)
    if sorted(TAG.findall(s)) != sorted(TAG.findall(d)):
        bad_tag.append(k)
    if sorted(AT.findall(s)) != sorted(AT.findall(d)):
        bad_at.append(k)
    if has_simplified(d):
        bad_cjk.append(k)

print(f'來源鍵數           : {len(src)}')
print(f'輸出鍵數           : {len(dst)}')
print(f'鍵集合一致         : {set(src) == set(dst)}')
print()
print(f'插值變數 {{}} 不符  : {len(bad_var)}')
print(f'HTML 標籤不符      : {len(bad_tag)}')
print(f'@ 參照不符         : {len(bad_at)}')
print(f'殘留簡體字         : {len(bad_cjk)}')

for label, lst in (('插值', bad_var), ('HTML', bad_tag),
                   ('@參照', bad_at), ('殘簡', bad_cjk)):
    if lst:
        print()
        print(f'--- {label} 異常鍵（最多 15 個）---')
        for k in lst[:15]:
            print(f'   {k}')

ok = not (bad_var or bad_tag or bad_at or bad_cjk) and set(src) == set(dst)
print()
print('驗證結果:', 'PASS' if ok else 'FAIL')
