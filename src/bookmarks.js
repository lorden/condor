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
