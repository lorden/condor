<template>
  <div class="cds-shell">
    <nav class="cds-rail" aria-label="Primary">
      <button
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'home' }"
        @click="currentView = 'home'"
        title="Home"
        aria-label="Home"
      >
        <Home20 aria-hidden="true" />
      </button>
      <button
        v-if="featureFlags.jira"
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'swimlanes' }"
        @click="currentView = 'swimlanes'"
        title="Swimlanes by author"
        aria-label="Swimlanes by author"
      >
        <Task20 aria-hidden="true" />
      </button>
      <button
        v-if="featureFlags.jira"
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'releases' }"
        @click="currentView = 'releases'"
        title="Releases"
        aria-label="Releases"
      >
        <Calendar20 aria-hidden="true" />
      </button>
      <button
        v-if="featureFlags.github"
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'github' }"
        @click="currentView = 'github'"
        title="Pull requests"
        aria-label="Pull requests"
      >
        <PullRequest20 aria-hidden="true" />
        <span v-if="reviewRequestedNonDraftCount > 0" class="cds-rail__badge" aria-label="Reviews needed">
          {{ reviewRequestedNonDraftCount }}
        </span>
      </button>
      <button
        type="button"
        class="cds-rail__btn cds-rail__btn--bottom"
        :class="{ 'cds-rail__btn--active': currentView === 'settings' }"
        @click="currentView = 'settings'"
        title="Settings"
        aria-label="Settings"
      >
        <Settings20 aria-hidden="true" />
      </button>
      <button
        type="button"
        class="cds-rail__btn"
        @click="toggleTheme"
        :title="theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'"
        :aria-label="theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'"
      >
        <Asleep20 v-if="theme === 'light'" aria-hidden="true" />
        <Light20 v-else aria-hidden="true" />
      </button>
    </nav>

    <header class="cds-header">
      <input
        v-model="searchQuery"
        @input="onSearch"
        type="text"
        placeholder="Search bookmarks…"
        class="cds-input cds-input--lg cds-input--inverse-layer cds-search"
        autofocus
      />
    </header>

    <main class="cds-main">
      <div v-if="currentView === 'home'" class="cds-home">
        <!-- Full-width: GitHub Pull Requests (only when there's data or an error) -->
        <section
          v-if="featureFlags.github && (hasHomeGithubPullRequests || githubError)"
          class="cds-tile"
          :class="{ 'cds-tile--collapsed': homePrCollapsed }"
        >
          <div class="cds-tile__head">
            <button
              type="button"
              class="cds-collapsible-trigger"
              :aria-expanded="!homePrCollapsed"
              @click="homePrCollapsed = !homePrCollapsed"
            >
              <ChevronDown20 class="cds-collapsible-trigger__chevron" :class="{ 'cds-collapsible-trigger__chevron--collapsed': homePrCollapsed }" aria-hidden="true" />
              <h2 class="cds-tile__title">Pull Requests</h2>
              <span class="cds-collapsible-trigger__counts cds-text-helper">
                <span>Needs review <span class="cds-pr-col__count">{{ homeReviewRequested.length }}</span></span>
                <span>Open <span class="cds-pr-col__count">{{ homeAuthored.length }}</span></span>
              </span>
            </button>
            <div v-if="!homePrCollapsed" class="cds-row cds-row--gap-3 cds-row--wrap">
              <span v-if="githubFetchedAt" class="cds-text-helper">{{ githubStatusLabel }}</span>
              <button @click="refreshGithubPullRequests" :disabled="githubLoading" class="cds-btn cds-btn--primary">Refresh</button>
            </div>
          </div>

          <template v-if="!homePrCollapsed">
            <pre v-if="githubError" class="cds-notification">{{ githubError }}</pre>
            <div v-else class="cds-pr-grid">
              <div v-if="homeReviewRequested.length" class="cds-pr-col">
                <h3 class="cds-pr-col__title">Needs my review <span class="cds-pr-col__count">{{ homeReviewRequested.length }}</span></h3>
                <ul class="cds-list cds-list--divided">
                  <li v-for="pr in homeReviewRequested" :key="pr.id" class="cds-stack-2">
                    <div class="cds-row cds-row--between cds-row--gap-3">
                      <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title cds-grow">
                        <span class="cds-text-truncate">{{ pr.title }}</span>
                      </a>
                    </div>
                    <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                      <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                      <span v-if="pr.author">by {{ pr.author }}</span>
                      <span v-if="pr.updated_at">· {{ formatRelative(pr.updated_at) }}</span>
                    </div>
                  </li>
                </ul>
              </div>
              <div v-if="homeAuthored.length" class="cds-pr-col">
                <h3 class="cds-pr-col__title">My open PRs <span class="cds-pr-col__count">{{ homeAuthored.length }}</span></h3>
                <ul class="cds-list cds-list--divided">
                  <li v-for="pr in homeAuthored" :key="pr.id" class="cds-stack-2">
                    <div class="cds-row cds-row--between cds-row--gap-3">
                      <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title cds-grow">
                        <span class="cds-text-truncate">{{ pr.title }}</span>
                      </a>
                    </div>
                    <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                      <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                      <span v-if="pr.updated_at">{{ formatRelative(pr.updated_at) }}</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </section>

        <div class="cds-grid" :class="{ 'cds-grid--single': !featureFlags.jira }">
        <!-- Left: Jira Updates -->
        <section v-if="featureFlags.jira" class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">Jira Updates</h2>
            <div class="cds-row cds-row--gap-3 cds-row--wrap">
              <select v-model="jiraAuthorFilter" class="cds-select" aria-label="Filter by author">
                <option value="">All authors</option>
                <option v-for="author in jiraAuthors" :key="author" :value="author">{{ author }}</option>
              </select>
              <select v-model="jiraTypeFilter" class="cds-select" aria-label="Filter by type">
                <option value="">All types</option>
                <option value="comment">Comment</option>
                <option value="status">Status</option>
              </select>
              <span v-if="jiraFetchedAt" class="cds-text-helper">{{ jiraStatusLabel }}</span>
              <button @click="refreshJiraUpdates" :disabled="jiraLoading" class="cds-btn cds-btn--primary">Refresh</button>
            </div>
          </div>

          <div v-if="jiraLoading && jiraUpdates.length === 0" class="cds-empty">Loading Jira updates…</div>
          <pre v-else-if="jiraError" class="cds-notification">{{ jiraError }}</pre>
          <ul v-else class="cds-list cds-list--divided">
            <li v-for="update in filteredJiraUpdates" :key="update.id" class="cds-stack-3">
              <div class="cds-row cds-row--between cds-row--gap-3">
                <div class="cds-row cds-row--gap-3 cds-grow">
                  <a :href="update.issue_url" target="_blank" rel="noreferrer" class="cds-issue-key cds-no-shrink">
                    {{ update.issue_key }}
                  </a>
                  <a
                    v-if="update.epic_key && update.epic_url"
                    :href="update.epic_url"
                    target="_blank"
                    rel="noreferrer"
                    :title="update.epic_key"
                    class="cds-tag cds-tag--purple cds-tag__label"
                  >
                    {{ update.epic_summary || update.epic_key }}
                  </a>
                  <span
                    v-else-if="update.epic_key"
                    :title="update.epic_key"
                    class="cds-tag cds-tag--purple cds-tag__label"
                  >
                    {{ update.epic_summary || update.epic_key }}
                  </span>
                </div>
                <span class="cds-tag cds-no-shrink" :class="update.type === 'comment' ? 'cds-tag--blue' : 'cds-tag--warmgray'">
                  {{ update.type === 'comment' ? 'Comment' : 'Status' }}
                </span>
              </div>
              <div class="cds-text-secondary">{{ update.issue_summary }}</div>
              <div v-if="update.type === 'status'" class="cds-text-secondary">
                <span class="cds-fw-500 cds-text-primary">{{ update.author }}</span>
                changed status:
                <span class="cds-text-secondary">{{ update.from_status || '—' }}</span>
                <span> → </span>
                <span class="cds-fw-500 cds-text-primary">{{ update.to_status || '—' }}</span>
              </div>
              <div v-else>
                <div class="cds-text-secondary">
                  <span class="cds-fw-500 cds-text-primary">{{ update.author }}</span> commented:
                </div>
                <div class="cds-text-secondary cds-text-pre cds-stack-2" style="margin-top: var(--cds-sp-02)">{{ truncate(update.body, 320) }}</div>
              </div>
              <div class="cds-text-helper">{{ formatRelative(update.timestamp) }}</div>
            </li>
            <li v-if="filteredJiraUpdates.length === 0 && !jiraLoading" class="cds-empty">
              {{ jiraUpdates.length === 0 ? 'No updates yet.' : 'No updates match the current filters.' }}
            </li>
          </ul>
        </section>

        <!-- Right column: Bookmarks (top, max 20) + Calendar (below) -->
        <div class="cds-col-stack">
          <!-- Bookmarks -->
          <section class="cds-tile">
            <div class="cds-tile__head">
              <h2 class="cds-tile__title">Bookmarks</h2>
              <button v-if="!showAddForm" @click="showAddForm = true" class="cds-btn cds-btn--primary">+ Add</button>
            </div>

            <form v-if="showAddForm" @submit.prevent="submitBookmark" class="cds-stack-3" style="margin-bottom: var(--cds-sp-05)">
              <div class="cds-form-row">
                <input v-model="newBookmarkUrl" type="text" placeholder="URL" class="cds-input" required />
                <input v-model="newBookmarkTitle" type="text" placeholder="Title (optional)" class="cds-input" />
              </div>
              <div class="cds-form-row">
                <input v-model="newBookmarkTags" type="text" placeholder="Tags (space-separated)" class="cds-input" />
                <button type="submit" class="cds-btn cds-btn--primary cds-btn--field">Save</button>
                <button type="button" @click="showAddForm = false" class="cds-btn cds-btn--tertiary cds-btn--field">Cancel</button>
              </div>
            </form>

            <div v-if="bookmarksLoading" class="cds-empty">Loading bookmarks…</div>
            <pre v-else-if="bookmarksError" class="cds-notification">{{ bookmarksError }}</pre>
            <ul v-else class="cds-list cds-list--divided">
              <li v-for="bm in displayBookmarks" :key="bm.id" class="cds-row cds-row--between cds-row--gap-3">
                <div class="cds-row cds-row--gap-3 cds-grow">
                  <img v-if="bm.favicon_url" :src="bm.favicon_url" alt="" width="16" height="16" class="cds-no-shrink" @error="onFaviconError" />
                  <a :href="bm.url" @click="onBookmarkClick(bm.id)" class="cds-text-truncate cds-grow">{{ bm.title || bm.url }}</a>
                  <span v-if="bm.tags && bm.tags.length" class="cds-row cds-row--gap-2 cds-row--wrap cds-no-shrink">
                    <span v-for="tag in bm.tags" :key="tag.id" class="cds-tag cds-tag--gray">{{ tag.name }}</span>
                  </span>
                </div>
                <span class="cds-text-helper cds-no-shrink">{{ bm.click_count || 0 }} clicks</span>
              </li>
              <li v-if="bookmarks.length === 0" class="cds-empty">No bookmarks yet.</li>
            </ul>
            <div v-if="bookmarks.length > BOOKMARK_LIMIT" class="cds-text-helper" style="margin-top: var(--cds-sp-04)">
              Showing top {{ BOOKMARK_LIMIT }} of {{ bookmarks.length }}.
            </div>
          </section>

          <!-- Calendar -->
          <section class="cds-tile">
            <div class="cds-tile__head">
              <h2 class="cds-tile__title">Today's Meetings</h2>
              <button @click="fetchTodayEvents" class="cds-btn cds-btn--primary">Refresh</button>
            </div>

            <div v-if="eventsLoading" class="cds-empty">Loading events…</div>
            <pre v-else-if="eventsError" class="cds-notification">{{ eventsError }}</pre>
            <ul v-else class="cds-list cds-list--divided">
              <li v-for="event in events" :key="event.id" class="cds-stack-3">
                <div class="cds-row cds-row--between cds-row--gap-3">
                  <div class="cds-fw-600 cds-text-primary">{{ event.summary }}</div>
                  <button
                    @click="openAllForEvent(event)"
                    :disabled="!event.bookmarks || event.bookmarks.length === 0"
                    class="cds-btn cds-btn--secondary"
                  >
                    Open All
                  </button>
                </div>
                <div class="cds-text-helper">{{ formatEventTime(event.start_time) }}</div>

                <div v-if="event.bookmarks && event.bookmarks.length" class="cds-row cds-row--gap-2 cds-row--wrap">
                  <span
                    v-for="linkedBookmark in event.bookmarks"
                    :key="`${event.id}-${linkedBookmark.id}`"
                    class="cds-tag cds-tag--gray"
                  >
                    <a
                      :href="linkedBookmark.url"
                      @click="onBookmarkClick(linkedBookmark.id)"
                      class="cds-tag__label"
                      style="color: inherit; max-width: 14rem"
                    >{{ linkedBookmark.title || linkedBookmark.url }}</a>
                    <button
                      @click.prevent="removeBookmarkFromEvent(event.mapping_key || event.id, linkedBookmark.id)"
                      class="cds-tag__close"
                      aria-label="Remove"
                      title="Remove"
                    >×</button>
                  </span>
                </div>

                <div v-if="eventSuggestions(event).length" class="cds-stack-2">
                  <div class="cds-row cds-row--between">
                    <span class="cds-text-helper cds-text-uppercase">Suggested from past meetings</span>
                    <button @click="openSuggestedForEvent(event)" class="cds-btn cds-btn--ghost">
                      Open Suggested
                    </button>
                  </div>
                  <div class="cds-row cds-row--gap-2 cds-row--wrap">
                    <a
                      v-for="suggestion in eventSuggestions(event)"
                      :key="`${meetingMappingKey(event)}-suggested-${suggestion.url}`"
                      :href="suggestion.url"
                      target="_blank"
                      rel="noreferrer"
                      class="cds-tag cds-tag--cyan"
                      style="max-width: 18rem"
                    >
                      <span class="cds-tag__label">{{ suggestion.title || suggestion.url }}</span>
                    </a>
                  </div>
                </div>

                <div class="cds-row cds-row--gap-3 cds-row--start">
                  <div class="cds-combobox">
                    <input
                      :value="bookmarkQueryByEvent[event.id] || ''"
                      @input="onEventBookmarkInput(event.id, $event.target.value)"
                      @focus="focusedEventId = event.id"
                      @blur="onEventBookmarkBlur(event.id)"
                      type="text"
                      placeholder="Type to find bookmark…"
                      class="cds-input cds-input--inverse-layer"
                    />
                    <ul
                      v-if="focusedEventId === event.id && filteredEventBookmarks(event).length"
                      class="cds-combobox__menu"
                    >
                      <li
                        v-for="bm in filteredEventBookmarks(event)"
                        :key="`event-${event.id}-bm-${bm.id}`"
                        @mousedown.prevent="selectEventBookmark(event.id, bm)"
                        class="cds-combobox__option"
                      >
                        {{ bookmarkLabel(bm) }}
                      </li>
                    </ul>
                  </div>
                  <button
                    @click="addBookmarkToEvent(event)"
                    :disabled="!selectedBookmarkByEvent[event.id]"
                    class="cds-btn cds-btn--primary cds-btn--field"
                  >
                    Add
                  </button>
                </div>
              </li>
              <li v-if="events.length === 0" class="cds-empty">No events today.</li>
            </ul>
          </section>
        </div>
        </div>
      </div>

      <section v-else-if="currentView === 'swimlanes'" class="cds-tile">
        <div class="cds-tile__head">
          <h2 class="cds-tile__title">Jira Swimlanes by author</h2>
          <div class="cds-row cds-row--gap-3 cds-row--wrap">
            <span v-if="jiraFetchedAt" class="cds-text-helper">{{ jiraStatusLabel }}</span>
            <button @click="refreshJiraUpdates" :disabled="jiraLoading" class="cds-btn cds-btn--primary">Refresh</button>
          </div>
        </div>

        <div v-if="jiraLoading && jiraUpdates.length === 0" class="cds-empty">Loading Jira updates…</div>
        <pre v-else-if="jiraError" class="cds-notification">{{ jiraError }}</pre>
        <div v-else-if="jiraSwimlanes.length === 0" class="cds-empty">No human-author updates yet.</div>
        <div v-else class="cds-swimlanes">
          <div v-for="lane in jiraSwimlanes" :key="lane.author" class="cds-swimlane">
            <header class="cds-swimlane__head">
              <span class="cds-swimlane__author" :title="lane.author">{{ lane.author }}</span>
              <span class="cds-swimlane__count">{{ lane.updates.length }}</span>
            </header>
            <div class="cds-swimlane__body">
              <article v-for="update in lane.updates" :key="update.id" class="cds-card">
                <div class="cds-row cds-row--between cds-row--gap-3">
                  <div class="cds-row cds-row--gap-3 cds-grow">
                    <a :href="update.issue_url" target="_blank" rel="noreferrer" class="cds-issue-key cds-no-shrink">{{ update.issue_key }}</a>
                    <a
                      v-if="update.epic_key && update.epic_url"
                      :href="update.epic_url"
                      target="_blank"
                      rel="noreferrer"
                      :title="update.epic_key"
                      class="cds-tag cds-tag--purple cds-tag__label"
                    >{{ update.epic_summary || update.epic_key }}</a>
                    <span
                      v-else-if="update.epic_key"
                      :title="update.epic_key"
                      class="cds-tag cds-tag--purple cds-tag__label"
                    >{{ update.epic_summary || update.epic_key }}</span>
                  </div>
                  <span class="cds-tag cds-no-shrink" :class="update.type === 'comment' ? 'cds-tag--blue' : 'cds-tag--warmgray'">
                    {{ update.type === 'comment' ? 'Comment' : 'Status' }}
                  </span>
                </div>
                <div class="cds-text-secondary">{{ update.issue_summary }}</div>
                <div v-if="update.type === 'status'" class="cds-text-secondary">
                  <span class="cds-text-secondary">{{ update.from_status || '—' }}</span>
                  <span> → </span>
                  <span class="cds-fw-500 cds-text-primary">{{ update.to_status || '—' }}</span>
                </div>
                <div v-else-if="update.body" class="cds-text-secondary cds-text-pre">{{ truncate(update.body, 220) }}</div>
                <div class="cds-text-helper">{{ formatRelative(update.timestamp) }}</div>
              </article>
            </div>
          </div>
        </div>
      </section>

      <div v-else-if="currentView === 'releases'" class="cds-grid">
        <!-- Left: release list -->
        <section class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">Releases</h2>
            <div class="cds-row cds-row--gap-3 cds-row--wrap">
              <span v-if="releasesFetchedAt" class="cds-text-helper">{{ releasesStatusLabel }}</span>
              <button @click="refreshReleases" :disabled="releasesLoading" class="cds-btn cds-btn--primary">Refresh</button>
            </div>
          </div>

          <div v-if="releasesLoading && releases.length === 0" class="cds-empty">Loading releases…</div>
          <pre v-else-if="releasesError" class="cds-notification">{{ releasesError }}</pre>
          <ul v-else-if="releases.length === 0" class="cds-list"><li class="cds-empty">No releases found.</li></ul>
          <ul v-else class="cds-list">
            <li
              v-for="release in sortedReleases"
              :key="release.id"
              class="cds-release"
              :class="{
                'cds-release--hovered': hoveredReleaseId === release.id,
                'cds-release--past': isPastRelease(release),
              }"
              @mouseenter="hoveredReleaseId = release.id"
              @mouseleave="hoveredReleaseId = null"
            >
              <div class="cds-row cds-row--between cds-row--gap-3">
                <a v-if="release.url" :href="release.url" target="_blank" rel="noreferrer" class="cds-fw-600 cds-text-primary">{{ release.name }}</a>
                <span v-else class="cds-fw-600 cds-text-primary">{{ release.name }}</span>
                <span class="cds-tag cds-no-shrink" :class="releaseStatusClass(release)">{{ releaseStatusLabel(release) }}</span>
              </div>
              <div v-if="release.release_date" class="cds-text-helper">
                Release date: {{ formatDate(release.release_date) }}<span v-if="relativeDays(release.release_date)"> · {{ relativeDays(release.release_date) }}</span><span v-if="release.overdue && !release.released"> · overdue</span>
              </div>
              <div v-if="release.start_date" class="cds-text-helper">
                Start: {{ formatDate(release.start_date) }}
              </div>
              <div v-if="release.description" class="cds-text-secondary cds-text-pre">{{ release.description }}</div>
            </li>
          </ul>
        </section>

        <!-- Right: calendar -->
        <section class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">{{ calendarTitle }}</h2>
            <div class="cds-calendar__nav">
              <button @click="prevMonth" class="cds-btn cds-btn--ghost" aria-label="Previous month">‹</button>
              <button @click="goToToday" class="cds-btn cds-btn--ghost">Today</button>
              <button @click="nextMonth" class="cds-btn cds-btn--ghost" aria-label="Next month">›</button>
            </div>
          </div>

          <div class="cds-calendar">
            <div class="cds-calendar__grid">
              <div v-for="day in weekdays" :key="day" class="cds-calendar__weekday">{{ day }}</div>
              <div
                v-for="cell in calendarCells"
                :key="cell.iso"
                class="cds-calendar__cell"
                :class="{ 'cds-calendar__cell--other-month': !cell.inMonth, 'cds-calendar__cell--today': cell.isToday }"
              >
                <span class="cds-calendar__day">{{ cell.day }}</span>
                <a
                  v-for="release in cell.releases"
                  :key="release.id"
                  :href="release.url || '#'"
                  :target="release.url ? '_blank' : undefined"
                  :rel="release.url ? 'noreferrer' : undefined"
                  class="cds-calendar__chip"
                  :class="[releaseChipClass(release), { 'cds-calendar__chip--hovered': hoveredReleaseId === release.id }]"
                  @mouseenter="hoveredReleaseId = release.id"
                  @mouseleave="hoveredReleaseId = null"
                >
                  <span class="cds-calendar__chip-label">{{ release.name }}</span>
                  <span class="cds-tooltip">
                    <strong class="cds-tooltip__title">{{ release.name }}</strong>
                    <div class="cds-tooltip__row">Status: {{ releaseStatusLabel(release) }}</div>
                    <div v-if="release.release_date" class="cds-tooltip__row">Release: {{ formatDate(release.release_date) }}<span v-if="relativeDays(release.release_date)"> · {{ relativeDays(release.release_date) }}</span></div>
                    <div v-if="release.start_date" class="cds-tooltip__row">Start: {{ formatDate(release.start_date) }}</div>
                    <div v-if="release.description" class="cds-tooltip__desc">{{ truncate(release.description, 240) }}</div>
                  </span>
                </a>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div v-else-if="currentView === 'github'" class="cds-home">
        <section class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">Ready for review</h2>
            <div class="cds-row cds-row--gap-3 cds-row--wrap">
              <span v-if="githubFetchedAt" class="cds-text-helper">{{ githubStatusLabel }}</span>
              <button @click="refreshGithubPullRequests" :disabled="githubLoading" class="cds-btn cds-btn--primary">Refresh</button>
            </div>
          </div>

          <div v-if="githubLoading && !hasGithubPullRequests" class="cds-empty">Loading pull requests…</div>
          <pre v-else-if="githubError" class="cds-notification">{{ githubError }}</pre>
          <div v-else-if="!hasHomeGithubPullRequests" class="cds-empty">No PRs ready for review.</div>
          <div v-else class="cds-pr-grid">
            <div class="cds-pr-col">
              <h3 class="cds-pr-col__title">
                Needs my review
                <span class="cds-pr-col__count">{{ homeReviewRequested.length }}</span>
              </h3>
              <ul v-if="homeReviewRequested.length" class="cds-list cds-list--divided">
                <li v-for="pr in homeReviewRequested" :key="pr.id" class="cds-stack-2">
                  <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title">
                    <span class="cds-text-truncate">{{ pr.title }}</span>
                  </a>
                  <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                    <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                    <span v-if="pr.author">by {{ pr.author }}</span>
                    <span v-if="pr.updated_at">· {{ formatRelative(pr.updated_at) }}</span>
                  </div>
                </li>
              </ul>
              <div v-else class="cds-empty">Nothing waiting on you.</div>
            </div>
            <div class="cds-pr-col">
              <h3 class="cds-pr-col__title">
                My open PRs
                <span class="cds-pr-col__count">{{ homeAuthored.length }}</span>
              </h3>
              <ul v-if="homeAuthored.length" class="cds-list cds-list--divided">
                <li v-for="pr in homeAuthored" :key="pr.id" class="cds-stack-2">
                  <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title">
                    <span class="cds-text-truncate">{{ pr.title }}</span>
                  </a>
                  <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                    <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                    <span v-if="pr.updated_at">{{ formatRelative(pr.updated_at) }}</span>
                  </div>
                </li>
              </ul>
              <div v-else class="cds-empty">No open PRs.</div>
            </div>
          </div>
        </section>

        <section v-if="hasDraftPullRequests" class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">Drafts</h2>
          </div>
          <div class="cds-pr-grid">
            <div class="cds-pr-col">
              <h3 class="cds-pr-col__title">
                Needs my review
                <span class="cds-pr-col__count">{{ draftReviewRequested.length }}</span>
              </h3>
              <ul v-if="draftReviewRequested.length" class="cds-list cds-list--divided">
                <li v-for="pr in draftReviewRequested" :key="pr.id" class="cds-stack-2">
                  <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title">
                    <span class="cds-text-truncate">{{ pr.title }}</span>
                  </a>
                  <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                    <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                    <span v-if="pr.author">by {{ pr.author }}</span>
                    <span v-if="pr.updated_at">· {{ formatRelative(pr.updated_at) }}</span>
                  </div>
                </li>
              </ul>
              <div v-else class="cds-empty">No drafts waiting on you.</div>
            </div>
            <div class="cds-pr-col">
              <h3 class="cds-pr-col__title">
                My open PRs
                <span class="cds-pr-col__count">{{ draftAuthored.length }}</span>
              </h3>
              <ul v-if="draftAuthored.length" class="cds-list cds-list--divided">
                <li v-for="pr in draftAuthored" :key="pr.id" class="cds-stack-2">
                  <a :href="pr.url" target="_blank" rel="noreferrer" class="cds-pr-title">
                    <span class="cds-text-truncate">{{ pr.title }}</span>
                  </a>
                  <div class="cds-row cds-row--gap-3 cds-row--wrap cds-text-helper">
                    <span class="cds-text-mono">{{ pr.repo }}#{{ pr.number }}</span>
                    <span v-if="pr.updated_at">{{ formatRelative(pr.updated_at) }}</span>
                  </div>
                </li>
              </ul>
              <div v-else class="cds-empty">No draft PRs.</div>
            </div>
          </div>
        </section>
      </div>

      <div v-else-if="currentView === 'settings'" class="cds-home">
        <section class="cds-tile">
          <div class="cds-tile__head">
            <h2 class="cds-tile__title">Settings</h2>
          </div>

          <pre v-if="settingsError" class="cds-notification">{{ settingsError }}</pre>

          <div class="cds-stack-5">
            <div class="cds-settings-row">
              <div class="cds-stack-2 cds-grow">
                <label class="cds-fw-500" for="jira-token">Jira API token</label>
                <div class="cds-text-helper">
                  <template v-if="featureFlags.jira">Saved · enter a new value to replace it.</template>
                  <template v-else>Not set · the Jira pages and panels are hidden until you save a token.</template>
                </div>
                <input
                  id="jira-token"
                  v-model="jiraTokenInput"
                  type="password"
                  autocomplete="off"
                  spellcheck="false"
                  :placeholder="featureFlags.jira ? '••••••••' : 'Paste Jira API token'"
                  class="cds-input"
                />
              </div>
              <div class="cds-row cds-row--gap-3 cds-no-shrink">
                <button
                  type="button"
                  @click="saveSetting('jira_token')"
                  :disabled="!jiraTokenInput || settingsSaving.jira_token"
                  class="cds-btn cds-btn--primary cds-btn--field"
                >Save</button>
                <button
                  v-if="featureFlags.jira"
                  type="button"
                  @click="clearSetting('jira_token')"
                  :disabled="settingsSaving.jira_token"
                  class="cds-btn cds-btn--danger cds-btn--field"
                >Clear</button>
              </div>
            </div>

            <div class="cds-settings-row">
              <div class="cds-stack-2 cds-grow">
                <label class="cds-fw-500" for="github-token">GitHub personal access token</label>
                <div class="cds-text-helper">
                  <template v-if="featureFlags.github">Saved · enter a new value to replace it.</template>
                  <template v-else>Not set · the Pull Requests page and panels are hidden until you save a token.</template>
                </div>
                <input
                  id="github-token"
                  v-model="githubTokenInput"
                  type="password"
                  autocomplete="off"
                  spellcheck="false"
                  :placeholder="featureFlags.github ? '••••••••' : 'Paste GitHub PAT'"
                  class="cds-input"
                />
              </div>
              <div class="cds-row cds-row--gap-3 cds-no-shrink">
                <button
                  type="button"
                  @click="saveSetting('github_token')"
                  :disabled="!githubTokenInput || settingsSaving.github_token"
                  class="cds-btn cds-btn--primary cds-btn--field"
                >Save</button>
                <button
                  v-if="featureFlags.github"
                  type="button"
                  @click="clearSetting('github_token')"
                  :disabled="settingsSaving.github_token"
                  class="cds-btn cds-btn--danger cds-btn--field"
                >Clear</button>
              </div>
            </div>

            <div v-if="featureFlags.jira" class="cds-settings-row">
              <div class="cds-stack-3 cds-grow">
                <label class="cds-fw-500">Jira swimlane authors</label>
                <div class="cds-text-helper">
                  Pick which authors appear in <em>Swimlanes by author</em>. Leave all unchecked to include everyone.
                </div>
                <div v-if="swimlaneAuthorOptions.length === 0" class="cds-empty">
                  No authors seen yet. Refresh Jira updates first to populate this list.
                </div>
                <div v-else class="cds-row cds-row--gap-3 cds-row--wrap">
                  <label
                    v-for="author in swimlaneAuthorOptions"
                    :key="author"
                    class="cds-checkbox"
                  >
                    <input
                      type="checkbox"
                      :value="author"
                      :checked="jiraSwimlaneAuthors.includes(author)"
                      @change="toggleSwimlaneAuthor(author)"
                    />
                    <span>{{ author }}</span>
                  </label>
                </div>
              </div>
              <div class="cds-row cds-row--gap-3 cds-no-shrink">
                <button
                  type="button"
                  @click="saveSwimlaneAuthors"
                  :disabled="settingsSaving.jira_swimlane_authors"
                  class="cds-btn cds-btn--primary cds-btn--field"
                >Save</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import {
  Asleep20,
  Calendar20,
  ChevronDown20,
  Task20,
  Home20,
  Light20,
  PullRequest20,
  Settings20,
} from '@carbon/icons-vue';
import {
  listBookmarks,
  addBookmark,
  recordClick,
  listTodayEvents,
  linkBookmarkToEvent,
  unlinkBookmarkFromEvent,
  listJiraUpdates,
  listJiraReleases,
  listGitHubPullRequests,
  getSettings,
  updateSettings,
} from './bookmarks.js';

