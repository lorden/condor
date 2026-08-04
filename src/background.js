// Background service worker for context menu and bookmarks

const MEETING_SUGGESTIONS_KEY = 'meetingSuggestionsV1';
const MAX_SUGGESTIONS_PER_MEETING = 75;
const DEDUPE_CAPTURE_MS = 20000;
const lastCaptureByTab = new Map();
let meetingContexts = [];

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'add-bookmark',
    title: 'Add as bookmark (Alt+Shift+S)',
    contexts: ['page', 'link'],
  });
  chrome.contextMenus.create({
    id: 'add-to-workstream',
    title: 'Add to workstream',
    contexts: ['page', 'link'],
  });
});

// Helper function to open bookmark form
function openBookmarkForm(url, title) {
  const params = new URLSearchParams({
    addBookmark: '1',
    url: url,
    title: title,
  });
  chrome.tabs.create({ url: `chrome://newtab?${params.toString()}` });
}

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener(async (command) => {
  if (command !== 'add-bookmark' && command !== 'add-to-workstream') return;
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;
  if (command === 'add-bookmark') {
    openBookmarkForm(tab.url, tab.title || '');
  } else {
    openWorkstreamLinkPicker(tab.url, tab.title || '', tab.id);
  }
});

// Toolbar icon: works on pages that swallow the native context menu
// (Google Docs/Sheets render their own right-click menu).
chrome.action.onClicked.addListener((tab) => {
  if (tab?.url) openWorkstreamLinkPicker(tab.url, tab.title || '', tab.id);
});

// Open the new-tab app on the workstream link picker, remembering the
// originating tab so the picker can return to it after saving.
function openWorkstreamLinkPicker(url, title, returnTabId) {
  const params = new URLSearchParams({
    addToWorkstream: '1',
    url: url,
    title: title,
  });
  if (returnTabId !== undefined) params.set('returnTabId', String(returnTabId));
  chrome.tabs.create({ url: `chrome://newtab?${params.toString()}` });
}

// Handle context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'add-bookmark' && info.menuItemId !== 'add-to-workstream') return;

  let url, title;
  if (info.linkUrl) {
    // Right-clicked on a link
    url = info.linkUrl;
    title = info.selectionText || '';
  } else {
    // Right-clicked on page
    url = tab.url;
    title = tab.title || '';
  }

  if (info.menuItemId === 'add-bookmark') {
    openBookmarkForm(url, title);
  } else {
    openWorkstreamLinkPicker(url, title, tab?.id);
  }
});

function parseTimeMs(value) {
  if (!value) return null;
  const parsed = new Date(value).getTime();
  return Number.isNaN(parsed) ? null : parsed;
}

function normalizeTrackableUrl(raw) {
  const value = String(raw || '').trim();
  if (!value) return null;
  if (value.startsWith('chrome://') || value.startsWith('chrome-extension://') || value.startsWith('about:') || value.startsWith('edge://') || value.startsWith('devtools://')) {
    return null;
  }

  let candidate = value;
  if (!/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(candidate)) candidate = `https://${candidate}`;

  try {
    const parsed = new URL(candidate);
    if (!['http:', 'https:'].includes(parsed.protocol)) return null;
    parsed.hash = '';
    return parsed.toString();
  } catch {
    return null;
  }
}

function getActiveMeetingContext(now = Date.now()) {
  const active = meetingContexts.find((context) => context.startMs <= now && now <= context.endMs);
  return active || null;
}

function storageGet(key) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(key, (result) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      resolve(result);
    });
  });
}

function storageSet(value) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.set(value, () => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      resolve();
    });
  });
}

function mapSuggestionsToList(suggestionsMap = {}) {
  return Object.values(suggestionsMap)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      if ((b.count || 0) !== (a.count || 0)) return (b.count || 0) - (a.count || 0);
      return (b.lastSeen || 0) - (a.lastSeen || 0);
    });
}

async function recordTabForActiveMeeting(tab) {
  const activeMeeting = getActiveMeetingContext();
  if (!activeMeeting) return;

  const normalizedUrl = normalizeTrackableUrl(tab?.url);
  if (!normalizedUrl) return;

  const dedupeKey = `${tab?.id || 'unknown'}:${activeMeeting.mappingKey}`;
  const previous = lastCaptureByTab.get(dedupeKey);
  const now = Date.now();
  if (previous && previous.url === normalizedUrl && now - previous.at < DEDUPE_CAPTURE_MS) return;
  lastCaptureByTab.set(dedupeKey, { url: normalizedUrl, at: now });

  const store = await storageGet(MEETING_SUGGESTIONS_KEY);
  const allSuggestions = store[MEETING_SUGGESTIONS_KEY] || {};
  const byMeeting = allSuggestions[activeMeeting.mappingKey] || {};
  const existing = byMeeting[normalizedUrl] || {
    url: normalizedUrl,
    title: tab?.title || normalizedUrl,
    count: 0,
    lastSeen: 0,
    score: 0,
  };

  const updated = {
    ...existing,
    title: tab?.title || existing.title,
    count: (existing.count || 0) + 1,
    lastSeen: now,
    score: (existing.score || 0) + 1,
  };
  byMeeting[normalizedUrl] = updated;

  const trimmed = mapSuggestionsToList(byMeeting).slice(0, MAX_SUGGESTIONS_PER_MEETING);
  const trimmedMap = {};
  trimmed.forEach((entry) => {
    trimmedMap[entry.url] = entry;
  });
  allSuggestions[activeMeeting.mappingKey] = trimmedMap;

  await storageSet({ [MEETING_SUGGESTIONS_KEY]: allSuggestions });
}

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  try {
    const tab = await chrome.tabs.get(tabId);
    await recordTabForActiveMeeting(tab);
  } catch (error) {
    console.warn('Failed to capture activated tab', error);
  }
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!tab?.active) return;
  if (!changeInfo.url && changeInfo.status !== 'complete') return;
  try {
    await recordTabForActiveMeeting(tab);
  } catch (error) {
    console.warn('Failed to capture updated tab', error);
  }
});

chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) return;
  try {
    const [tab] = await chrome.tabs.query({ active: true, windowId });
    if (tab) await recordTabForActiveMeeting(tab);
  } catch (error) {
    console.warn('Failed to capture focused window tab', error);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'update-meeting-contexts') {
    const contexts = Array.isArray(message.contexts) ? message.contexts : [];
    meetingContexts = contexts
      .map((context) => {
        const mappingKey = String(context?.mappingKey || '').trim();
        const startMs = parseTimeMs(context?.startTime);
        const endMs = parseTimeMs(context?.endTime);
        if (!mappingKey || startMs === null || endMs === null || endMs <= startMs) return null;
        return {
          mappingKey,
          startMs,
          endMs,
          summary: String(context?.summary || ''),
        };
      })
      .filter(Boolean);
    sendResponse({ ok: true, trackedContexts: meetingContexts.length });
    return;
  }

  if (message?.type === 'get-meeting-suggestions') {
    (async () => {
      const mappingKey = String(message?.mappingKey || '').trim();
      if (!mappingKey) {
        sendResponse({ ok: true, suggestions: [] });
        return;
      }
      const limit = Math.max(1, Math.min(20, Number(message?.limit) || 6));
      const store = await storageGet(MEETING_SUGGESTIONS_KEY);
      const allSuggestions = store[MEETING_SUGGESTIONS_KEY] || {};
      const byMeeting = allSuggestions[mappingKey] || {};
      const suggestions = mapSuggestionsToList(byMeeting).slice(0, limit);
      sendResponse({ ok: true, suggestions });
    })().catch((error) => {
      sendResponse({ ok: false, error: error.message || 'Failed to get suggestions.' });
    });
    return true;
  }

  if (message?.type === 'close-and-return') {
    (async () => {
      const returnTabId = Number(message.returnTabId);
      if (Number.isFinite(returnTabId)) {
        try {
          const tab = await chrome.tabs.update(returnTabId, { active: true });
          if (tab?.windowId !== undefined) {
            await chrome.windows.update(tab.windowId, { focused: true });
          }
        } catch {
          // The originating tab was closed in the meantime — nothing to focus.
        }
      }
      if (sender?.tab?.id !== undefined) chrome.tabs.remove(sender.tab.id);
      sendResponse({ ok: true });
    })().catch((error) => {
      sendResponse({ ok: false, error: error.message || 'Failed to close and return.' });
    });
    return true;
  }

  if (message?.type !== 'open-event-bookmarks') return;

  (async () => {
    const normalizeUrl = (raw) => {
      const value = String(raw || '').trim();
      if (!value) return null;
      if (/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(value)) return value;
      return `https://${value}`;
    };

    const links = Array.isArray(message.links) ? message.links.map(normalizeUrl).filter(Boolean) : [];
    if (links.length === 0) {
      sendResponse({ ok: false, error: 'No links to open.' });
      return;
    }

    const createTab = (url, active, windowId, index) => new Promise((resolve, reject) => {
      const createOptions = { url, active, windowId, index };
      chrome.tabs.create(createOptions, (tab) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        resolve(tab);
      });
    });

    const openedTabIds = [];
    const openErrors = [];
    let newWindowId;

    try {
      const firstTab = await new Promise((resolve, reject) => {
        chrome.windows.create({ url: links[0], focused: true }, (newWindow) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
            return;
          }
          resolve(newWindow?.tabs?.[0]);
        });
      });
      if (firstTab?.id !== undefined) openedTabIds.push(firstTab.id);
      newWindowId = firstTab?.windowId;
    } catch (error) {
      openErrors.push(error.message || 'Failed to open first bookmark tab');
    }

    if (typeof newWindowId === 'number') {
      for (let i = 1; i < links.length; i += 1) {
        try {
          const tab = await createTab(links[i], false, newWindowId, i);
          if (tab?.id !== undefined) openedTabIds.push(tab.id);
        } catch (error) {
          openErrors.push(error.message || 'Failed to open a bookmark tab');
        }
      }
    }

    if (openedTabIds.length === 0) {
      sendResponse({ ok: false, error: openErrors[0] || 'Failed to open meeting tabs.' });
      return;
    }

    const openedAll = openErrors.length === 0 && openedTabIds.length === links.length;
    if (openedAll && sender?.tab?.id !== undefined) {
      chrome.tabs.remove(sender.tab.id);
    }

    sendResponse({
      ok: true,
      openedCount: openedTabIds.length,
      failedCount: openErrors.length,
      closedSourceTab: openedAll,
      warning: openErrors.length ? openErrors[0] : undefined,
    });
  })().catch((error) => {
    sendResponse({ ok: false, error: error.message || 'Failed to open meeting tabs.' });
  });

  return true;
});
