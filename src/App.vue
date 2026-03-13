<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <!-- Top Search Bar -->
    <header class="sticky top-0 z-10 bg-white shadow px-4 py-3">
      <input v-model="searchQuery" @input="onSearch" type="text" placeholder="Search..." class="border rounded px-4 py-2 w-full max-w-2xl mx-auto block" autofocus />
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col items-center py-8 px-4">
      <!-- Bookmarks Panel -->
      <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold">Bookmarks</h2>
          <button v-if="!showAddForm" @click="showAddForm = true" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm">+ Add</button>
        </div>
        <!-- Add Bookmark Form -->
        <form v-if="showAddForm" @submit.prevent="submitBookmark" class="flex flex-col gap-2 mb-4">
          <div class="flex gap-2">
            <input v-model="newBookmarkUrl" type="text" placeholder="URL" class="border rounded px-2 py-1 flex-1" required />
            <input v-model="newBookmarkTitle" type="text" placeholder="Title (optional)" class="border rounded px-2 py-1 flex-1" />
          </div>
          <div class="flex gap-2">
            <input v-model="newBookmarkTags" type="text" placeholder="Tags (space-separated)" class="border rounded px-2 py-1 flex-1" />
            <button type="submit" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Save</button>
            <button type="button" @click="showAddForm = false" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">Cancel</button>
          </div>
        </form>
        <div v-if="bookmarksLoading" class="text-gray-500">Loading bookmarks...</div>
        <div v-else-if="bookmarksError" class="text-red-500">{{ bookmarksError }}</div>
        <ul v-else class="divide-y">
          <li v-for="bm in bookmarks" :key="bm.id" class="py-2 flex items-center justify-between">
            <div class="flex items-center">
              <img v-if="bm.favicon_url" :src="bm.favicon_url" alt="" class="w-4 h-4 mr-2 flex-shrink-0" @error="onFaviconError" />
              <a :href="bm.url" @click="onBookmarkClick(bm.id)" class="text-blue-600 hover:underline">{{ bm.title || bm.url }}</a>
              <span v-if="bm.tags && bm.tags.length" class="ml-2">
                <span v-for="tag in bm.tags" :key="tag.id" class="inline-block bg-gray-200 text-gray-700 text-xs px-2 py-0.5 rounded mr-1">{{ tag.name }}</span>
              </span>
            </div>
            <span class="text-gray-400 text-xs ml-2">{{ bm.click_count || 0 }} clicks</span>
          </li>
          <li v-if="bookmarks.length === 0" class="text-gray-400">No bookmarks yet.</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script>
import { listBookmarks, addBookmark, recordClick } from './bookmarks.js';
export default {
  data() {
    return {
      bookmarks: [],
      bookmarksLoading: true,
      bookmarksError: null,
      newBookmarkUrl: '',
      newBookmarkTitle: '',
      newBookmarkTags: '',
      searchQuery: '',
      showAddForm: false,
    };
  },
  methods: {
    async fetchBookmarks() {
      this.bookmarksLoading = true;
      this.bookmarksError = null;
      try {
        this.bookmarks = await listBookmarks(this.searchQuery);
      } catch (e) {
        this.bookmarksError = e.message || 'Failed to load bookmarks.';
      } finally {
        this.bookmarksLoading = false;
      }
    },
    onSearch() {
      this.fetchBookmarks();
    },
    onFaviconError(e) {
      e.target.style.display = 'none';
    },
    async onBookmarkClick(bookmarkId) {
      try {
        await recordClick(bookmarkId);
      } catch (e) {
        // Silently fail, don't block navigation
      }
    },
    async submitBookmark() {
      if (!this.newBookmarkUrl) return;
      try {
        await addBookmark(this.newBookmarkUrl, this.newBookmarkTitle || null, this.newBookmarkTags || null);
        this.newBookmarkUrl = '';
        this.newBookmarkTitle = '';
        this.newBookmarkTags = '';
        this.showAddForm = false;
        await this.fetchBookmarks();
      } catch (e) {
        this.bookmarksError = e.message || 'Failed to add bookmark.';
      }
    },
  },
  mounted() {
    this.fetchBookmarks();

    // Check for prepopulated bookmark from context menu
    const params = new URLSearchParams(window.location.search);
    if (params.get('addBookmark') === '1') {
      this.newBookmarkUrl = params.get('url') || '';
      this.newBookmarkTitle = params.get('title') || '';
      this.showAddForm = true;
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  },
};
</script>
