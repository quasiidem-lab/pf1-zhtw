# -*- coding: utf-8 -*-
"""建置 PF1 系統介面繁體中文語言檔。

策略：
  1. 以 OpenCC s2tw 做字形轉換（不做台灣用語替換，避免 PF1 術語被轉壞）
  2. 再套一份人工審定的用語替換表（只採納 s2twp 轉對的部分）
  3. 保護清單：PF1 專有術語，任何替換都不得動到

來源：xgg-mod-chn (MIT, Copyright (c) 2026 EzithiStar) 的 lang/pf1-system.json
"""
import json, os, re, sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding='utf-8')
import opencc

DATA = r'C:\Users\User\AppData\Local\FoundryVTT\Data'
SRC = os.path.join(DATA, 'modules', 'xgg-mod-chn', 'lang', 'pf1-system.json')
EN = os.path.join(DATA, 'systems', 'pf1', 'lang', 'en.json')

cc = opencc.OpenCC('s2tw')  # 只轉字形

# ---------------------------------------------------------------
# 用語替換表：s2twp 轉對的部分，人工挑出後採納
# 順序有意義，長詞在前避免被短詞先吃掉
# ---------------------------------------------------------------
TERM_MAP = OrderedDict([
    # 介面通用詞（台灣慣用）
    ('默認', '預設'),
    ('鏈接', '連結'),
    ('信息', '資訊'),
    ('數據', '資料'),
    ('激活', '啟用'),
    ('剪貼板', '剪貼簿'),
    ('鼠標', '滑鼠'),
    ('字段', '欄位'),
    ('查看', '檢視'),
    ('集成', '整合'),
    ('調用', '呼叫'),
    ('註冊表', '登錄檔'),
    ('發佈', '發布'),
    ('創建', '建立'),
    ('添加', '新增'),
    ('加載', '載入'),
    ('緩存', '快取'),
    ('屏幕', '螢幕'),
    ('視頻', '影片'),
    ('文件夾', '資料夾'),
    ('對話框', '對話方塊'),
    ('復選框', '核取方塊'),
    ('下拉框', '下拉選單'),
    ('刷新', '重新整理'),
    ('質量', '品質'),
    ('進度條', '進度列'),
    ('拖拽', '拖曳'),
    ('可選', '選用'),
    ('布爾', '布林'),
])

# ---------------------------------------------------------------
# 保護清單：PF1 專有術語，替換表不得動到
# 這些詞若被上面的 TERM_MAP 誤傷，會在這裡還原
# ---------------------------------------------------------------
PROTECTED = [
    '遠程',      # ranged，絕不可轉成「遠端」
    '類型',      # 規則書用「類型」，非「型別」
    '重載',      # reload，非「過載」
    '點擊',      # 台灣桌遊圈通用
    '腳本',      # 非「指令碼」
    '過濾器',
    '合集包',
    '施法',
    '豁免',
    '先攻',
    '戰技',
]