const BOOKMARK_LIMIT = 10;
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function startOfDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

function isoDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

// Parse a Jira-style date as the local-calendar day, not UTC midnight.
// `new Date("2026-04-27")` is UTC, which displays as the previous day in
// any negative-offset timezone. For YYYY-MM-DD strings we construct a Date
// in local time so the calendar/labels match what the user sees.
function parseLocalDate(value) {
  if (!value) return null;
  if (typeof value === 'string') {
    const m = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  }
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export default {
  components: {
    Asleep20,
    Calendar20,
    ChevronDown20,
    Task20,
    Home20,
    Light20,
    PullRequest20,
    Settings20,
  },
  data() {
    return {
      bookmarks: [],
      bookmarksLoading: true,
      bookmarksError: null,
      events: [],
      eventsLoading: true,
      eventsError: null,
      suggestionsByEvent: {},
      selectedBookmarkByEvent: {},
      bookmarkQueryByEvent: {},
      focusedEventId: null,
      newBookmarkUrl: '',
      newBookmarkTitle: '',
      newBookmarkTags: '',
      searchQuery: '',
      showAddForm: false,
      jiraUpdates: [],
      jiraLoading: false,
      jiraError: null,
      jiraFetchedAt: null,
      jiraCached: false,
      jiraAuthorFilter: '',
      jiraTypeFilter: '',
      currentView: 'home',
      theme: 'dark',
      releases: [],
      releasesLoading: false,
      releasesError: null,
      releasesFetchedAt: null,
      releasesCached: false,
      hoveredReleaseId: null,
      releaseCalendarMonth: { year: new Date().getFullYear(), month: new Date().getMonth() },
      weekdays: WEEKDAYS,
      BOOKMARK_LIMIT,
      githubReviewRequested: [],
      githubAuthored: [],
      githubLoading: false,
      githubError: null,
      githubFetchedAt: null,
      githubCached: false,
      homePrCollapsed: true,
      featureFlags: { jira: false, github: false },
      settingsLoaded: false,
      settingsError: null,
      settingsSaving: { jira_token: false, github_token: false, jira_swimlane_authors: false },
      jiraTokenInput: '',
      githubTokenInput: '',
      jiraSwimlaneAuthors: [],
    };
  },
  computed: {
    displayBookmarks() {
      return this.bookmarks.slice(0, BOOKMARK_LIMIT);
    },
    jiraStatusLabel() {
      if (!this.jiraFetchedAt) return '';
      const date = new Date(this.jiraFetchedAt * 1000);
      const stamp = date.toLocaleTimeString();
      return this.jiraCached ? `Cached · ${stamp}` : `Updated ${stamp}`;
    },
    jiraAuthors() {
      const seen = new Set();
      for (const update of this.jiraUpdates) {
        if (update.author) seen.add(update.author);
      }
      return Array.from(seen).sort((a, b) => a.localeCompare(b));
    },
    filteredJiraUpdates() {
      return this.jiraUpdates.filter((update) => {
        if (this.jiraAuthorFilter && update.author !== this.jiraAuthorFilter) return false;
        if (this.jiraTypeFilter && update.type !== this.jiraTypeFilter) return false;
        return true;
      });
    },
    releasesStatusLabel() {
      if (!this.releasesFetchedAt) return '';
      const date = new Date(this.releasesFetchedAt * 1000);
      const stamp = date.toLocaleTimeString();
      return this.releasesCached ? `Cached · ${stamp}` : `Updated ${stamp}`;
    },
    sortedReleases() {
      const today = startOfDay(new Date()).getTime();
      const distance = (release) => {
        const parsed = parseLocalDate(release.release_date);
        if (!parsed) return Number.POSITIVE_INFINITY;
        return Math.abs(startOfDay(parsed).getTime() - today);
      };
      return [...this.releases].sort((a, b) => distance(a) - distance(b));
    },
    releasesByDate() {
      const map = new Map();
      for (const release of this.releases) {
        if (!release.release_date) continue;
        if (!map.has(release.release_date)) map.set(release.release_date, []);
        map.get(release.release_date).push(release);
      }
      return map;
    },
    calendarTitle() {
      const { year, month } = this.releaseCalendarMonth;
      return new Date(year, month, 1).toLocaleString(undefined, { month: 'long', year: 'numeric' });
    },
    calendarCells() {
      const { year, month } = this.releaseCalendarMonth;
      const firstOfMonth = new Date(year, month, 1);
      const start = new Date(year, month, 1 - firstOfMonth.getDay());
      const today = startOfDay(new Date()).getTime();
      const cells = [];
      for (let i = 0; i < 42; i += 1) {
        const d = new Date(start);
        d.setDate(start.getDate() + i);
        const iso = isoDate(d);
        cells.push({
          iso,
          day: d.getDate(),
          inMonth: d.getMonth() === month,
          isToday: startOfDay(d).getTime() === today,
          releases: this.releasesByDate.get(iso) || [],
        });
      }
      return cells;
    },
    githubStatusLabel() {
      if (!this.githubFetchedAt) return '';
      const date = new Date(this.githubFetchedAt * 1000);
      const stamp = date.toLocaleTimeString();
      return this.githubCached ? `Cached · ${stamp}` : `Updated ${stamp}`;
    },
    swimlaneAuthorOptions() {
      const seen = new Set();
      for (const update of this.jiraUpdates) {
        if (update.author) seen.add(update.author);
      }
      for (const a of this.jiraSwimlaneAuthors) seen.add(a);
      return Array.from(seen).sort((a, b) => a.localeCompare(b));
    },
    hasGithubPullRequests() {
      return (this.githubReviewRequested.length + this.githubAuthored.length) > 0;
    },
    homeReviewRequested() {
      return this.githubReviewRequested.filter((pr) => !pr.draft);
    },
    homeAuthored() {
      return this.githubAuthored.filter((pr) => !pr.draft);
    },
    hasHomeGithubPullRequests() {
      return (this.homeReviewRequested.length + this.homeAuthored.length) > 0;
    },
    draftReviewRequested() {
      return this.githubReviewRequested.filter((pr) => pr.draft);
    },
    draftAuthored() {
      return this.githubAuthored.filter((pr) => pr.draft);
    },
    hasDraftPullRequests() {
      return (this.draftReviewRequested.length + this.draftAuthored.length) > 0;
    },
    reviewRequestedNonDraftCount() {
      return this.homeReviewRequested.length;
    },
    jiraSwimlanes() {
      const isHumanAuthor = (name) => {
        if (!name) return false;
        const n = name.toLowerCase();
        if (n.includes('slack')) return false;
        if (n.includes('automation for jira')) return false;
        if (n.includes('atlassian assist')) return false;
        if (n.endsWith('bot') || n.includes('(bot)')) return false;
        return true;
      };
      const allowed = this.jiraSwimlaneAuthors.length
        ? new Set(this.jiraSwimlaneAuthors)
        : null;
      const lanesByAuthor = new Map();
      for (const update of this.jiraUpdates) {
        if (!isHumanAuthor(update.author)) continue;
        if (allowed && !allowed.has(update.author)) continue;
        if (!lanesByAuthor.has(update.author)) {
          lanesByAuthor.set(update.author, []);
        }
        lanesByAuthor.get(update.author).push(update);
      }
      const lanes = Array.from(lanesByAuthor, ([author, updates]) => ({ author, updates }));
      lanes.sort((a, b) => {
        const ta = a.updates[0]?.timestamp || '';
        const tb = b.updates[0]?.timestamp || '';
        if (ta !== tb) return tb.localeCompare(ta);
        return a.author.localeCompare(b.author);
      });
      return lanes;
    },
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
    async fetchTodayEvents() {
      this.eventsLoading = true;
      this.eventsError = null;
      try {
        this.events = await listTodayEvents();
        await this.syncMeetingContexts();
        await this.loadSuggestionsForVisibleEvents();
      } catch (e) {
        this.eventsError = e.message || 'Failed to load calendar events.';
      } finally {
        this.eventsLoading = false;
      }
    },
    formatEventTime(value) {
      if (!value) return 'Time unavailable';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString();
    },
    formatRelative(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      const seconds = Math.max(0, (Date.now() - date.getTime()) / 1000);
      if (seconds < 60) return 'just now';
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      if (days < 7) return `${days}d ago`;
      return date.toLocaleDateString();
    },
    truncate(text, max) {
      if (!text) return '';
      if (text.length <= max) return text;
      return `${text.slice(0, max).trimEnd()}…`;
    },
    bookmarkLabel(bookmark) {
      return bookmark.title || bookmark.url;
    },
    meetingMappingKey(event) {
      return event.mapping_key || event.id;
    },
    eventSuggestions(event) {
      return this.suggestionsByEvent[this.meetingMappingKey(event)] || [];
    },
    async fetchJiraUpdates({ refresh = false } = {}) {
      this.jiraLoading = true;
      this.jiraError = null;
      try {
        const result = await listJiraUpdates({ refresh });
        this.jiraUpdates = result.updates || [];
        this.jiraFetchedAt = result.fetched_at;
        this.jiraCached = !!result.cached;
      } catch (e) {
        this.jiraError = e.message || 'Failed to load Jira updates.';
      } finally {
        this.jiraLoading = false;
      }
    },
    async refreshJiraUpdates() {
      await this.fetchJiraUpdates({ refresh: true });
    },
    async fetchGithubPullRequests({ refresh = false } = {}) {
      this.githubLoading = true;
      this.githubError = null;
      try {
        const result = await listGitHubPullRequests({ refresh });
        this.githubReviewRequested = result.review_requested || [];
        this.githubAuthored = result.authored || [];
        this.githubFetchedAt = result.fetched_at;
        this.githubCached = !!result.cached;
      } catch (e) {
        this.githubError = e.message || 'Failed to load GitHub pull requests.';
      } finally {
        this.githubLoading = false;
      }
    },
    async refreshGithubPullRequests() {
      await this.fetchGithubPullRequests({ refresh: true });
    },
    applySettingsResponse(flags) {
      this.featureFlags = {
        jira: !!flags.jira_token_set,
        github: !!flags.github_token_set,
      };
      this.jiraSwimlaneAuthors = Array.isArray(flags.jira_swimlane_authors)
        ? flags.jira_swimlane_authors.slice()
        : [];
    },
    async loadSettings() {
      this.settingsError = null;
      try {
        const flags = await getSettings();
        this.applySettingsResponse(flags);
        this.settingsLoaded = true;
      } catch (e) {
        this.settingsError = e.message || 'Failed to load settings.';
      }
    },
    toggleSwimlaneAuthor(author) {
      const idx = this.jiraSwimlaneAuthors.indexOf(author);
      if (idx === -1) this.jiraSwimlaneAuthors.push(author);
      else this.jiraSwimlaneAuthors.splice(idx, 1);
    },
    async saveSwimlaneAuthors() {
      this.settingsError = null;
      this.settingsSaving.jira_swimlane_authors = true;
      try {
        const flags = await updateSettings({ jira_swimlane_authors: this.jiraSwimlaneAuthors });
        this.applySettingsResponse(flags);
      } catch (e) {
        this.settingsError = e.message || 'Failed to save authors.';
      } finally {
        this.settingsSaving.jira_swimlane_authors = false;
      }
    },
    async saveSetting(key) {
      this.settingsError = null;
      const value = key === 'jira_token' ? this.jiraTokenInput : this.githubTokenInput;
      if (!value) return;
      this.settingsSaving[key] = true;
      try {
        const flags = await updateSettings({ [key]: value });
        this.applySettingsResponse(flags);
        if (key === 'jira_token') {
          this.jiraTokenInput = '';
          this.fetchJiraUpdates({ refresh: true });
        } else {
          this.githubTokenInput = '';
          this.fetchGithubPullRequests({ refresh: true });
        }
      } catch (e) {
        this.settingsError = e.message || 'Failed to save setting.';
      } finally {
        this.settingsSaving[key] = false;
      }
    },
    async clearSetting(key) {
      this.settingsError = null;
      this.settingsSaving[key] = true;
      try {
        const flags = await updateSettings({ [key]: '' });
        this.applySettingsResponse(flags);
        if (key === 'jira_token') {
          this.jiraUpdates = [];
          this.releases = [];
          this.jiraFetchedAt = null;
          this.releasesFetchedAt = null;
        } else {
          this.githubReviewRequested = [];
          this.githubAuthored = [];
          this.githubFetchedAt = null;
        }
      } catch (e) {
        this.settingsError = e.message || 'Failed to clear setting.';
      } finally {
        this.settingsSaving[key] = false;
      }
    },
    async fetchReleases({ refresh = false } = {}) {
      this.releasesLoading = true;
      this.releasesError = null;
      try {
        const result = await listJiraReleases({ refresh });
        this.releases = result.releases || [];
        this.releasesFetchedAt = result.fetched_at;
        this.releasesCached = !!result.cached;
        this.focusCalendarOnNearestRelease();
      } catch (e) {
        this.releasesError = e.message || 'Failed to load releases.';
      } finally {
        this.releasesLoading = false;
      }
    },
    async refreshReleases() {
      await this.fetchReleases({ refresh: true });
    },
    focusCalendarOnNearestRelease() {
      const today = startOfDay(new Date());
      const dated = this.releases
        .map((r) => ({ r, d: parseLocalDate(r.release_date) }))
        .filter(({ d }) => d);
      if (dated.length === 0) return;
      // Pick the soonest upcoming release; if none, the most recent past one.
      const future = dated.filter(({ d }) => d.getTime() >= today.getTime()).sort((a, b) => a.d - b.d);
      const target = future[0] || dated.sort((a, b) => b.d - a.d)[0];
      if (!target) return;
      this.releaseCalendarMonth = { year: target.d.getFullYear(), month: target.d.getMonth() };
    },
    prevMonth() {
      const { year, month } = this.releaseCalendarMonth;
      const prev = new Date(year, month - 1, 1);
      this.releaseCalendarMonth = { year: prev.getFullYear(), month: prev.getMonth() };
    },
    nextMonth() {
      const { year, month } = this.releaseCalendarMonth;
      const next = new Date(year, month + 1, 1);
      this.releaseCalendarMonth = { year: next.getFullYear(), month: next.getMonth() };
    },
    goToToday() {
      const now = new Date();
      this.releaseCalendarMonth = { year: now.getFullYear(), month: now.getMonth() };
    },
    formatDate(value) {
      const date = parseLocalDate(value);
      if (!date) return value || '';
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    },
    relativeDays(value) {
      const target = parseLocalDate(value);
      if (!target) return '';
      const today = startOfDay(new Date());
      const days = Math.round((startOfDay(target).getTime() - today.getTime()) / 86400000);
      if (days === 0) return 'Today';
      if (days === 1) return 'Tomorrow';
      if (days === -1) return 'Yesterday';
      if (days > 0) return `In ${days} days`;
      return `${Math.abs(days)} days ago`;
    },
    isPastRelease(release) {
      const target = parseLocalDate(release.release_date);
      if (!target) return false;
      return startOfDay(target).getTime() < startOfDay(new Date()).getTime();
    },
    releaseStatusLabel(release) {
      if (release.archived) return 'Archived';
      if (release.released) return 'Released';
      return 'Unreleased';
    },
    releaseStatusClass(release) {
      if (release.archived) return 'cds-tag--gray';
      if (release.released) return 'cds-tag--green';
      return 'cds-tag--blue';
    },
    releaseChipClass(release) {
      if (release.archived) return 'cds-calendar__chip--archived';
      if (release.released) return 'cds-calendar__chip--released';
      return 'cds-calendar__chip--unreleased';
    },
    applyTheme(theme) {
      this.theme = theme === 'light' ? 'light' : 'dark';
      document.documentElement.dataset.theme = this.theme === 'light' ? 'light' : '';
      try {
        localStorage.setItem('theme', this.theme);
      } catch (_) { /* no-op */ }
    },
    toggleTheme() {
      this.applyTheme(this.theme === 'light' ? 'dark' : 'light');
    },
    async syncMeetingContexts() {
      if (!chrome?.runtime?.sendMessage) return;
      const contexts = this.events
        .map((event) => ({
          mappingKey: this.meetingMappingKey(event),
          startTime: event.start_time,
          endTime: event.end_time,
          summary: event.summary,
        }))
        .filter((context) => context.startTime && context.endTime);

      await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          { type: 'update-meeting-contexts', contexts },
          (result) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }
            if (!result?.ok) {
              reject(new Error(result?.error || 'Failed to sync meeting contexts.'));
              return;
            }
            resolve(result);
          },
        );
      });
    },
    async loadSuggestionsForEvent(event) {
      const mappingKey = this.meetingMappingKey(event);
      if (!mappingKey || !chrome?.runtime?.sendMessage) return;

      const response = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          { type: 'get-meeting-suggestions', mappingKey, limit: 6 },
          (result) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }
            resolve(result);
          },
        );
      });
      if (!response?.ok) return;

      this.suggestionsByEvent = {
        ...this.suggestionsByEvent,
        [mappingKey]: response.suggestions || [],
      };
    },
    async loadSuggestionsForVisibleEvents() {
      await Promise.all(this.events.map((event) => this.loadSuggestionsForEvent(event)));
    },
    filteredEventBookmarks(event) {
      const query = (this.bookmarkQueryByEvent[event.id] || '').trim().toLowerCase();
      const linkedBookmarkIds = new Set((event.bookmarks || []).map((bookmark) => bookmark.id));

      const candidates = this.bookmarks.filter((bookmark) => !linkedBookmarkIds.has(bookmark.id));
      if (!query) return candidates.slice(0, 8);

      return candidates.filter((bookmark) => {
        const label = this.bookmarkLabel(bookmark).toLowerCase();
        return label.includes(query) || bookmark.url.toLowerCase().includes(query);
      }).slice(0, 8);
    },
    onEventBookmarkInput(eventId, value) {
      this.bookmarkQueryByEvent = { ...this.bookmarkQueryByEvent, [eventId]: value };
      this.selectedBookmarkByEvent = { ...this.selectedBookmarkByEvent, [eventId]: null };
    },
    selectEventBookmark(eventId, bookmark) {
      this.selectedBookmarkByEvent = { ...this.selectedBookmarkByEvent, [eventId]: bookmark.id };
      this.bookmarkQueryByEvent = { ...this.bookmarkQueryByEvent, [eventId]: this.bookmarkLabel(bookmark) };
      this.focusedEventId = null;
    },
    onEventBookmarkBlur(eventId) {
      setTimeout(() => {
        if (this.focusedEventId === eventId) this.focusedEventId = null;
      }, 120);
    },
    async addBookmarkToEvent(event) {
      const bookmarkId = this.selectedBookmarkByEvent[event.id];
      if (!bookmarkId) return;
      try {
        const mappingKey = event.mapping_key || event.id;
        const updated = await linkBookmarkToEvent(mappingKey, Number(bookmarkId), event.summary, event.start_time);
        this.events = this.events.map((existing) => (
          existing.id === event.id
            ? { ...existing, bookmarks: updated.bookmarks || [] }
            : existing
        ));
        this.selectedBookmarkByEvent = { ...this.selectedBookmarkByEvent, [event.id]: null };
        this.bookmarkQueryByEvent = { ...this.bookmarkQueryByEvent, [event.id]: '' };
        await this.loadSuggestionsForEvent(event);
      } catch (e) {
        this.eventsError = e.message || 'Failed to link bookmark to event.';
      }
    },
    async removeBookmarkFromEvent(eventId, bookmarkId) {
      try {
        await unlinkBookmarkFromEvent(eventId, bookmarkId);
        this.events = this.events.map((event) => (
          event.id === eventId
            ? { ...event, bookmarks: event.bookmarks.filter((bookmark) => bookmark.id !== bookmarkId) }
            : event
        ));
      } catch (e) {
        this.eventsError = e.message || 'Failed to unlink bookmark from event.';
      }
    },
    async openSuggestedForEvent(event) {
      const links = this.eventSuggestions(event).map((suggestion) => suggestion.url).filter(Boolean);
      if (!links.length) return;

      try {
        if (!chrome?.runtime?.sendMessage) {
          throw new Error('Extension runtime messaging is unavailable.');
        }

        const response = await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage(
            {
              type: 'open-event-bookmarks',
              links,
            },
            (result) => {
              if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message));
                return;
              }
              resolve(result);
            },
          );
        });

        if (!response?.ok) {
          throw new Error(response?.error || 'Failed to open suggested URLs.');
        }
      } catch (e) {
        this.eventsError = e.message || 'Failed to open suggested URLs.';
      }
    },
    async openAllForEvent(event) {
      const links = (event.bookmarks || []).map((bookmark) => bookmark.url).filter(Boolean);
      if (links.length === 0) return;

      try {
        if (!chrome?.runtime?.sendMessage) {
          throw new Error('Extension runtime messaging is unavailable.');
        }

        const response = await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage(
            {
              type: 'open-event-bookmarks',
              links,
              groupTitle: event.summary || 'Meeting',
            },
            (result) => {
              if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message));
                return;
              }
              resolve(result);
            },
          );
        });

        if (!response?.ok) {
          throw new Error(response?.error || 'Failed to open bookmarks for event.');
        }
        if (response?.warning) {
          this.eventsError = `Opened ${response.openedCount || 0}/${(event.bookmarks || []).length} tabs. ${response.warning}`;
        }
      } catch (e) {
        this.eventsError = e.message || 'Failed to open bookmarks for event.';
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
  watch: {
    currentView(view) {
      if (!this.featureFlags.jira && (view === 'swimlanes' || view === 'releases')) {
        this.currentView = 'settings';
        return;
      }
      if (!this.featureFlags.github && view === 'github') {
        this.currentView = 'settings';
        return;
      }
      if (view === 'releases' && this.releases.length === 0 && !this.releasesLoading && !this.releasesError) {
        this.fetchReleases();
      }
    },
  },
  async mounted() {
    let storedTheme = null;
    try { storedTheme = localStorage.getItem('theme'); } catch (_) { /* no-op */ }
    this.applyTheme(storedTheme === 'light' ? 'light' : 'dark');

    this.fetchBookmarks();
    this.fetchTodayEvents();

    await this.loadSettings();
    if (this.featureFlags.jira) this.fetchJiraUpdates();
    if (this.featureFlags.github) this.fetchGithubPullRequests();
    if (!this.featureFlags.jira && !this.featureFlags.github && this.settingsLoaded) {
      this.currentView = 'settings';
    }

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
