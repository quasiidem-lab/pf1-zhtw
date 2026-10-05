# -*- coding: utf-8 -*-
r"""pf1-zhtw 發版：建置 → 驗證 → 同步進發布倉庫 → 升版號 → commit → push → GitHub Release。

為什麼有這支（2026-10-05）：
  建置工作區在 D:\TRPG\4_工具與筆記\pf1-zhtw\（本檔所在），真正發布的是 Foundry 本機資料夾裡的 git 倉庫
  C:\Users\User\AppData\Local\FoundryVTT\Data\modules\pf1-zhtw\（remote quasiidem-lab/pf1-zhtw，公開）。
  以前兩邊靠手動複製，10-05 發現 D 槽改了 PF1.Aura（靈氳）但發布倉庫還停在 v0.1.3 的「靈光」。
  Forge 是用 manifest（releases/latest/download/module.json）裝的，發新 Release 後 Forge 端才看得到更新。

用法：
  python release.py                     只建置、驗證、比對發布倉庫差在哪，什麼都不寫
  python release.py --sync              再把 _build\*.py 與 lang\zh-tw.json 複製進發布倉庫（不 commit）
  python release.py --publish "說明"     同步＋升 patch 版號＋commit＋push＋建 Release（module.json、module.zip）
                                        **這一步會公開發布，要他點頭才跑**

module.zip 用 `git archive` 打包：倉庫的 .gitattributes 把 _build/ 設成 export-ignore，跟 v0.1.x 的包一致。
壞掉時：
  - 建置或驗證失敗 → 先看 build.bat 的輸出，這支不會往下走
  - push 被拒 → 發布倉庫有別處推上去的 commit，先 git pull 再重跑
  - gh 沒登入 → `gh auth status`
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
REPO = r'C:\Users\User\AppData\Local\FoundryVTT\Data\modules\pf1-zhtw'
GH = 'quasiidem-lab/pf1-zhtw'
SYNC = [os.path.join('lang', 'zh-tw.json')] + [os.path.join('_build', f) for f in
                                                ('build_zhtw.py', 'verify_zhtw.py', 'audit_all.py', 'build.bat', 'release.py')]


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    if check and r.returncode:
        sys.exit('失敗：%s\n%s' % (' '.join(cmd), (r.stdout + r.stderr)[-1500:]))
    return r.stdout


def flat(d, p=''):
    out = {}
    for k, v in d.items():
        kk = p + '.' + k if p else k
        out.update(flat(v, kk) if isinstance(v, dict) else {kk: v})
    return out


def main():
    publish = '--publish' in sys.argv
    sync = publish or '--sync' in sys.argv
    note = ''
    if publish:
        i = sys.argv.index('--publish')
        note = sys.argv[i + 1] if i + 1 < len(sys.argv) else ''
        if not note:
            sys.exit('--publish 要給一句說明（會當 commit 與 Release 標題）')

    # 1. 建置＋驗證（build.bat 驗證沒過會回非零）
    print(run(['cmd', '/c', os.path.join(HERE, 'build.bat')], cwd=HERE).strip().splitlines()[-1])
    shutil.copyfile(os.path.join(HERE, 'pf1-zhtw-preview.json'), os.path.join(WORK, 'lang', 'zh-tw.json'))

    # 2. 跟發布倉庫比
    new = flat(json.load(open(os.path.join(WORK, 'lang', 'zh-tw.json'), encoding='utf-8')))
    old = flat(json.load(open(os.path.join(REPO, 'lang', 'zh-tw.json'), encoding='utf-8')))
    diff = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
    print('譯文跟發布倉庫差 %d 個鍵' % len(diff))
    for k in diff[:30]:
        print('  %s：%s → %s' % (k, old.get(k), new.get(k)))
    if not sync:
        return
    for rel in SYNC:
        src = os.path.join(WORK, rel)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(REPO, rel))
    print('已同步進發布倉庫：%s' % REPO)
    if not publish:
        return
    if not run(['git', 'status', '--porcelain'], cwd=REPO).strip():
        sys.exit('發布倉庫沒有變化，不發版')

    # 3. 升 patch 版號（發布倉庫的 module.json 是正本，工作區那份跟著抄）
    mj = os.path.join(REPO, 'module.json')
    m = json.load(open(mj, encoding='utf-8'))
    a, b, c = (int(x) for x in m['version'].split('.'))
    ver = '%d.%d.%d' % (a, b, c + 1)
    txt = open(mj, encoding='utf-8').read()
    txt = re.sub(r'("version":\s*")[^"]+(")', r'\g<1>%s\g<2>' % ver, txt, count=1)
    open(mj, 'w', encoding='utf-8', newline='\n').write(txt)
    shutil.copyfile(mj, os.path.join(WORK, 'module.json'))
    tag = 'v' + ver

    # 4. commit、push、Release
    run(['git', 'add', '-A'], cwd=REPO)
    run(['git', 'commit', '-m', '%s：%s' % (tag, note)], cwd=REPO)
    run(['git', 'push', 'origin', 'HEAD'], cwd=REPO)
    zp = os.path.join(HERE, 'module.zip')
    run(['git', 'archive', '--format=zip', '-o', zp, 'HEAD'], cwd=REPO)
    body = '%s\n\n變動的鍵：\n%s' % (note, '\n'.join('- `%s`：%s → %s' % (k, old.get(k), new.get(k)) for k in diff[:50]))
    run(['gh', 'release', 'create', tag, mj, zp, '-R', GH, '--title', '%s — %s' % (tag, note), '--notes', body])
    os.remove(zp)
    print('已發布 %s：https://github.com/%s/releases/tag/%s' % (tag, GH, tag))
    print('Forge 端：Foundry 設定畫面的「附加模組」按更新（或 Forge 的 Bazaar 檢查更新）')


if __name__ == '__main__':
    main()
