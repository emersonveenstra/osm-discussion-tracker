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
const showFilterDropdown = ref(false)

const showWatchedCS = ref(true)
const showSnoozedCS = ref(false)
const showResolvedCS = ref(false)

const { result, loading, refetch, onResult, error } = useQuery(gql`
	query MyQuery($uid: Int!, $showWatched: Boolean!, $showSnoozed: Boolean!, $showResolved: Boolean!) {
		watchedChangesets(uid: $uid, showWatched: $showWatched, showSnoozed: $showSnoozed, showResolved: $showResolved) {
			csid
			lastActivityTs
			ts
			notices
			comment
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
		status: status_value,
		snoozeUntil: ''
	}
	if (status_value === 'snoozed') {
		const currentTime = new Date();
		//@ts-ignore
		const daysToSnooze = parseInt(document.getElementById('daysToSnooze')?.value ?? '0', 10);
		currentTime.setTime(currentTime.getTime() + (daysToSnooze * 86400 * 1000))
		data.snoozeUntil = currentTime.toISOString();
	}
	console.log(data)
	try {
		const response = await fetch("http://127.0.0.1:8000/status", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		});

		const result = await response.json();
		console.log("Success:", result);
		refetch();
		checkedCards.currentCheckedCards = [];
	} catch (error) {
		console.error("Error:", error);
	}
}
</script>

<template>
	<main>
		<section class="changeset-list">
			<div class="header" v-if="watched_changesets || loading">
				<p>
					<span>Your watched changesets</span>
					<span><button @click="refetch()"><font-awesome-icon icon="fa-solid fa-rotate-right" /></button></span>
				</p>
				<div class="filter-wrapper">
					<div class="filter">
						<span class="dropdown-toggle" @click="showFilterDropdown = !showFilterDropdown">Filter <font-awesome-icon icon="fa-solid fa-caret-down" /></span>
						<ul class="filter-options" v-if="showFilterDropdown">
							<li><label><input type="checkbox" name="watched" v-model="showWatchedCS" checked><span>Watched</span></label></li>
							<li><label><input type="checkbox" name="snoozed" v-model="showSnoozedCS"><span>Snoozed</span></label></li>
							<li><label><input type="checkbox" name="resolved" v-model="showResolvedCS"><span>Resolved</span></label></li>
						</ul>
					</div>
					<div class="mass-update" v-if="checkedCards.currentCheckedCards.length > 0">
						<span class="update-count">{{ checkedCards.currentCheckedCards.length }} selected</span>
						<select v-model="status">
							<option value="watched">Watch</option>
							<option value="resolved">Resolve</option>
							<option value="snoozed">Snooze</option>
							<option value="unwatched">Unwatch</option>
						</select>
						<span v-if="status == 'snoozed'">for <input id="daysToSnooze" type="number" value="3"> days</span>
						<button @click="updateChangesets(status)" :disabled="status === ''">Update</button>
					</div>
				</div>
			</div>

			<div class="loading" v-if="loading">
				<p>Loading changesets...</p>
			</div>
			<div class="error" v-else-if="error">
				<p>Error: unable to load changesets</p>
			</div>
			<div class="list" v-else-if="watched_changesets && !loading">
				<template v-for="changeset in watched_changesets.slice(listOffset, listOffset+20)"  :key="changeset.csid">
					<ChangesetCard
					:changeset-id="changeset.csid"
					:user-name="changeset.username"
					:notices="changeset.notices"
					:comment="changeset.comment"
					:last-activity="changeset.lastActivityTs"
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
		padding-top: 10px;
	}

	.changeset-list .header p {
		display: flex;
		justify-content: space-between;
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

	.dropdown-toggle {
		cursor: pointer;
	}

	.filter-wrapper {
		display: flex;
		justify-content: space-between;
	}

	.filter {
		position: relative;
	}
	.filter-options {
		position: absolute;
		top: 20px;
		left: 0;
		padding: 0;
		margin: 0;
		background-color: white;
	}

	.filter li {
		display: block;
		width: max-content;
		padding: 2px 5px;
	}

	.filter span {
		padding-left: 5px;
		display: inline-block;
	}
</style>