# ---------------------------------------------------------------
# 逐鍵覆寫：上游簡體稿本身就譯錯的地方，字形轉換救不了
#
# 這兩條都是「同一個英文詞在不同語境有不同意思」，上游挑錯了語境：
#
#   PF1.Save   = "Save"
#       上游作「豁免」。但系統裡它只出現在表單的送出按鈕
#       （label:"PF1.Save", icon:"fa-floppy-disk"），是「儲存」。
#       真正的豁免另有 PF1.SavingThrow（豁免檢定）與
#       PF1.SavingThrowFort/Ref/Will，不缺這一條。
#
#   PF1.Weight = "Weight"
#       上游作「体重」。角色卡的 system.details.weight 確實是體重，
#       但同一個鍵也用在容器內容物重量（templates/items/container.hbs），
#       那裡顯示的是 weight.contents 加單位，講「體重」不通。
#       改用中性的「重量」兩邊都成立；物品另有 PF1.ItemWeight。
# ---------------------------------------------------------------
KEY_OVERRIDE = {
    # 語境誤譯（上游挑錯語境，見上方說明）
    'PF1.Save': '儲存',
    'PF1.Weight': '重量',

    # 2026-10-05 他裁定 aura 一律「靈氳」（見 pf1-glossary README「Aura 一律靈氳」）；上游作灵光
    'PF1.Aura.Single': '靈氳',
    'PF1.Aura.Plural': '靈氳',

    # 人工審定的譯名。這些原本只存在於輸出檔，未回寫進本檔，
    # 導致 2026-08-30 重建時整批被蓋回上游用詞（v0.1.2 的教訓）。
    # 放在這裡才不會再被重建洗掉。
    'PF1.Alignments.l': '守序',
    'PF1.Alignments.le': '守序邪惡',
    'PF1.Alignments.lg': '守序善良',
    'PF1.Alignments.ln': '守序中立',
    'PF1.Calendar.Months.8.Name': '奧羅登 (Arodus)',
    'PF1.Chat.Visibility.Blind': '暗骰',
    'PF1.Condition.energyDrain': '能量流失',
    'PF1.CreatureSubTypes.adlet': '狼妖',
    'PF1.CreatureSubTypes.agathion': '衛使',
    'PF1.CreatureSubTypes.archon': '聖使',
    'PF1.CreatureSubTypes.astomoi': '阿斯托莫伊人',
    'PF1.CreatureSubTypes.azata': '靈使',
    'PF1.CreatureSubTypes.blight': '荒疫怪',
    'PF1.CreatureSubTypes.darkFolk': '幽暗之民',
    'PF1.CreatureSubTypes.demodand': '神孽',
    'PF1.CreatureSubTypes.derro': '迪洛人',
    'PF1.CreatureSubTypes.div': '妖靈',
    'PF1.CreatureSubTypes.extraplanar': '跨位面',
    'PF1.CreatureSubTypes.gray': '小灰人',
    'PF1.CreatureSubTypes.herald': '令使',
    'PF1.CreatureSubTypes.hive': '巢群',
    'PF1.CreatureSubTypes.kami': '神靈',
    'PF1.CreatureSubTypes.lawful': '守序',
    'PF1.CreatureSubTypes.leshy': '萊西',
    'PF1.CreatureSubTypes.manasaputra': '聖仙',
    'PF1.CreatureSubTypes.mortic': '死靈裔',
    'PF1.CreatureSubTypes.munavri': '白化人',
    'PF1.CreatureSubTypes.robot': '機體',
    'PF1.CreatureSubTypes.skinwalker': '獸態人',
    'PF1.CreatureSubTypes.spawnOfRovagug': '拉瓦古格之嗣',
    'PF1.CreatureSubTypes.troop': '部隊',
    'PF1.DomainSlotValue': '領域/學派槽',
    'PF1.Error.NoMacroID': "未找到 ID 為 '{id}' 的巨集",
    'PF1.Help/Items/Script-Calls': '# 腳本呼叫\n\n大多數物品都有某些類別的腳本呼叫，這些是在該物品的特定事件下運行的巨集和內聯腳本的組合。\n',
    'PF1.Inventory': '物品欄',
    'PF1.KEYBINDINGS.ForceShowItem.Hint': '在使用物品巨集時，強制在聊天欄中顯示該物品卡片',
    'PF1.Language.munavri': '白化人語',
    'PF1.Language.reptoid': '爬蟲語',
    'PF1.Language.syrinx': '貓頭鷹人語',
    'PF1.Language.tekritanin': '泰克立坦語',
    'PF1.Language.vegepygmy': '孢子人語',
    'PF1.Language.yaddithian': '亞狄斯語',
    'PF1.Materials.Types.angelSkin': '天使皮',
    'PF1.Materials.Types.eelHide': '電鰻革',
    'PF1.Materials.Types.horacalcum': '時銅',
    'PF1.NPCs': 'NPC們',
    'PF1.PACKS.macros': '示例巨集',
    'PF1.PCs': 'PC們',
    'PF1.SkillKAr': '知識（奧秘）',
    'PF1.SkillKDu': '知識（地城）',
    'PF1.SkillKEn': '知識（工程）',
    'PF1.SkillKGe': '知識（地理）',
    'PF1.SkillKHi': '知識（歷史）',
    'PF1.SkillKLo': '知識（地方）',
    'PF1.SkillKNa': '知識（自然）',
    'PF1.SkillKNo': '知識（貴族）',
    'PF1.SkillKPl': '知識（位面）',
    'PF1.SkillKRe': '知識（宗教）',
    'PF1.SpellLevels.0': '0環 (戲法/禱念/念力)',
    'PF1.Subtypes.Item.implant.cybertech.Single': '賽博科技植入物',
    'PF1.Tours.ActorSheet.TraitsSection.Content': "體型、感官、抗力、免疫... 這裡的所有條目都可以通過點擊 <i class='fas fa-edit'></i> 編輯，直接在輸入框中輸入或從下拉選單中選擇。<br><br>感官會自動配合 Foundry 光照系統工作，除了那些不支持並標記為 (<code>*</code>) 的感官。",
}


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


