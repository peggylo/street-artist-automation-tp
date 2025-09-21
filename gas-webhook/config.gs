// 台北街頭藝人申請系統 - Google Apps Script 設定檔

// Google Sheets 設定
const GOOGLE_SHEETS_ID = "13MN6MWTI1KNwVZ29bqlwq7oJUAANeHRLS72XLDjOBq8";

// 申請時間窗口設定
const APPLICATION_PERIODS = {
  // 每月 1-3 日 17:00 前，申請當月下半月
  FIRST_PERIOD: {
    startDay: 1,
    endDay: 3,
    deadline: 17, // 17:00 (不包含)
    targetPeriod: "當月下半月"
  },
  
  // 每月 21-22 日 17:00 前，申請次月上半月  
  SECOND_PERIOD: {
    startDay: 21,
    endDay: 22,
    deadline: 17, // 17:00 (不包含)
    targetPeriod: "次月上半月"
  }
};

// LINE Bot 觸發關鍵字
const TRIGGER_KEYWORDS = ["申請", "我要申請", "我想申請"];

// GitHub Repository 設定
const GITHUB_OWNER = "peggylo";
const GITHUB_REPO = "street-artist-automation-tp";

// 時區設定
const TIMEZONE = "Asia/Taipei";
