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
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'workstreams' }"
        @click="currentView = 'workstreams'"
        title="Workstreams"
        aria-label="Workstreams"
      >
        <Roadmap20 aria-hidden="true" />
      </button>
      <button
        v-if="featureFlags.jira"
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'my-issues' }"
        @click="currentView = 'my-issues'"
        title="My tasks"
        aria-label="My tasks"
      >
        <TaskStar20 aria-hidden="true" />
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
        v-if="featureFlags.jira"
        type="button"
        class="cds-rail__btn"
        :class="{ 'cds-rail__btn--active': currentView === 'incomplete' }"
        @click="currentView = 'incomplete'"
        title="Incomplete issues"
        aria-label="Incomplete issues"
      >
        <IncompleteWarning20 aria-hidden="true" />
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
    </nav>

    <header class="cds-header">
      <div class="cds-header__inner">
        <input
          v-model="searchQuery"
          @input="onSearch"
          type="text"
          :placeholder="currentView === 'workstreams' ? 'Search workstreams by name or comments…' : 'Search bookmarks…'"
          class="cds-input cds-input--lg cds-input--inverse-layer cds-search"
          autofocus
        />
        <label v-if="currentView === 'workstreams'" class="cds-checkbox cds-no-shrink">
          <input type="checkbox" v-model="showArchived" />
          Show archived
        </label>
      </div>
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
                  <img v-if="bm.favicon_url" :src="bm.favicon_url" alt="" width="16" height="16" class="cds-favicon cds-no-shrink" @error="onFaviconError" />
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
              <li v-for="event in visibleEvents" :key="event.id" class="cds-stack-3">
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
              <li v-if="visibleEvents.length === 0" class="cds-empty">No upcoming events today.</li>
            </ul>
          </section>
        </div>
        </div>
      </div>

      <div v-else-if="currentView === 'my-issues'" class="cds-col-stack">
      <section class="cds-tile">
        <div class="cds-tile__head">
          <h2 class="cds-tile__title">My Tasks ({{ myIssues.length }}{{ myIssuesTruncated ? '+' : '' }})</h2>
          <span v-if="myIssuesFetchedAt" class="cds-text-helper">{{ myIssuesStatusLabel }}</span>
          <button @click="refreshMyIssues" :disabled="myIssuesLoading" class="cds-btn cds-btn--primary">Refresh</button>
        </div>
        <div v-if="myIssuesLoading && myIssues.length === 0" class="cds-empty">Loading my tasks…</div>
        <pre v-else-if="myIssuesError" class="cds-notification">{{ myIssuesError }}</pre>
        <div v-else-if="myIssues.length === 0" class="cds-empty">No open tasks assigned to you.</div>
        <div v-else class="cds-ic__scroll">
          <div class="cds-ic__row cds-ic__head">
            <button type="button" class="cds-th cds-ic__col--key" :class="{ 'cds-th--active': myIssuesSort.key === 'key' }" :aria-sort="ariaSort(myIssuesSort, 'key')" @click="toggleSort(myIssuesSort, 'key')">Issue<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'key') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--summary" :class="{ 'cds-th--active': myIssuesSort.key === 'summary' }" :aria-sort="ariaSort(myIssuesSort, 'summary')" @click="toggleSort(myIssuesSort, 'summary')">Title<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'summary') }}</span></button>
            <button type="button" class="cds-th cds-mi__col--type" :class="{ 'cds-th--active': myIssuesSort.key === 'issue_type' }" :aria-sort="ariaSort(myIssuesSort, 'issue_type')" @click="toggleSort(myIssuesSort, 'issue_type')">Type<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'issue_type') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': myIssuesSort.key === 'created' }" :aria-sort="ariaSort(myIssuesSort, 'created')" @click="toggleSort(myIssuesSort, 'created')">Created<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'created') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': myIssuesSort.key === 'due_date' }" :aria-sort="ariaSort(myIssuesSort, 'due_date')" @click="toggleSort(myIssuesSort, 'due_date')">Due date<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'due_date') }}</span></button>
            <button type="button" class="cds-th cds-mi__col--sprint" :class="{ 'cds-th--active': myIssuesSort.key === 'sprint' }" :aria-sort="ariaSort(myIssuesSort, 'sprint')" @click="toggleSort(myIssuesSort, 'sprint')">Sprint<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'sprint') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--status" :class="{ 'cds-th--active': myIssuesSort.key === 'status' }" :aria-sort="ariaSort(myIssuesSort, 'status')" @click="toggleSort(myIssuesSort, 'status')">Status<span class="cds-th__arrow">{{ sortArrow(myIssuesSort, 'status') }}</span></button>
          </div>
          <div v-for="issue in sortedMyIssues" :key="issue.key" class="cds-ic__row" :class="{ 'cds-ic__row--overdue': isOverdue(issue.due_date) }">
            <a :href="issue.url" target="_blank" rel="noopener" class="cds-ic__col--key cds-link" style="font-weight:500; white-space:nowrap;">{{ issue.key }}</a>
            <span class="cds-ic__col--summary" :title="issue.summary">{{ issue.summary }}</span>
            <span class="cds-mi__col--type">
              <span v-if="issue.issue_type" class="cds-tag cds-tag--blue">{{ issue.issue_type }}</span>
            </span>
            <span class="cds-ic__col--date cds-text-helper">{{ formatDate(issue.created) }}</span>
            <span class="cds-ic__col--date" :class="isOverdue(issue.due_date) ? 'cds-text-error' : 'cds-text-helper'" :title="isOverdue(issue.due_date) ? 'Overdue' : null">{{ issue.due_date ? formatDate(issue.due_date) : '—' }}</span>
            <span class="cds-mi__col--sprint">
              <span v-if="issue.sprint" class="cds-tag cds-tag--purple" :title="issue.sprint">{{ issue.sprint }}</span>
            </span>
            <span class="cds-ic__col--status">
              <span v-if="issue.status" class="cds-tag" style="max-width:100%; overflow:hidden; text-overflow:ellipsis;" :title="issue.status">{{ issue.status }}</span>
            </span>
          </div>
        </div>
      </section>

      <section class="cds-tile">
        <div class="cds-tile__head">
          <h2 class="cds-tile__title">Unassigned ({{ unassignedIssues.length }}{{ unassignedTruncated ? '+' : '' }})</h2>
          <span v-if="unassignedFetchedAt" class="cds-text-helper">{{ unassignedStatusLabel }}</span>
          <button @click="refreshUnassignedIssues" :disabled="unassignedLoading" class="cds-btn cds-btn--primary">Refresh</button>
        </div>
        <div v-if="unassignedLoading && unassignedIssues.length === 0" class="cds-empty">Loading unassigned tasks…</div>
        <pre v-else-if="unassignedError" class="cds-notification">{{ unassignedError }}</pre>
        <div v-else-if="unassignedIssues.length === 0" class="cds-empty">No unassigned tasks — everything has an owner.</div>
        <div v-else class="cds-ic__scroll">
          <div class="cds-ic__row cds-ic__head">
            <button type="button" class="cds-th cds-ic__col--key" :class="{ 'cds-th--active': unassignedSort.key === 'key' }" :aria-sort="ariaSort(unassignedSort, 'key')" @click="toggleSort(unassignedSort, 'key')">Issue<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'key') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--summary" :class="{ 'cds-th--active': unassignedSort.key === 'summary' }" :aria-sort="ariaSort(unassignedSort, 'summary')" @click="toggleSort(unassignedSort, 'summary')">Title<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'summary') }}</span></button>
            <button type="button" class="cds-th cds-mi__col--type" :class="{ 'cds-th--active': unassignedSort.key === 'issue_type' }" :aria-sort="ariaSort(unassignedSort, 'issue_type')" @click="toggleSort(unassignedSort, 'issue_type')">Type<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'issue_type') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': unassignedSort.key === 'created' }" :aria-sort="ariaSort(unassignedSort, 'created')" @click="toggleSort(unassignedSort, 'created')">Created<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'created') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': unassignedSort.key === 'due_date' }" :aria-sort="ariaSort(unassignedSort, 'due_date')" @click="toggleSort(unassignedSort, 'due_date')">Due date<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'due_date') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--age" title="Days since last update" :class="{ 'cds-th--active': unassignedSort.key === 'stale' }" :aria-sort="ariaSort(unassignedSort, 'stale')" @click="toggleSort(unassignedSort, 'stale')">Idle<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'stale') }}</span></button>
            <button type="button" class="cds-th cds-mi__col--sprint" :class="{ 'cds-th--active': unassignedSort.key === 'sprint' }" :aria-sort="ariaSort(unassignedSort, 'sprint')" @click="toggleSort(unassignedSort, 'sprint')">Sprint<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'sprint') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--status" :class="{ 'cds-th--active': unassignedSort.key === 'status' }" :aria-sort="ariaSort(unassignedSort, 'status')" @click="toggleSort(unassignedSort, 'status')">Status<span class="cds-th__arrow">{{ sortArrow(unassignedSort, 'status') }}</span></button>
          </div>
          <div v-for="issue in sortedUnassignedIssues" :key="issue.key" class="cds-ic__row" :class="{ 'cds-ic__row--overdue': isOverdue(issue.due_date) }">
            <a :href="issue.url" target="_blank" rel="noopener" class="cds-ic__col--key cds-link" style="font-weight:500; white-space:nowrap;">{{ issue.key }}</a>
            <span class="cds-ic__col--summary" :title="issue.summary">{{ issue.summary }}</span>
            <span class="cds-mi__col--type">
              <span v-if="issue.issue_type" class="cds-tag cds-tag--blue">{{ issue.issue_type }}</span>
            </span>
            <span class="cds-ic__col--date cds-text-helper">{{ formatDate(issue.created) }}</span>
            <span class="cds-ic__col--date" :class="isOverdue(issue.due_date) ? 'cds-text-error' : 'cds-text-helper'" :title="isOverdue(issue.due_date) ? 'Overdue' : null">{{ issue.due_date ? formatDate(issue.due_date) : '—' }}</span>
            <span class="cds-ic__col--age">
              <span v-if="daysSince(issue.updated) !== null" class="cds-tag" :class="staleTagClass(issue.updated)" :title="`Last updated ${formatDate(issue.updated)}`">{{ daysSince(issue.updated) }}d</span>
              <span v-else class="cds-text-helper">—</span>
            </span>
            <span class="cds-mi__col--sprint">
              <span v-if="issue.sprint" class="cds-tag cds-tag--purple" :title="issue.sprint">{{ issue.sprint }}</span>
            </span>
            <span class="cds-ic__col--status">
              <span v-if="issue.status" class="cds-tag" style="max-width:100%; overflow:hidden; text-overflow:ellipsis;" :title="issue.status">{{ issue.status }}</span>
            </span>
          </div>
        </div>
      </section>
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
              <label class="cds-checkbox">
                <input type="checkbox" v-model="hideReleasedItems" />
                Hide released
              </label>
              <span v-if="releasesFetchedAt" class="cds-text-helper">{{ releasesStatusLabel }}</span>
              <button @click="refreshReleases" :disabled="releasesLoading" class="cds-btn cds-btn--primary">Refresh</button>
            </div>
          </div>

          <div v-if="releasesLoading && releases.length === 0" class="cds-empty">Loading releases…</div>
          <pre v-else-if="releasesError" class="cds-notification">{{ releasesError }}</pre>
          <ul v-else-if="releases.length === 0" class="cds-list"><li class="cds-empty">No releases found.</li></ul>
          <ul v-else-if="sortedReleases.length === 0" class="cds-list"><li class="cds-empty">No releases to show.</li></ul>
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

      <section v-else-if="currentView === 'incomplete'" class="cds-tile">
        <div class="cds-tile__head">
          <h2 class="cds-tile__title">Incomplete Issues ({{ incompleteIssues.length }}{{ incompleteTruncated ? '+' : '' }})</h2>
          <button @click="refreshJiraIncomplete" :disabled="incompleteLoading" class="cds-btn cds-btn--primary">Refresh</button>
        </div>
        <div v-if="incompleteLoading && incompleteIssues.length === 0" class="cds-empty">Loading incomplete issues…</div>
        <pre v-else-if="incompleteError" class="cds-notification">{{ incompleteError }}</pre>
        <div v-else-if="incompleteIssues.length === 0" class="cds-empty">No incomplete issues found.</div>
        <div v-else class="cds-ic__scroll">
          <div class="cds-ic__row cds-ic__head">
            <button type="button" class="cds-th cds-ic__col--key" :class="{ 'cds-th--active': incompleteSort.key === 'key' }" :aria-sort="ariaSort(incompleteSort, 'key')" @click="toggleSort(incompleteSort, 'key')">Issue<span class="cds-th__arrow">{{ sortArrow(incompleteSort, 'key') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--summary" :class="{ 'cds-th--active': incompleteSort.key === 'summary' }" :aria-sort="ariaSort(incompleteSort, 'summary')" @click="toggleSort(incompleteSort, 'summary')">Summary<span class="cds-th__arrow">{{ sortArrow(incompleteSort, 'summary') }}</span></button>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': incompleteSort.key === 'created' }" :aria-sort="ariaSort(incompleteSort, 'created')" @click="toggleSort(incompleteSort, 'created')">Created<span class="cds-th__arrow">{{ sortArrow(incompleteSort, 'created') }}</span></button>
            <span class="cds-ic__col--age">Age</span>
            <button type="button" class="cds-th cds-ic__col--date" :class="{ 'cds-th--active': incompleteSort.key === 'updated' }" :aria-sort="ariaSort(incompleteSort, 'updated')" @click="toggleSort(incompleteSort, 'updated')">Updated<span class="cds-th__arrow">{{ sortArrow(incompleteSort, 'updated') }}</span></button>
            <span class="cds-ic__col--assignee">Assignee</span>
            <span class="cds-ic__col--due">Due date</span>
            <span class="cds-ic__col--status">Status</span>
          </div>
          <div v-for="issue in sortedIncompleteIssues" :key="issue.key" class="cds-ic__row">
            <a :href="issue.url" target="_blank" rel="noopener" class="cds-ic__col--key cds-link" style="font-weight:500; white-space:nowrap;">{{ issue.key }}</a>
            <span class="cds-ic__col--summary" :title="issue.summary">{{ issue.summary }}</span>
            <span class="cds-ic__col--date cds-text-helper">{{ formatDate(issue.created) }}</span>
            <span class="cds-ic__col--age">
              <span class="cds-tag cds-tag--cool-gray" :title="formatDate(issue.created)">{{ issueAge(issue.created) }}</span>
            </span>
            <span class="cds-ic__col--date cds-text-helper" :title="formatDate(issue.updated)">{{ formatDate(issue.updated) }}</span>
            <span class="cds-ic__col--assignee">
              <span v-if="issue.missing_assignee" class="cds-tag cds-tag--red" title="No assignee">No assignee</span>
            </span>
            <span class="cds-ic__col--due">
              <span v-if="issue.missing_due_date" class="cds-tag cds-tag--magenta" title="No due date">No due date</span>
            </span>
            <span class="cds-ic__col--status">
              <span v-if="issue.status" class="cds-tag" style="max-width:100%; overflow:hidden; text-overflow:ellipsis;" :title="issue.status">{{ issue.status }}</span>
            </span>
          </div>
        </div>
      </section>

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

      <div v-else-if="currentView === 'workstreams'" class="cds-col-stack">
        <section v-for="section in workstreamSections" :key="section.key" class="cds-tile">
        <template v-if="section.key === 'active'">
        <div v-if="categories.length" class="cds-row cds-row--gap-2 cds-row--wrap" style="margin-bottom: var(--cds-sp-05)">
          <button
            v-for="cat in categories"
            :key="cat.id"
            type="button"
            class="cds-tag cds-ws-chip-btn"
            :class="categoryFilterIds.includes(cat.id) ? 'cds-tag--purple' : 'cds-tag--gray'"
            :aria-pressed="categoryFilterIds.includes(cat.id)"
            @click="toggleCategoryFilter(cat.id)"
          >{{ cat.name }}</button>
          <button
            v-if="categoryFilterIds.length"
            type="button"
            class="cds-tag cds-tag--gray cds-ws-chip-btn"
            @click="categoryFilterIds = []"
          >× Clear</button>
        </div>

        <div class="cds-tile__head">
          <h2 class="cds-tile__title">Workstreams</h2>
          <div class="cds-row cds-row--gap-3 cds-row--wrap">
            <button v-if="!showAddWorkstream" @click="showAddWorkstream = true" class="cds-btn cds-btn--primary">+ Add workstream</button>
            <button @click="fetchWorkstreams" :disabled="workstreamsLoading" class="cds-btn cds-btn--tertiary">Refresh</button>
          </div>
        </div>

        <form v-if="showAddWorkstream" @submit.prevent="submitWorkstream" class="cds-form-row" style="margin-bottom: var(--cds-sp-05); max-width: 40rem">
          <input v-model="newWorkstreamName" type="text" placeholder="Workstream name" class="cds-input" required />
          <button type="submit" class="cds-btn cds-btn--primary cds-btn--field">Save</button>
          <button type="button" @click="cancelAddWorkstream" class="cds-btn cds-btn--tertiary cds-btn--field">Cancel</button>
        </form>

        <pre v-if="workstreamsError" class="cds-notification">{{ workstreamsError }}</pre>
        </template>

        <div v-else class="cds-tile__head">
          <h2 class="cds-tile__title">Archived ({{ section.lanes.length }})</h2>
        </div>

        <div v-if="section.key === 'active' && workstreamsLoading && workstreams.length === 0" class="cds-empty">Loading workstreams…</div>
        <div v-else-if="section.lanes.length === 0" class="cds-empty">{{ section.emptyText }}</div>
        <div v-else class="cds-swimlanes">
          <div v-for="ws in section.lanes" :key="ws.id" class="cds-swimlane">
            <header class="cds-swimlane__head cds-swimlane__head--start">
              <span class="cds-row cds-row--gap-2 cds-row--wrap cds-grow" style="min-width: 0">
                <span class="cds-swimlane__author" :title="ws.name">{{ ws.name }}</span>
                <span v-for="cat in ws.categories" :key="cat.id" class="cds-tag cds-tag--purple">{{ cat.name }}</span>
              </span>
              <span class="cds-row cds-row--gap-2 cds-no-shrink">
                <span class="cds-swimlane__count">{{ ws.comments.length }}</span>
                <button
                  @click="toggleEditMode(ws.id)"
                  class="cds-ws-edit-btn"
                  :class="{ 'cds-ws-edit-btn--active': editMode[ws.id] }"
                  :aria-pressed="!!editMode[ws.id]"
                  aria-label="Edit categories and links"
                  title="Edit categories and links"
                >
                  <Edit16 aria-hidden="true" />
                </button>
              </span>
            </header>
            <div class="cds-swimlane__body">
              <div v-if="ws.archived_at" class="cds-text-helper" :title="ws.archived_at">
                Archived {{ formatRelative(ws.archived_at) }}
              </div>
              <div v-if="editMode[ws.id]" class="cds-row cds-row--gap-2 cds-row--wrap">
                <button
                  type="button"
                  class="cds-tag cds-tag--gray cds-ws-chip-btn"
                  @click="toggleCategoryPicker(ws.id)"
                >{{ categoryPickerOpen[ws.id] ? 'Done' : '+ Category' }}</button>
              </div>
              <div v-if="editMode[ws.id] && categoryPickerOpen[ws.id]" class="cds-row cds-row--gap-2 cds-row--wrap">
                <span v-if="categories.length === 0" class="cds-text-helper">No categories yet — add them in Settings.</span>
                <label v-for="cat in categories" :key="cat.id" class="cds-checkbox">
                  <input
                    type="checkbox"
                    :checked="ws.categories.some((c) => c.id === cat.id)"
                    @change="toggleWorkstreamCategory(ws, cat)"
                  />
                  <span>{{ cat.name }}</span>
                </label>
              </div>

              <div>
                <button
                  type="button"
                  class="cds-ws-links__trigger"
                  :aria-expanded="!!linksExpanded[ws.id]"
                  @click="toggleLinks(ws.id)"
                >
                  <ChevronDown20
                    class="cds-collapsible-trigger__chevron"
                    :class="{ 'cds-collapsible-trigger__chevron--collapsed': !linksExpanded[ws.id] }"
                    aria-hidden="true"
                  />
                  <span>Links</span>
                  <span class="cds-swimlane__count">{{ ws.links.length }}</span>
                </button>
                <div v-if="linksExpanded[ws.id]" class="cds-stack-2" style="margin-top: var(--cds-sp-02)">
                  <div v-for="link in ws.links" :key="link.id" class="cds-row cds-row--between cds-row--gap-2">
                    <a :href="link.url" target="_blank" rel="noreferrer" class="cds-text-truncate cds-grow" :title="link.url">{{ link.title || link.url }}</a>
                    <button v-if="editMode[ws.id]" @click="removeLink(ws, link.id)" class="cds-tag__close" aria-label="Remove link" title="Remove link">×</button>
                  </div>
                  <div v-if="ws.links.length === 0" class="cds-text-helper">No links yet.</div>
                  <form v-if="editMode[ws.id]" @submit.prevent="submitLink(ws)" class="cds-stack-2">
                    <input v-model="linkUrlDrafts[ws.id]" type="text" placeholder="URL" class="cds-input cds-input--inverse-layer" required />
                    <div class="cds-form-row">
                      <input v-model="linkTitleDrafts[ws.id]" type="text" placeholder="Title (optional)" class="cds-input cds-input--inverse-layer" />
                      <button type="submit" class="cds-btn cds-btn--primary cds-btn--field">Add</button>
                    </div>
                  </form>
                </div>
              </div>

              <div v-if="editMode[ws.id]" class="cds-row cds-row--gap-3 cds-row--wrap">
                <button
                  type="button"
                  @click="toggleArchive(ws)"
                  class="cds-btn cds-btn--secondary"
                >{{ ws.archived_at ? 'Unarchive' : 'Archive' }}</button>
                <button
                  type="button"
                  @click="removeWorkstream(ws)"
                  class="cds-btn cds-btn--danger"
                >Delete</button>
              </div>

              <form @submit.prevent="submitComment(ws)" class="cds-form-row">
                <input v-model="commentDrafts[ws.id]" type="text" placeholder="Add a comment…" class="cds-input cds-input--inverse-layer" />
                <button type="submit" :disabled="!(commentDrafts[ws.id] || '').trim()" class="cds-btn cds-btn--primary cds-btn--field">Add</button>
              </form>

              <article v-for="comment in ws.comments" :key="comment.id" class="cds-card">
                <div class="cds-text-secondary cds-text-pre">{{ comment.body }}</div>
                <div class="cds-row cds-row--between cds-row--gap-2">
                  <span class="cds-text-helper" :title="comment.created_at">{{ formatRelative(comment.created_at) }}</span>
                  <button @click="removeComment(ws, comment.id)" class="cds-tag__close" aria-label="Delete comment" title="Delete comment">×</button>
                </div>
              </article>
              <div v-if="ws.comments.length === 0" class="cds-empty">No comments yet.</div>
            </div>
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
                <label class="cds-fw-500">Theme</label>
                <div class="cds-text-helper">Choose how the new tab page looks.</div>
                <div class="cds-row cds-row--gap-3 cds-row--wrap">
                  <label
                    v-for="option in themeOptions"
                    :key="option.value"
                    class="cds-checkbox"
                  >
                    <input
                      type="radio"
                      name="theme"
                      :value="option.value"
                      :checked="theme === option.value"
                      @change="applyTheme(option.value)"
                    />
                    <span>{{ option.label }}</span>
                  </label>
                </div>
              </div>
            </div>

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

            <div class="cds-settings-row">
              <div class="cds-stack-3 cds-grow">
                <label class="cds-fw-500">Workstream categories</label>
                <div class="cds-text-helper">
                  Categories you can assign to workstreams. They show as chips under the workstream title.
                </div>
                <div v-if="categories.length === 0" class="cds-empty">No categories yet.</div>
                <div v-else class="cds-stack-3">
                  <div v-for="cat in categories" :key="cat.id" class="cds-form-row" style="max-width: 32rem">
                    <input v-model="categoryEdits[cat.id]" type="text" class="cds-input" />
                    <button
                      type="button"
                      @click="renameCategory(cat)"
                      :disabled="!(categoryEdits[cat.id] || '').trim() || (categoryEdits[cat.id] || '').trim() === cat.name"
                      class="cds-btn cds-btn--primary cds-btn--field"
                    >Save</button>
                    <button
                      type="button"
                      @click="removeCategory(cat)"
                      class="cds-btn cds-btn--danger cds-btn--field"
                    >Delete</button>
                  </div>
                </div>
                <form @submit.prevent="submitCategory" class="cds-form-row" style="max-width: 32rem">
                  <input v-model="newCategoryName" type="text" placeholder="New category name" class="cds-input" />
                  <button type="submit" :disabled="!newCategoryName.trim()" class="cds-btn cds-btn--primary cds-btn--field">Add</button>
                </form>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <div v-if="workstreamPicker" class="cds-modal" @click.self="cancelWorkstreamPicker">
      <div class="cds-modal__panel" role="dialog" aria-modal="true" aria-label="Add link to workstream">
        <h2 class="cds-tile__title">Add link to workstream</h2>
        <div class="cds-stack-2">
          <div class="cds-fw-500 cds-text-primary cds-text-truncate" style="max-width: 100%" :title="workstreamPicker.title || workstreamPicker.url">
            {{ workstreamPicker.title || workstreamPicker.url }}
          </div>
          <div class="cds-text-helper cds-text-truncate" style="max-width: 100%" :title="workstreamPicker.url">{{ workstreamPicker.url }}</div>
        </div>
        <pre v-if="pickerError" class="cds-notification">{{ pickerError }}</pre>
        <input
          ref="pickerSearch"
          v-model="pickerQuery"
          @keydown.enter.prevent="pickFirstWorkstream"
          @keydown.esc.prevent="cancelWorkstreamPicker"
          type="text"
          placeholder="Filter workstreams…"
          class="cds-input cds-input--inverse-layer"
        />
        <div class="cds-modal__list">
          <button
            v-for="ws in pickerWorkstreams"
            :key="ws.id"
            type="button"
            class="cds-modal__option"
            :disabled="pickerSaving"
            @click="pickWorkstream(ws)"
          >
            <span class="cds-text-truncate cds-grow">{{ ws.name }}</span>
            <span v-for="cat in ws.categories" :key="cat.id" class="cds-tag cds-tag--purple cds-no-shrink">{{ cat.name }}</span>
          </button>
          <div v-if="pickerWorkstreams.length === 0" class="cds-empty">
            {{ workstreamsLoading ? 'Loading workstreams…' : (workstreams.length === 0 ? 'No workstreams yet — add one first.' : 'No workstreams match.') }}
          </div>
        </div>
        <div class="cds-row cds-row--gap-3" style="justify-content: flex-end">
          <button type="button" @click="cancelWorkstreamPicker" class="cds-btn cds-btn--tertiary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  Calendar20,
  ChevronDown20,
  Edit16,
  IncompleteWarning20,
  Roadmap20,
  Task20,
  TaskStar20,
  Home20,
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
  listJiraIncomplete,
  listJiraMyIssues,
  listJiraUnassigned,
  listGitHubPullRequests,
  listWorkstreams,
  createWorkstream,
  updateWorkstream,
  deleteWorkstream,
  addWorkstreamComment,
  deleteWorkstreamComment,
  addWorkstreamLink,
  deleteWorkstreamLink,
  listCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  getSettings,
  updateSettings,
} from './bookmarks.js';

const BOOKMARK_LIMIT = 10;
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const THEME_OPTIONS = [
  { value: 'dark', label: 'Dark' },
  { value: 'light', label: 'Light' },
  { value: 'minimal', label: 'Minimal dark' },
  { value: 'minimal-light', label: 'Minimal light' },
];

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
    Calendar20,
    ChevronDown20,
    Edit16,
    IncompleteWarning20,
    Roadmap20,
    Task20,
    TaskStar20,
    Home20,
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

      incompleteIssues: [],
      incompleteTruncated: false,
      incompleteLoading: false,
      incompleteError: null,
      incompleteSort: { key: 'created', dir: 'desc' },

      myIssues: [],
      myIssuesTruncated: false,
      myIssuesLoading: false,
      myIssuesError: null,
      myIssuesFetchedAt: null,
      myIssuesCached: false,
      myIssuesSort: { key: 'due_date', dir: 'asc' },
      unassignedIssues: [],
      unassignedTruncated: false,
      unassignedLoading: false,
      unassignedError: null,
      unassignedFetchedAt: null,
      unassignedCached: false,
      unassignedSort: { key: 'due_date', dir: 'asc' },
      jiraAuthorFilter: '',
      jiraTypeFilter: '',
      currentView: 'home',
      theme: 'dark',
      themeOptions: THEME_OPTIONS,
      releases: [],
      releasesLoading: false,
      releasesError: null,
      releasesFetchedAt: null,
      releasesCached: false,
      hideReleasedItems: true,
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

      workstreams: [],
      workstreamsLoading: false,
      workstreamsError: null,
      showArchived: false,
      showAddWorkstream: false,
      newWorkstreamName: '',
      commentDrafts: {},
      linkUrlDrafts: {},
      linkTitleDrafts: {},
      linksExpanded: {},
      categoryPickerOpen: {},
      editMode: {},
      categories: [],
      categoryFilterIds: [],
      newCategoryName: '',
      categoryEdits: {},
      workstreamPicker: null,
      pickerQuery: '',
      pickerError: null,
      pickerSaving: false,

      now: Date.now(),
      nowTickHandle: null,
    };
  },
  computed: {
    sortedIncompleteIssues() {
      return this.sortRows(this.incompleteIssues, this.incompleteSort);
    },
    myIssuesStatusLabel() {
      if (!this.myIssuesFetchedAt) return '';
      const date = new Date(this.myIssuesFetchedAt * 1000);
      const stamp = date.toLocaleTimeString();
      return this.myIssuesCached ? `Cached · ${stamp}` : `Updated ${stamp}`;
    },
    sortedMyIssues() {
      return this.sortRows(this.myIssues, this.myIssuesSort);
    },
    unassignedStatusLabel() {
      if (!this.unassignedFetchedAt) return '';
      const date = new Date(this.unassignedFetchedAt * 1000);
      const stamp = date.toLocaleTimeString();
      return this.unassignedCached ? `Cached · ${stamp}` : `Updated ${stamp}`;
    },
    sortedUnassignedIssues() {
      return this.sortRows(this.unassignedIssues, this.unassignedSort);
    },
    displayBookmarks() {
      return this.bookmarks.slice(0, BOOKMARK_LIMIT);
    },
    visibleEvents() {
      return this.events.filter((event) => {
        const endValue = event.end_time || event.start_time;
        if (!endValue) return true;
        const end = new Date(endValue).getTime();
        if (Number.isNaN(end)) return true;
        return end > this.now;
      });
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
    visibleReleases() {
      if (!this.hideReleasedItems) return this.releases;
      return this.releases.filter((release) => !release.released);
    },
    sortedReleases() {
      const today = startOfDay(new Date()).getTime();
      const distance = (release) => {
        const parsed = parseLocalDate(release.release_date);
        if (!parsed) return Number.POSITIVE_INFINITY;
        return Math.abs(startOfDay(parsed).getTime() - today);
      };
      return [...this.visibleReleases].sort((a, b) => distance(a) - distance(b));
    },
    releasesByDate() {
      const map = new Map();
      for (const release of this.visibleReleases) {
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
    filteredWorkstreams() {
      let list = this.workstreams;
      if (this.categoryFilterIds.length) {
        const wanted = new Set(this.categoryFilterIds);
        list = list.filter((ws) => ws.categories.some((cat) => wanted.has(cat.id)));
      }
      const q = this.searchQuery.trim().toLowerCase();
      if (!q) return list;
      return list.filter((ws) => (
        ws.name.toLowerCase().includes(q)
        || ws.comments.some((comment) => comment.body.toLowerCase().includes(q))
      ));
    },
    activeWorkstreams() {
      // Most recently commented first; never-commented lanes sink, newest first.
      return this.filteredWorkstreams
        .filter((ws) => !ws.archived_at)
        .sort((a, b) => {
          if (!!a.last_comment_at !== !!b.last_comment_at) return a.last_comment_at ? -1 : 1;
          const ta = a.last_comment_at || a.created_at || '';
          const tb = b.last_comment_at || b.created_at || '';
          return tb.localeCompare(ta);
        });
    },
    archivedWorkstreams() {
      return this.filteredWorkstreams
        .filter((ws) => ws.archived_at)
        .sort((a, b) => b.archived_at.localeCompare(a.archived_at));
    },
    workstreamSections() {
      const anyActive = this.workstreams.some((ws) => !ws.archived_at);
      const sections = [{
        key: 'active',
        lanes: this.activeWorkstreams,
        emptyText: anyActive
          ? 'No workstreams match the current filters.'
          : 'No workstreams yet. Add one to get started.',
      }];
      if (this.showArchived) {
        const anyArchived = this.workstreams.some((ws) => ws.archived_at);
        sections.push({
          key: 'archived',
          lanes: this.archivedWorkstreams,
          emptyText: anyArchived
            ? 'No archived workstreams match the current filters.'
            : 'No archived workstreams yet.',
        });
      }
      return sections;
    },
    pickerWorkstreams() {
      const q = this.pickerQuery.trim().toLowerCase();
      const active = this.workstreams.filter((ws) => !ws.archived_at);
      if (!q) return active;
      return active.filter((ws) => ws.name.toLowerCase().includes(q));
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
      return date.toLocaleString('en-US', {
        timeZone: 'America/Los_Angeles',
        weekday: 'short',
        hour: 'numeric',
        minute: '2-digit',
        timeZoneName: 'short',
      });
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
    async fetchJiraIncomplete({ refresh = false } = {}) {
      this.incompleteLoading = true;
      this.incompleteError = null;
      try {
        const result = await listJiraIncomplete({ refresh });
        this.incompleteIssues = result.issues || [];
        this.incompleteTruncated = !!result.truncated;
      } catch (e) {
        this.incompleteError = e.message || 'Failed to fetch incomplete issues';
      } finally {
        this.incompleteLoading = false;
      }
    },
    async refreshJiraIncomplete() {
      await this.fetchJiraIncomplete({ refresh: true });
    },
    async fetchMyIssues({ refresh = false } = {}) {
      this.myIssuesLoading = true;
      this.myIssuesError = null;
      try {
        const result = await listJiraMyIssues({ refresh });
        this.myIssues = result.issues || [];
        this.myIssuesTruncated = !!result.truncated;
        this.myIssuesFetchedAt = result.fetched_at;
        this.myIssuesCached = !!result.cached;
      } catch (e) {
        this.myIssuesError = e.message || 'Failed to fetch my tasks';
      } finally {
        this.myIssuesLoading = false;
      }
    },
    async refreshMyIssues() {
      await this.fetchMyIssues({ refresh: true });
    },
    async fetchUnassignedIssues({ refresh = false } = {}) {
      this.unassignedLoading = true;
      this.unassignedError = null;
      try {
        const result = await listJiraUnassigned({ refresh });
        this.unassignedIssues = result.issues || [];
        this.unassignedTruncated = !!result.truncated;
        this.unassignedFetchedAt = result.fetched_at;
        this.unassignedCached = !!result.cached;
      } catch (e) {
        this.unassignedError = e.message || 'Failed to fetch unassigned tasks';
      } finally {
        this.unassignedLoading = false;
      }
    },
    async refreshUnassignedIssues() {
      await this.fetchUnassignedIssues({ refresh: true });
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
          this.fetchJiraIncomplete({ refresh: true });
          this.fetchMyIssues({ refresh: true });
          this.fetchUnassignedIssues({ refresh: true });
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
          this.incompleteIssues = [];
          this.incompleteTruncated = false;
          this.unassignedIssues = [];
          this.unassignedTruncated = false;
          this.unassignedFetchedAt = null;
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
    // --- Column-header sorting (shared across all issue tables) ---
    sortValue(row, key) {
      switch (key) {
        case 'due_date': return { type: 'date', v: row.due_date };
        case 'created': return { type: 'date', v: row.created };
        case 'updated': return { type: 'date', v: row.updated };
        case 'stale': return { type: 'num', v: this.daysSince(row.updated) };
        default: return { type: 'text', v: row[key] };
      }
    },
    sortRows(rows, sort) {
      const { key, dir } = sort;
      const sign = dir === 'desc' ? -1 : 1;
      const isEmpty = (x) => x === null || x === undefined || x === '';
      return [...rows].sort((a, b) => {
        const av = this.sortValue(a, key);
        const bv = this.sortValue(b, key);
        // Missing values always sink to the bottom, regardless of direction.
        if (isEmpty(av.v) && isEmpty(bv.v)) return 0;
        if (isEmpty(av.v)) return 1;
        if (isEmpty(bv.v)) return -1;
        let cmp;
        if (av.type === 'num') cmp = av.v - bv.v;
        else if (av.type === 'date') cmp = String(av.v).localeCompare(String(bv.v));
        else cmp = String(av.v).toLowerCase().localeCompare(String(bv.v).toLowerCase());
        return sign * cmp;
      });
    },
    toggleSort(sort, key) {
      if (sort.key === key) {
        sort.dir = sort.dir === 'asc' ? 'desc' : 'asc';
        return;
      }
      sort.key = key;
      // Sensible first-click direction per column: soonest-due and A→Z for most
      // columns, but newest/most-idle first for recency-oriented columns.
      const descFirst = { created: true, updated: true, stale: true };
      sort.dir = descFirst[key] ? 'desc' : 'asc';
    },
    sortArrow(sort, key) {
      if (sort.key !== key) return '';
      return sort.dir === 'asc' ? '↑' : '↓';
    },
    ariaSort(sort, key) {
      if (sort.key !== key) return 'none';
      return sort.dir === 'asc' ? 'ascending' : 'descending';
    },
    formatDate(value) {
      const date = parseLocalDate(value);
      if (!date) return value || '';
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    },
    daysSince(value) {
      if (!value) return null;
      const parsed = new Date(value);
      if (isNaN(parsed)) return null;
      const days = Math.floor((startOfDay(new Date()).getTime() - startOfDay(parsed).getTime()) / 86400000);
      return days < 0 ? 0 : days;
    },
    staleTagClass(value) {
      // Escalate the tag colour with idle age so droppable tasks stand out.
      const days = this.daysSince(value);
      if (days === null) return '';
      if (days >= 90) return 'cds-tag--red';
      if (days >= 30) return 'cds-tag--magenta';
      return 'cds-tag--gray';
    },
    issueAge(value) {
      if (!value) return '';
      const created = new Date(value);
      if (isNaN(created)) return '';
      const now = new Date();
      const diffMs = now - created;
      const days = Math.floor(diffMs / 86400000);
      if (days < 1) return 'today';
      if (days === 1) return '1 day';
      if (days < 30) return `${days} days`;
      const months = Math.floor(days / 30);
      if (months < 12) return months === 1 ? '1 month' : `${months} months`;
      const years = Math.floor(days / 365);
      return years === 1 ? '1 year' : `${years} years`;
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
    isOverdue(value) {
      const target = parseLocalDate(value);
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
      this.theme = THEME_OPTIONS.some((option) => option.value === theme) ? theme : 'dark';
      document.documentElement.dataset.theme = this.theme === 'dark' ? '' : this.theme;
      try {
        localStorage.setItem('theme', this.theme);
      } catch (_) { /* no-op */ }
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
      // Workstream search filters client-side via filteredWorkstreams.
      if (this.currentView !== 'workstreams') this.fetchBookmarks();
    },
    // --- Workstreams ---
    // Ordering lives in the activeWorkstreams/archivedWorkstreams computeds.
    replaceWorkstream(updated) {
      this.workstreams = this.workstreams.map((ws) => (ws.id === updated.id ? updated : ws));
    },
    async fetchWorkstreams() {
      this.workstreamsLoading = true;
      this.workstreamsError = null;
      try {
        this.workstreams = await listWorkstreams();
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to load workstreams.';
      } finally {
        this.workstreamsLoading = false;
      }
    },
    cancelAddWorkstream() {
      this.showAddWorkstream = false;
      this.newWorkstreamName = '';
    },
    async submitWorkstream() {
      const name = this.newWorkstreamName.trim();
      if (!name) return;
      this.workstreamsError = null;
      try {
        const created = await createWorkstream(name);
        this.workstreams = [created, ...this.workstreams];
        this.cancelAddWorkstream();
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to add workstream.';
      }
    },
    async toggleArchive(ws) {
      this.workstreamsError = null;
      try {
        const updated = await updateWorkstream(ws.id, { archived: !ws.archived_at });
        this.replaceWorkstream(updated);
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to update workstream.';
      }
    },
    async removeWorkstream(ws) {
      if (!window.confirm(`Delete workstream "${ws.name}" and all its comments and links?\n\nIf it just ran its course, use Archive instead.`)) return;
      this.workstreamsError = null;
      try {
        await deleteWorkstream(ws.id);
        this.workstreams = this.workstreams.filter((existing) => existing.id !== ws.id);
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to delete workstream.';
      }
    },
    async submitComment(ws) {
      const body = (this.commentDrafts[ws.id] || '').trim();
      if (!body) return;
      this.workstreamsError = null;
      try {
        const updated = await addWorkstreamComment(ws.id, body);
        this.replaceWorkstream(updated);
        this.commentDrafts[ws.id] = '';
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to add comment.';
      }
    },
    async removeComment(ws, commentId) {
      this.workstreamsError = null;
      try {
        const updated = await deleteWorkstreamComment(ws.id, commentId);
        this.replaceWorkstream(updated);
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to delete comment.';
      }
    },
    toggleLinks(workstreamId) {
      this.linksExpanded[workstreamId] = !this.linksExpanded[workstreamId];
    },
    toggleEditMode(workstreamId) {
      const enabled = !this.editMode[workstreamId];
      this.editMode[workstreamId] = enabled;
      // Expand links when entering edit mode so the add form is reachable;
      // close the category picker when leaving it.
      if (enabled) this.linksExpanded[workstreamId] = true;
      else this.categoryPickerOpen[workstreamId] = false;
    },
    async submitLink(ws) {
      const url = (this.linkUrlDrafts[ws.id] || '').trim();
      if (!url) return;
      this.workstreamsError = null;
      try {
        const updated = await addWorkstreamLink(ws.id, url, (this.linkTitleDrafts[ws.id] || '').trim() || null);
        this.replaceWorkstream(updated);
        this.linkUrlDrafts[ws.id] = '';
        this.linkTitleDrafts[ws.id] = '';
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to add link.';
      }
    },
    async removeLink(ws, linkId) {
      this.workstreamsError = null;
      try {
        const updated = await deleteWorkstreamLink(ws.id, linkId);
        this.replaceWorkstream(updated);
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to remove link.';
      }
    },
    // --- "Add to workstream" picker (opened from the context menu) ---
    async pickWorkstream(ws) {
      if (!this.workstreamPicker || this.pickerSaving) return;
      this.pickerSaving = true;
      this.pickerError = null;
      try {
        const updated = await addWorkstreamLink(
          ws.id,
          this.workstreamPicker.url,
          this.workstreamPicker.title || null,
        );
        this.replaceWorkstream(updated);
        this.closePickerAndReturn();
      } catch (e) {
        this.pickerError = e.message || 'Failed to add link.';
      } finally {
        this.pickerSaving = false;
      }
    },
    pickFirstWorkstream() {
      if (this.pickerWorkstreams.length > 0) this.pickWorkstream(this.pickerWorkstreams[0]);
    },
    cancelWorkstreamPicker() {
      this.closePickerAndReturn();
    },
    closePickerAndReturn() {
      const returnTabId = this.workstreamPicker?.returnTabId;
      this.workstreamPicker = null;
      this.pickerQuery = '';
      this.pickerError = null;
      // Focus the originating tab and close this one; if messaging is
      // unavailable (e.g. dev server) just close the modal.
      if (chrome?.runtime?.sendMessage) {
        chrome.runtime.sendMessage({ type: 'close-and-return', returnTabId }, () => {
          if (chrome.runtime.lastError) {
            // Tab close failed — the modal is already dismissed, nothing else to do.
          }
        });
      }
    },
    toggleCategoryFilter(categoryId) {
      const idx = this.categoryFilterIds.indexOf(categoryId);
      if (idx === -1) this.categoryFilterIds.push(categoryId);
      else this.categoryFilterIds.splice(idx, 1);
    },
    toggleCategoryPicker(workstreamId) {
      this.categoryPickerOpen[workstreamId] = !this.categoryPickerOpen[workstreamId];
    },
    async toggleWorkstreamCategory(ws, category) {
      const current = ws.categories.map((c) => c.id);
      const categoryIds = current.includes(category.id)
        ? current.filter((id) => id !== category.id)
        : [...current, category.id];
      this.workstreamsError = null;
      try {
        const updated = await updateWorkstream(ws.id, { category_ids: categoryIds });
        this.replaceWorkstream(updated);
      } catch (e) {
        this.workstreamsError = e.message || 'Failed to update categories.';
      }
    },
    // --- Workstream categories (managed from settings) ---
    async fetchCategories() {
      try {
        this.categories = await listCategories();
        this.categoryEdits = Object.fromEntries(this.categories.map((cat) => [cat.id, cat.name]));
        // Drop filter selections for categories that no longer exist.
        const ids = new Set(this.categories.map((cat) => cat.id));
        this.categoryFilterIds = this.categoryFilterIds.filter((id) => ids.has(id));
      } catch (e) {
        this.settingsError = e.message || 'Failed to load categories.';
      }
    },
    async submitCategory() {
      const name = this.newCategoryName.trim();
      if (!name) return;
      this.settingsError = null;
      try {
        await createCategory(name);
        this.newCategoryName = '';
        await this.fetchCategories();
      } catch (e) {
        this.settingsError = e.message || 'Failed to add category.';
      }
    },
    async renameCategory(category) {
      const name = (this.categoryEdits[category.id] || '').trim();
      if (!name || name === category.name) return;
      this.settingsError = null;
      try {
        await updateCategory(category.id, name);
        await Promise.all([this.fetchCategories(), this.fetchWorkstreams()]);
      } catch (e) {
        this.settingsError = e.message || 'Failed to rename category.';
      }
    },
    async removeCategory(category) {
      if (!window.confirm(`Delete category "${category.name}"? It will be removed from all workstreams.`)) return;
      this.settingsError = null;
      try {
        await deleteCategory(category.id);
        await Promise.all([this.fetchCategories(), this.fetchWorkstreams()]);
      } catch (e) {
        this.settingsError = e.message || 'Failed to delete category.';
      }
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
    this.applyTheme(storedTheme || 'dark');

    this.fetchBookmarks();
    this.fetchTodayEvents();
    this.fetchWorkstreams();
    this.fetchCategories();

    this.nowTickHandle = setInterval(() => { this.now = Date.now(); }, 30000);

    await this.loadSettings();
    if (this.featureFlags.jira) this.fetchJiraUpdates();
    if (this.featureFlags.jira) this.fetchJiraIncomplete();
    if (this.featureFlags.jira) this.fetchMyIssues();
    if (this.featureFlags.jira) this.fetchUnassignedIssues();
    if (this.featureFlags.github) this.fetchGithubPullRequests();
    if (!this.featureFlags.jira && !this.featureFlags.github && this.settingsLoaded) {
      this.currentView = 'settings';
    }

    // Check for "Add to workstream" from context menu
    const params = new URLSearchParams(window.location.search);
    if (params.get('addToWorkstream') === '1' && params.get('url')) {
      this.workstreamPicker = {
        url: params.get('url'),
        title: params.get('title') || '',
        returnTabId: params.get('returnTabId') || null,
      };
      this.currentView = 'workstreams';
      window.history.replaceState({}, '', window.location.pathname);
      this.$nextTick(() => this.$refs.pickerSearch?.focus());
    }

    // Check for prepopulated bookmark from context menu
    if (params.get('addBookmark') === '1') {
      this.newBookmarkUrl = params.get('url') || '';
      this.newBookmarkTitle = params.get('title') || '';
      this.showAddForm = true;
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  },
  beforeUnmount() {
    if (this.nowTickHandle) clearInterval(this.nowTickHandle);
  },
};
</script>
