// StudyHelper — Scriptable Widget
// Shows the next upcoming lesson on your iOS home screen.
// Uses /today endpoint for full offline support with local time calculation.
//
// Setup:
// 1. Install Scriptable from the App Store
// 2. Open this file in Scriptable
// 3. On first run, enter your API key (from StudyHelper Settings > Widgets)
// 4. Add a Scriptable widget to your home screen, select this script

const KEYCHAIN_KEY = "studyhelper_api_key";
const BASE_URL = "https://studyhelper1.ru/api/v1/widget/today";
const CACHE_FILE = "studyhelper_cache.json";

const WEEKDAYS_SHORT = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
const MONTHS_SHORT = [
  "янв", "фев", "мар", "апр", "май", "июн",
  "июл", "авг", "сен", "окт", "ноя", "дек",
];

async function getApiKey() {
  if (Keychain.contains(KEYCHAIN_KEY)) {
    return Keychain.get(KEYCHAIN_KEY);
  }

  const alert = new Alert();
  alert.title = "StudyHelper";
  alert.message = "Введите API ключ из настроек StudyHelper (Настройки \u2192 Виджеты)";
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
      const data = JSON.parse(raw);
      // Expire cache after 24 hours
      if (data.cached_at) {
        const cacheAge = Date.now() - new Date(data.cached_at).getTime();
        if (cacheAge > 24 * 60 * 60 * 1000) return null;
      }
      return data;
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

async function fetchTodaySchedule(apiKey) {
  const url = `${BASE_URL}?api_key=${encodeURIComponent(apiKey)}`;
  const req = new Request(url);
  req.timeoutInterval = 10;

  try {
    const data = await req.loadJSON();
    saveCache(data);
    return data;
  } catch {
    // Offline fallback
    return loadCache();
  }
}

function formatDateShort(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  const wd = WEEKDAYS_SHORT[d.getDay()];
  const day = d.getDate();
  const mon = MONTHS_SHORT[d.getMonth()];
  return `${wd}, ${day} ${mon}`;
}

function parseTime(timeStr) {
  const [h, m] = timeStr.split(":").map(Number);
  return h * 60 + m;
}

function findNextLesson(data) {
  if (!data) return { no_more_lessons: true };

  const now = new Date();
  const todayStr =
    now.getFullYear() +
    "-" +
    String(now.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(now.getDate()).padStart(2, "0");

  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  // If cached date is today, look for the next upcoming lesson
  if (data.date === todayStr && data.lessons && data.lessons.length > 0) {
    for (const lesson of data.lessons) {
      const lessonMinutes = parseTime(lesson.time_start);
      if (lessonMinutes > currentMinutes) {
        return {
          ...lesson,
          minutes_until: lessonMinutes - currentMinutes,
          is_today: true,
        };
      }
    }
  }

  // All today's lessons have passed or date doesn't match — show future lesson
  if (data.next_lesson_from_future) {
    return {
      ...data.next_lesson_from_future,
      is_today: false,
      future_date: data.next_lesson_date,
    };
  }

  return { no_more_lessons: true };
}

function formatMinutesUntil(minutes) {
  if (minutes <= 0) return "Сейчас";
  if (minutes < 60) {
    return `через ${minutes} мин`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `через ${hours} ч ${mins} мин` : `через ${hours} ч`;
}

function createWidget(data) {
  const widget = new ListWidget();
  widget.backgroundColor = new Color("#1a1a2e");

  const lesson = findNextLesson(data);

  if (!lesson || !data) {
    const errText = widget.addText("Нет данных");
    errText.textColor = Color.gray();
    errText.font = Font.mediumSystemFont(14);
    return widget;
  }

  if (lesson.no_more_lessons) {
    const title = widget.addText("StudyHelper");
    title.textColor = new Color("#8b8ba7");
    title.font = Font.boldSystemFont(12);

    widget.addSpacer(8);

    const noLessons = widget.addText("Нет пар");
    noLessons.textColor = Color.white();
    noLessons.font = Font.boldSystemFont(18);

    widget.addSpacer(4);

    const subText = widget.addText("в ближайшую неделю");
    subText.textColor = new Color("#8b8ba7");
    subText.font = Font.regularSystemFont(12);

    return widget;
  }

  // Header
  const header = widget.addText("Следующая пара");
  header.textColor = new Color("#8b8ba7");
  header.font = Font.boldSystemFont(11);

  widget.addSpacer(6);

  // Subject
  const subject = widget.addText(lesson.subject || "\u2014");
  subject.textColor = Color.white();
  subject.font = Font.boldSystemFont(16);
  subject.lineLimit = 2;

  widget.addSpacer(4);

  // Time
  const timeStr = `${lesson.time_start} \u2013 ${lesson.time_end}`;
  const timeText = widget.addText(timeStr);
  timeText.textColor = new Color("#6c9eff");
  timeText.font = Font.semiboldSystemFont(14);

  widget.addSpacer(3);

  // Location
  if (lesson.location) {
    const loc = widget.addText(lesson.location);
    loc.textColor = new Color("#c0c0d0");
    loc.font = Font.regularSystemFont(12);
    loc.lineLimit = 1;
  }

  // Teacher
  if (lesson.teacher) {
    const teacher = widget.addText(lesson.teacher);
    teacher.textColor = new Color("#c0c0d0");
    teacher.font = Font.regularSystemFont(11);
    teacher.lineLimit = 1;
  }

  widget.addSpacer(4);

  // Time info: minutes until (today) or date (future)
  if (lesson.is_today && lesson.minutes_until !== undefined) {
    const untilStr = formatMinutesUntil(lesson.minutes_until);
    const untilText = widget.addText(untilStr);
    untilText.textColor = new Color("#4ade80");
    untilText.font = Font.semiboldSystemFont(12);
  } else if (lesson.future_date) {
    const dateStr = formatDateShort(lesson.future_date);
    const dateText = widget.addText(dateStr);
    dateText.textColor = new Color("#fbbf24");
    dateText.font = Font.semiboldSystemFont(12);
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
  const data = await fetchTodaySchedule(apiKey);
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
