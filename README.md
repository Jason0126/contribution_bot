# Contribution Bot
本專案是一個discord伺服器用的機器人，主要以python語言為主。

## 功能
主要是紀錄discord伺服器中的使用者，當使用者進出聊天頻道時，會進行時間的紀錄，並且在離開時就會進行時間的計算，計算使用者在聊天頻道所停留的時間。

## 指令
### !check
查詢發送者自身在discord伺服器中，所產生多少的貢獻時間以及相對應的貢獻等級。
### !check @member
查詢特定使用者在discord伺服器中，所產生多少的貢獻時間以及相對應的貢獻等級。

## 檔案說明
* contribution_bot(azure sql server).py - 此版本是將使用者的時間記錄以及貢獻數據，記錄在Microsoft Azure SQL Database裡。
* contribution_bot(local json).py - 此版本是將使用者的時間記錄以及貢獻數據，記錄在本地端的json檔裡。
* data.json - 此為使用(local json)版本時，負責儲存使用者的時間記錄以及貢獻數據。
