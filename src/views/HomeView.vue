<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
import ChangesetDetail from '../components/ChangesetDetail.vue'

import ChangesetCard from '../components/ChangesetCard.vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed, ref } from 'vue'
import { Changeset } from '@/classes/Changeset';

const listOffset = ref(0)
const csFilter = ref('w')

const showWatchedCS = ref(true)
const showSnoozedCS = ref(false)
const showResolvedCS = ref(false)

const { result, loading, error, refetch, onResult } = useQuery(gql`
	query MyQuery($uid: Int!, $showWatched: Boolean!, $showSnoozed: Boolean!, $showResolved: Boolean!) {
		watchedChangesets(uid: $uid, showWatched: $showWatched, showSnoozed: $showSnoozed, showResolved: $showResolved) {
			csid
			lastActivity
			ts
			comment
			hasResponse
			hasNewChangesets
			username
			status
		}
	}`,
	{
		uid: userData.userID,
		showWatched: showWatchedCS,
		showSnoozed: showSnoozedCS,
		showResolved: showResolvedCS
	}
)

if (window.location.hash !== '') {
	changesetData.currentChangeset = parseInt(window.location.hash.slice(1), 10)
}

const watched_changesets = computed(() => result.value?.watchedChangesets)

onResult(queryResult => {
	if (queryResult.loading)
		return;
	for (const changeset of watched_changesets.value) {
		if (!changesetData.watchedChangesets.has(changeset.csid))
			changesetData.watchedChangesets.set(changeset.csid, new Changeset(changeset.csid, changeset.username, changeset.ts, changeset.hasResponse, changeset.hasNewChangesets))
	}
})

function loadNextPage(newOffset: number) {
	listOffset.value = newOffset;
}
</script>

<template>
	<main>
		<section class="changeset-list">
			<div class="header" v-if="watched_changesets">
				<p>Your watched changesets</p>
				<span>{{ watched_changesets.length }} changesets <button @click="refetch()">Refresh list</button></span>
				<div class="filter-wrapper">
					<button>Filter</button>
					<div class="filter-options">
						<label>Watched<input type="checkbox" name="watched" v-model="showWatchedCS" checked></label>
						<label>Snoozed<input type="checkbox" name="snoozed" v-model="showSnoozedCS"></label>
						<label>Resolved<input type="checkbox" name="resolved" v-model="showResolvedCS"></label>
					</div>
				</div>
			</div>

			<div class="list" v-if="watched_changesets">
				<template v-for="changeset in watched_changesets.slice(listOffset, listOffset+20)"  :key="changeset.csid">
					<ChangesetCard
					:changeset-id="changeset.csid"
					:changeset-comment="changeset.comment"
					:user-name="changeset.username"
					:has-response="changeset.hasResponse"
					:has-new-changesets="changeset.hasNewChangesets"
					:last-activity="changeset.lastActivity"
					:status="changeset.status"
				/>
				</template>
			</div>
			<div class="pagination" v-if="watched_changesets">
				<button class="prev" @click="loadNextPage(listOffset-20)" v-if="listOffset != 0">Prev</button>
				<button class="next" @click="loadNextPage(listOffset+20)" v-if="(listOffset+20) < watched_changesets.length">Next</button>
			</div>
		</section>
		<ChangesetDetail v-if="changesetData.currentChangeset !== 0" />
	</main>
</template>

<style scoped>
	main {
		display: flex;
		flex-flow: row nowrap;
		height: 100vh;
	}

	.changeset-detail {
		flex: 1 1 100%;
		height: 100%;
		overflow: auto;
	}
	.changeset-list {
		height: 100%;
		overflow: auto;
		flex: 0 0 auto;
		width: 300px;
	}
</style>