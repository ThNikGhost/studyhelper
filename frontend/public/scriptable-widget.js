// StudyHelper — Scriptable Widget
// Shows the next upcoming lesson on your iOS home screen.
//
// Setup:
// 1. Install Scriptable from the App Store
// 2. Open this file in Scriptable
// 3. On first run, enter your API key (from StudyHelper Settings > Widgets)
// 4. Add a Scriptable widget to your home screen, select this script

const KEYCHAIN_KEY = "studyhelper_api_key";
const BASE_URL = "https://studyhelper1.ru/api/v1/widget/next-lesson";
const CACHE_FILE = "studyhelper_cache.json";

async function getApiKey() {
  if (Keychain.contains(KEYCHAIN_KEY)) {
    return Keychain.get(KEYCHAIN_KEY);
  }

  const alert = new Alert();
  alert.title = "StudyHelper";
  alert.message = "Введите API ключ из настроек StudyHelper (Настройки → Виджеты)";
  alert.addTextField("API ключ");
  alert.addAction("Сохранить");
  alert.addCancelAction("Отмена");

  const idx = await alert.presentAlert();
  if (idx === -1) return null;

  const key = alert.textFieldValue(0).trim();
  if (!key) return null;

  Keychain.set(KEYCHAIN_KEY, key);
  return key;
}

function getCachePath() {
  const fm = FileManager.local();
  const dir = fm.documentsDirectory();
  return fm.joinPath(dir, CACHE_FILE);
}

function loadCache() {
  const fm = FileManager.local();
  const path = getCachePath();
  if (fm.fileExists(path)) {
    try {
      const raw = fm.readString(path);
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }
  return null;
}

function saveCache(data) {
  const fm = FileManager.local();
  const path = getCachePath();
  fm.writeString(path, JSON.stringify(data));
}

async function fetchNextLesson(apiKey) {
  const url = `${BASE_URL}?api_key=${encodeURIComponent(apiKey)}`;
  const req = new Request(url);
  req.timeoutInterval = 10;

  try {
    const data = await req.loadJSON();
    saveCache(data);
    return data;
  } catch {
    // Offline fallback
    const cached = loadCache();
    return cached;
  }
}

function createWidget(data) {
  const widget = new ListWidget();
  widget.backgroundColor = new Color("#1a1a2e");

  if (!data) {
    const errText = widget.addText("Нет данных");
    errText.textColor = Color.gray();
    errText.font = Font.mediumSystemFont(14);
    return widget;
  }

  if (data.no_more_lessons) {
    const title = widget.addText("StudyHelper");
    title.textColor = new Color("#8b8ba7");
    title.font = Font.boldSystemFont(12);

    widget.addSpacer(8);

    const noLessons = widget.addText("Нет занятий");
    noLessons.textColor = Color.white();
    noLessons.font = Font.boldSystemFont(18);

    widget.addSpacer(4);

    const subText = widget.addText("в ближайшие 7 дней");
    subText.textColor = new Color("#8b8ba7");
    subText.font = Font.regularSystemFont(12);

    return widget;
  }

  // Header
  const header = widget.addText("Следующее занятие");
  header.textColor = new Color("#8b8ba7");
  header.font = Font.boldSystemFont(11);

  widget.addSpacer(6);

  // Subject
  const subject = widget.addText(data.subject || "—");
  subject.textColor = Color.white();
  subject.font = Font.boldSystemFont(16);
  subject.lineLimit = 2;

  widget.addSpacer(4);

  // Time
  const timeStr = `${data.time_start} – ${data.time_end}`;
  const timeText = widget.addText(timeStr);
  timeText.textColor = new Color("#6c9eff");
  timeText.font = Font.semiboldSystemFont(14);

  widget.addSpacer(3);

  // Location
  if (data.location) {
    const loc = widget.addText(data.location);
    loc.textColor = new Color("#c0c0d0");
    loc.font = Font.regularSystemFont(12);
    loc.lineLimit = 1;
  }

  // Teacher
  if (data.teacher) {
    const teacher = widget.addText(data.teacher);
    teacher.textColor = new Color("#c0c0d0");
    teacher.font = Font.regularSystemFont(11);
    teacher.lineLimit = 1;
  }

  widget.addSpacer(4);

  // Minutes until
  if (data.minutes_until !== null && data.minutes_until !== undefined) {
    let untilStr;
    if (data.minutes_until < 60) {
      untilStr = `через ${data.minutes_until} мин`;
    } else {
      const hours = Math.floor(data.minutes_until / 60);
      const mins = data.minutes_until % 60;
      untilStr = mins > 0 ? `через ${hours}ч ${mins}мин` : `через ${hours}ч`;
    }
    const untilText = widget.addText(untilStr);
    untilText.textColor = new Color("#4ade80");
    untilText.font = Font.semiboldSystemFont(12);
  }

  return widget;
}

// Main
const apiKey = await getApiKey();
if (!apiKey) {
  const w = new ListWidget();
  const t = w.addText("API ключ не задан");
  t.textColor = Color.red();
  Script.setWidget(w);
  Script.complete();
} else {
  const data = await fetchNextLesson(apiKey);
  const widget = createWidget(data);

  // Refresh every 15 minutes
  const nextRefresh = new Date(Date.now() + 15 * 60 * 1000);
  widget.refreshAfterDate = nextRefresh;

  if (config.runsInWidget) {
    Script.setWidget(widget);
  } else {
    widget.presentMedium();
  }
  Script.complete();
}
