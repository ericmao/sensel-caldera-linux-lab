# 教學指南 PDF 來源

**唯一 Markdown 來源：** [`../TRAINING-GUIDE-2.1.md`](../TRAINING-GUIDE-2.1.md)

舊版 `SenseL_Caldera_Linux_Lab_教學指南_v2.0.pdf` 已由 v2.1 取代。請勿直接編輯 PDF；改 Markdown 後重新匯出。

## 匯出 PDF（需 pandoc）

```bash
bash scripts/export-training-guide-pdf.sh
```

輸出：`training/pdf/SenseL_Caldera_Linux_Lab_教學指南_v2.1.pdf`

若未安裝 pandoc：

- macOS：`brew install pandoc basictex`（或 mactex）
- Ubuntu：`sudo apt install pandoc texlive-xetex`
- Windows： [Pandoc 安裝程式](https://pandoc.org/installing.html) + MiKTeX

亦可用 Typora、VS Code Markdown PDF 等工具，以 `TRAINING-GUIDE-2.1.md` 為輸入。

## v2.1 相對 v2.0 PDF 新增章節

- 部署模式（Docker macOS/Windows vs Ubuntu VM SPAN）
- Chain C 雙靶機模擬橫向（完整 8 步）
- NDR Chain（SEN-NDR-LNX-01）與 Suricata SID
- 三層關聯（Caldera × Wazuh × Suricata）
- Edge Console :8090 雲端註冊
