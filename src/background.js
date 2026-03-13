// Background service worker for context menu and bookmarks

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'add-bookmark',
    title: 'Add as bookmark (Alt+Shift+S)',
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

// Handle keyboard shortcut
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'add-bookmark') {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      openBookmarkForm(tab.url, tab.title || '');
    }
  }
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'add-bookmark') {
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

    openBookmarkForm(url, title);
  }
});
