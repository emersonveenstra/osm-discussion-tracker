<script setup lang="ts">
import { useUserStore } from '@/stores/user';
const userData = useUserStore();

import ChangesetCard from '../components/ChangesetCard.vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed, ref } from 'vue'
import { useCheckedCardsStore } from '@/stores/checkedCards';
const checkedCards = useCheckedCardsStore();

const listOffset = ref(0)
const status = ref('')

const showWatchedCS = ref(true)
const showSnoozedCS = ref(false)
const showResolvedCS = ref(false)

const { result, loading, refetch, onResult } = useQuery(gql`
	query MyQuery($uid: Int!, $showWatched: Boolean!, $showSnoozed: Boolean!, $showResolved: Boolean!) {
		watchedChangesets(uid: $uid, showWatched: $showWatched, showSnoozed: $showSnoozed, showResolved: $showResolved) {
			csid
			lastActivity
			ts
			comment
			hasResponse
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

const watched_changesets = computed(() => result.value?.watchedChangesets)

onResult(queryResult => {
	if (queryResult.loading)
		return;
})

function loadNextPage(newOffset: number) {
	listOffset.value = newOffset;
}

async function updateChangesets(status_value: string) {
	const data = {
		uid: userData.userID,
		csid: [...checkedCards.currentCheckedCards],
		status: 'resolve',
		snoozeUntil: ''
	}
	let url = `http://127.0.0.1:8000/${status_value}`;
	if (status_value === 'snooze') {
		const currentTime = new Date();
		// @ts-ignore
		const daysToSnooze = parseInt(document.getElementById('daysToSnooze')?.value ?? '0', 10);
		currentTime.setTime(currentTime.getTime() + (daysToSnooze * 86400 * 1000))
		data.snoozeUntil = currentTime.toISOString();
		data.status = 'snooze'
		url = "http://127.0.0.1:8000/resolve"
	}
	console.log(data)
	try {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		});

		const result = await response.json();
		console.log("Success:", result);
		refetch()
		checkedCards.currentCheckedCards = []
	} catch (error) {
		console.error("Error:", error);
	}
}
</script>

<template>
	<main>
		<section class="changeset-list">
			<div class="header" v-if="watched_changesets || loading">
				<p>Your watched changesets</p>
				<span><button @click="refetch()">Refresh list</button></span>
				<div class="filter-wrapper">
					<button>Filter</button>
					<div class="filter-options">
						<label>Watched<input type="checkbox" name="watched" v-model="showWatchedCS" checked></label>
						<label>Snoozed<input type="checkbox" name="snoozed" v-model="showSnoozedCS"></label>
						<label>Resolved<input type="checkbox" name="resolved" v-model="showResolvedCS"></label>
					</div>
				</div>
				<span v-if="watched_changesets && !loading">{{ watched_changesets.length }} changesets</span>
				<div class="mass-update" v-if="checkedCards.currentCheckedCards.length > 0">
					<select v-model="status">
					<option value="unresolve">Watch</option>
					<option value="resolve">Resolve</option>
					<option value="snooze">Snooze</option>
					</select>
					<span v-if="status == 'snooze'">for <input id="daysToSnooze" type="number" value="3"> days</span>
					<button @click="updateChangesets(status)" :disabled="status === ''">Update</button>
				</div>
			</div>

			<div class="loading" v-if="loading">
				<p>Loading changesets...</p>
			</div>
			<div class="list" v-if="watched_changesets && !loading">
				<template v-for="changeset in watched_changesets.slice(listOffset, listOffset+20)"  :key="changeset.csid">
					<ChangesetCard
					:changeset-id="changeset.csid"
					:changeset-comment="changeset.comment"
					:user-name="changeset.username"
					:has-response="changeset.hasResponse"
					:last-activity="changeset.lastActivity"
					:status="changeset.status"
				/>
				</template>
			</div>
			<div class="pagination" v-if="watched_changesets">
				<button class="prev" @click="loadNextPage(listOffset-20)" v-if="listOffset != 0">Prev</button>
				<template v-for="num in Math.ceil(watched_changesets.length / 20)" :key="num">
					<button @click="loadNextPage((num-1)*20)" class="page">{{ num }}</button>
				</template>
				<button class="next" @click="loadNextPage(listOffset+20)" v-if="(listOffset+20) < watched_changesets.length">Next</button>
			</div>
		</section>
	</main>
</template>

<style scoped>
	.changeset-list {
		height: 100%;
		overflow: auto;
		flex: 0 0 auto;
		width: 300px;
		display: flex;
		flex-flow: column;
	}

	.changeset-list .header {
		flex: 0 0 auto;
	}

	.changeset-list .list, .changeset-list .loading {
		flex: 1 1 100%;
		overflow: auto;
	}

	.changeset-list .loading {
		display: flex;
		align-items: center;
		justify-content: center;
	}
</style>