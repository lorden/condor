const BACKEND_URL = 'http://localhost:8000';

export async function listBookmarks(query) {
  const url = query ? `${BACKEND_URL}/bookmarks?q=${encodeURIComponent(query)}` : `${BACKEND_URL}/bookmarks`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch bookmarks');
  return res.json();
}

export async function addBookmark(url, title, tags) {
  const res = await fetch(`${BACKEND_URL}/bookmarks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, title, tags }),
  });
  if (!res.ok) throw new Error('Failed to add bookmark');
  return res.json();
}

export async function recordClick(bookmarkId) {
  const res = await fetch(`${BACKEND_URL}/bookmarks/${bookmarkId}/click`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to record click');
  return res.json();
}

function getGoogleAccessToken() {
  if (!chrome?.identity?.getAuthToken) {
    throw new Error('Chrome identity API is unavailable. Check extension permissions.');
  }

  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (!token) {
        reject(new Error('No Google OAuth token was returned.'));
        return;
      }
      resolve(token);
    });
  });
}

async function authorizedRequest(path, options = {}) {
  const token = await getGoogleAccessToken();
  const headers = {
    ...(options.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  const res = await fetch(`${BACKEND_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Request failed');
  }
  return res.json();
}

export async function listTodayEvents() {
  return authorizedRequest('/calendar/events/today');
}

export async function linkBookmarkToEvent(eventId, bookmarkId, eventTitle, eventStart) {
  return authorizedRequest(`/calendar/events/${encodeURIComponent(eventId)}/bookmarks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      bookmark_id: bookmarkId,
      event_title: eventTitle,
      event_start: eventStart,
    }),
  });
}

export async function unlinkBookmarkFromEvent(eventId, bookmarkId) {
  return authorizedRequest(`/calendar/events/${encodeURIComponent(eventId)}/bookmarks/${bookmarkId}`, {
    method: 'DELETE',
  });
}

async function fetchJira(path, { refresh = false } = {}) {
  const params = new URLSearchParams();
  if (refresh) params.set('refresh', '1');
  const qs = params.toString();
  const res = await fetch(`${BACKEND_URL}${path}${qs ? `?${qs}` : ''}`);
  if (!res.ok) {
    const raw = await res.text();
    let detail = raw;
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed.detail === 'string') detail = parsed.detail;
      else if (parsed) detail = JSON.stringify(parsed, null, 2);
    } catch {
      // raw text is not JSON — use as-is
    }
    throw new Error(`HTTP ${res.status} ${res.statusText}\n${detail}`);
  }
  return res.json();
}

export function listJiraUpdates(opts) {
  return fetchJira('/jira/updates', opts);
}

export function listJiraReleases(opts) {
  return fetchJira('/jira/releases', opts);
}

export function listGitHubPullRequests(opts) {
  return fetchJira('/github/pull-requests', opts);
}

export async function getSettings() {
  const res = await fetch(`${BACKEND_URL}/settings`);
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json();
}

export async function updateSettings(payload) {
  const res = await fetch(`${BACKEND_URL}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const raw = await res.text();
    throw new Error(`HTTP ${res.status} ${res.statusText}\n${raw}`);
  }
  return res.json();
}