# Foundry 的插值變數 {xxx} 與 HTML 標籤不得被轉換
PLACEHOLDER = re.compile(r'(\{[^}]*\}|<[^>]+>|@[A-Za-z][\w.]*)')


def convert(text):
    """字形轉換 + 用語替換，保護插值變數與 HTML。"""
    if not isinstance(text, str) or not text:
        return text

    # 切出不可動的片段
    parts = PLACEHOLDER.split(text)
    out = []
    for i, seg in enumerate(parts):
        if PLACEHOLDER.fullmatch(seg or ''):
            out.append(seg)          # 原樣保留
            continue
        s = cc.convert(seg)          # 字形轉換
        for a, b in TERM_MAP.items():
            s = s.replace(a, b)      # 用語替換
        out.append(s)
    return ''.join(out)


def unflatten(flat):
    """把點分隔鍵還原成巢狀結構。"""
    root = {}
    for k, v in flat.items():
        parts = k.split('.')
        cur = root
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = v
    return root


if __name__ == '__main__':
    with open(SRC, encoding='utf-8-sig') as f:
        src = json.load(f)
    src_flat = flatten(src)

    with open(EN, encoding='utf-8-sig') as f:
        en_flat = flatten(json.load(f))

    result = {}
    protected_hits = []
    for k, v in src_flat.items():
        conv = convert(v)
        # 保護清單檢查：轉換後這些詞不該消失
        for p in PROTECTED:
            plain = cc.convert(v)
            if p in plain and p not in conv:
                protected_hits.append((k, p, plain, conv))
        result[k] = KEY_OVERRIDE.get(k, conv)

    print(f'來源字串數     : {len(src_flat)}')
    print(f'轉換後字串數   : {len(result)}')
    print(f'保護清單誤傷   : {len(protected_hits)}')
    if protected_hits:
        print()
        print('!! 保護詞被替換表誤傷，需修正 TERM_MAP:')
        for k, p, a, b in protected_hits[:10]:
            print(f'   {k}  [{p}]')
            print(f'      {a[:60]}')
            print(f'   -> {b[:60]}')

    # 覆蓋率
    covered = sum(1 for k in en_flat if k in result and result[k] != en_flat[k])
    print()
    print(f'PF1 英文鍵數   : {len(en_flat)}')
    print(f'繁中覆蓋       : {covered}  ({round(covered/len(en_flat)*100,1)}%)')

    out_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out_dir, 'pf1-zhtw-preview.json'), 'w', encoding='utf-8') as f:
        json.dump(unflatten(result), f, ensure_ascii=False, indent=2)

    print()
    print('=== 抽樣檢查（PF1 關鍵術語）===')
    samples = ['PF1.ActionTypes.rwak', 'PF1.ActionTypes.rsak', 'PF1.ActionTypes.rcman',
               'PF1.BuffTarRangedAttack', 'PF1.ClassType', 'PF1.Spellcasting.Type.Label',
               'PF1.CompendiumBrowser.ReloadPacks', 'PF1.CompendiumBrowser.ActiveFilters',
               'PF1.QuantityAdd', 'PF1.CreateItem', 'PF1.LevelUp.Add',
               'PF1.HelpSellMultiplier', 'PF1.CopyUuidToClipboard', 'PF1.FlagsBoolean',
               'PF1.LinkHelpClassAssociations']
    for k in samples:
        if k in result:
            print(f'  {k:<42} {result[k][:56]}')
