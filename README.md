# PF1e 系統介面繁體中文

為 Foundry VTT 的 Pathfinder 1e 系統介面提供繁體中文（臺灣）翻譯。

## 這個模組翻什麼

只翻 **PF1 系統介面**——欄位標籤、按鈕、對話框、提示文字這類寫死在系統程式碼裡的字串。

**不翻**合集包內容（法術、專長、物品的名稱與描述）。那屬於 Babele 層，見下方「尚未涵蓋」。

## 涵蓋率

| 項目 | 數量 |
|---|---|
| PF1 系統英文鍵總數 | 2,438 |
| 本模組已譯 | 2,347（96.3%） |
| 未涵蓋 | 91 |

未涵蓋的 91 條絕大多數**不需要翻譯**：法術構材縮寫（V／S／M／DF）、幣值縮寫（PP／GP／SP／CP）、格式字串（`{value} gp`）、專有語言名（Munavri、Syrinx、Vegepygmy）。

## 安裝

Forge 或本機的模組管理器中，用 manifest URL 安裝；或直接把整個資料夾複製到 `Data/modules/pf1-zhtw/`。

安裝後在「設定 → 一般設定 → 語言」選擇繁體中文（`zh-tw`）。
選單顯示的名稱由已安裝的語系包決定，可能顯示為「正體中文」。

## 譯文來源與授權

譯文以 [xgg-mod-chn](https://github.com/EzithiStar/xgg_mod_chn)（MIT，Copyright (c) 2026 EzithiStar）的簡體譯稿為基礎，經：

1. OpenCC `s2tw` 字形轉換
2. 人工審定的用語替換表（採納台灣慣用詞）
3. PF1 術語保護清單（防止專有名詞被誤轉）

依 MIT 條款保留原始著作權聲明，見 [LICENSE](LICENSE)。

## 術語處理的關鍵決定

OpenCC 的 `s2twp`（含台灣用語轉換）在 PF1 語境下**會轉錯**，因此改用 `s2tw` 純字形轉換 + 自訂替換表。被明確排除的錯誤轉換：

| 簡體原文 | s2twp 會轉成 | 本模組採用 | 原因 |
|---|---|---|---|
| 远程 | 遠端 | **遠程** | PF1 的 ranged，非網路術語 |
| 类型 | 型別 | **類型** | 「型別」是程式術語 |
| 重载 | 過載 | **重載** | reload，語意完全不同 |
| 点击 | 點選 | **點擊** | 台灣桌遊圈通用 |
| 脚本 | 指令碼 | **腳本** | 較自然 |

採納的台灣慣用詞：默認→預設、鏈接→連結、信息→資訊、數據→資料、激活→啟用、剪貼板→剪貼簿、鼠標→滑鼠、字段→欄位、創建→建立、添加→新增。

完整替換表與保護清單見 `_build/build_zhtw.py`。

## 重新產生譯文

xgg-mod-chn 更新後，重跑建置即可：

```
python _build/build_zhtw.py     # 產出 pf1-zhtw-preview.json
python _build/verify_zhtw.py    # 驗證插值/HTML/殘簡，須 PASS
```

`build_zhtw.py` 直接讀取本機 `Data/modules/xgg-mod-chn/lang/pf1-system.json` 作為來源，路徑寫在腳本開頭。

`verify_zhtw.py` 檢查四項：鍵集合一致、插值變數 `{}` 完好、HTML 標籤完好、無殘留簡體（以 OpenCC 反向轉換偵測，非手寫字元表）。

## 尚未涵蓋

| 層 | 現況 | 阻礙 |
|---|---|---|
| 合集資料（法術／專長／物品） | 僅有簡體 [pf1e_compendium_chn](https://github.com/fvtt-cn/pf1e_compendium_chn)，14,909 條 | **該專案無授權聲明**，做繁中分支前需先取得授權 |
| 通用模組介面 | 22 個已裝模組完全無中文，6,255 條鍵 | 無人翻譯；多為設定選單，跑團少見 |

## 相關

核心介面（Foundry 本體）用 [foundry-core-zh-tw](https://gitlab.com/fvtt-zh_TW/foundry-core-zh-tw)。注意**版本要對應核心版本**：v13 核心須裝 13.351，裝成 14.363 會有 381 個鍵顯示英文。
