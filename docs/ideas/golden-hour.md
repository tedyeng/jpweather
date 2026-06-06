# Golden & Blue Hour 功能設計

## 1. Problem Statement (問題陳述)
How might we provide photographers and outdoor enthusiasts with exact start and end times for Golden Hour and Blue Hour combined with real-time cloud cover and weather conditions to help them plan their photoshoots effectively?

## 2. Recommended Direction (推薦方向)
我們將新增一個獨立子指令 `uv run jpweather golden "地點"`（並支援 `--week` 預報一週，以及 `--mobile` 緊湊排版）。
此指令會：
1. 使用現有的 Geocoding / GPS 解析機制取得地點的經緯度與時區。
2. 在本地以 **SunCalc 數學模型** 計算出該日期精準的「日出/日落、藍調時刻、黃金時刻」起訖時間。
3. 串接 **Open-Meteo Weather API**，獲取該時段對應的「每小時雲量 (Cloud Cover)」與「降水機率 (Precipitation Probability)」。
4. 根據雲量和降雨評估當下的拍照條件，提供一個直觀的 **「攝影推薦指數 (Photography Rating)」**（以 ⭐ 星等呈現）與簡短建議。

## 3. Key Assumptions to Validate (關鍵假設與驗證方法)
* **太陽高度角計算的準確度**：本地 Python 實現的 SunCalc 算法與標準天文觀測資料（或 JS `suncalc` 庫）對齊，時間誤差控制在 1-2 分鐘內。
  * *驗證方法*：在單元測試中，對比東京、臺北、倫敦等不同緯度城市在特定日期的日出日落與黃金時刻時間。
* **時區轉換的正確性**：不論查詢全球哪一個城市，回報的起訖時間均為該地當地的 Local Time。
  * *驗證方法*：使用 `pytz` 或 Python 3.9+ 內建的 `zoneinfo`，配合 Open-Meteo 回傳的時區字串（如 `Europe/London`）進行轉換測試。
* **天氣與時間段的對齊**：攝影指數計算時，能正確對齊黃金時刻所在的 hourly 區間，而非隨機取一整天的平均雲量。
  * *驗證方法*：撰寫 mock 測試，確保當黃金時刻在 18:00 ~ 18:40 時，系統讀取的是 18:00 和 19:00 的雲量數據。

## 4. MVP Scope (首裝版範圍)
### In Scope (納入範圍)
* **子指令 `golden`**：支援單日查詢（預設今天）與一週查詢（`--week`）。
* **GPS / 地名雙引擎定位**：完美繼承現有 CJK 地名補全、DMS/十進位 GPS 座標解析，以及 OSM 反查。
* **光影時刻計算**：
  * **藍調時刻 (Blue Hour)**: 太陽角度在 $-6^\circ$ 至 $-4^\circ$ 之間。
  * **黃金時刻 (Golden Hour)**: 太陽角度在 $-4^\circ$ 至 $6^\circ$ 之間。
* **攝影推薦指數**：
  * 結合 Open-Meteo 每小時雲量、降水機率、天氣狀況，計算綜合評分。
  * 評分邏輯範例：
    * 降雨機率 > 50% 或雲量 > 90% ➡️ 1~2 顆星（光線被阻擋或下雨）。
    * 雲量在 20% ~ 60% 之間 ➡️ 5 顆星（極佳，有機會出現美麗 of 火燒雲/暮光絲狀雲）。
    * 雲量 < 10% ➡️ 4 顆星（晴空無雲，光線柔和但天空可能略顯單調）。
* **Rich 終端機排版**：採用金色 (yellow/orange) 與藍色 (blue/cyan) 的配色，排版整齊，並支援 `--mobile`（38欄寬）排版。

### Out of Scope (暫不納入)
* **太陽方位角 (Azimuth) 羅盤圖**：暫不顯示太陽在天空中的具體方位度數與羅盤指向（未來可作為進階功能）。
* **自訂光線高度角**：暫不支持使用者自訂高度角範圍，統一使用標準的攝影定義。

## 5. Not Doing (暫不實作原因)
* **串接專門的付費天文 API**：因為 Open-Meteo 已經有免費的地理編碼和天氣，配合本地 SunCalc 算法即可達到相同甚至更快的精確度，無需額外的 API Key 或付費服務。

## 6. Open Questions (待確認問題)
* 系統是否應自動在 `current` 即時天氣指令的輸出最下方，也順便塞入一行精簡的今日黃金時刻？（例如：`[今日光影] 藍調: 18:00-18:20 | 黃金: 18:20-19:10`）還是保持兩者完全獨立？
