# 智慧視覺閱卷系統


[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/sunflower519sf/correct_exam/total?style=plastic&logo=github)](https://github.com/sunflower519sf/correct_exam/releases/latest)
[![GitHub latest version](https://img.shields.io/github/release/sunflower519sf/correct_exam?style=plastic&logo=github)](https://github.com/sunflower519sf/correct_exam/releases/latest)

![python version](https://img.shields.io/badge/python-3.11%2B-important?style=plastic&logo=python)
![GitHub License](https://img.shields.io/github/license/sunflower519sf/correct_exam?style=plastic)
![GitHub repo size](https://img.shields.io/github/repo-size/sunflower519sf/correct_exam?style=plastic)


## 功能介紹
- 閱卷系統用於在考試時快速的批改試卷，他是以視覺化的方式來讀取答案內容，所以輸入只需使用圖片，不須使用特定的機器讀取。
- 閱卷系統可以將特定格式中的資料讀取出來，並與答案做比較，輸出讀取到所寫的答案及評分後的分數。
- 閱卷系統提供許多自定義設定，在系統不穩定時可以嘗試微調設定檔，保證程式正常運作，以免在不同場景時出現問題而無法評分。
- 閱卷系統支援多種圖片格式，方便在使用掃描後格式不同造成的轉檔麻煩。
- 閱卷系統提供一鍵執行功能，把所要的圖片放入 *img* 資料夾、安裝好指定版本的python後，在執行`一鍵執行.bat`檔案，即可快速進行評分。

## 快速開始

1. 下載並**安裝python**(版本**大於3.11**或使用 *python* 資料夾中提供的安裝檔)。
2. 將**圖片放入 *img* 資料夾**中，並將**答案圖片重新命名為設定檔(`config.yaml`)中指定的名稱**，預設為`ans`(副檔名除非有指定，否則預設只要是支援格式都可以)。
3. 檢查傳入圖片格式，在設定檔(`config.yaml`)中有寫出可支援格式，預設為png、jpg、、jpeg、webp，如確認該格式可以支援可以自行添加到設定檔(`config.yaml`)中。
4. **執行`一鍵執行.bat`檔案**，即可開始進行評分，評分結果會放入輸出檔中(類似於紀錄檔，正式的結果檔案會在評分的資料夾中 *img*)，預設為`ans.csv`，並請注意他**只會添加，不會覆蓋**，所以請確認檔案中是否有遺留資料，或是直接將檔案移除後再執行；如果執行`一鍵執行.bat`時出現警示不放心，也可以手動執行以下指令來運行。
```bash
pip install -r requirements.txt
python main.py
```
5. 完成後，即可在輸出檔中查看評分結果。

## 相關檔案說明

- `requirements.txt`：python套件需求檔，用於安裝所需的套件。
- `config.yaml`：設定檔，用於設定閱卷系統的各項設定，包含圖片路徑、答案名稱、答案路徑、輸出檔名、可支援格式、分數等。注意無此檔案將導致程式無法執行。
- `csvreadwrite.py`：用作於讀寫csv檔案，讀取csv不是使用外部套件，且格是因為資料含有逗號，會與正常格式衝突，所以使用不同分隔符號。


