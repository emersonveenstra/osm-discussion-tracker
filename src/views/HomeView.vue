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

const { result, loading, error, refetch, onResult } = useQuery(gql`
	query MyQuery($uid: Int!) {
		watchedChangesets(uid: $uid) {
			csid
			lastActivity
			ts
			hasResponse
			hasNewChangesets
			username
		}
	}`,
	{
		uid: userData.userID
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
		console.log(changeset)
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
		<section class="changeset-list" v-if="watched_changesets">
			<p>Your watched changesets</p>
			<template v-for="changeset in watched_changesets.slice(listOffset, listOffset+20)"  :key="changeset.csid">
				<ChangesetCard
				:changeset-id="changeset.csid"
				:user-name="changeset.username"
				:has-response="changeset.hasResponse"
				:has-new-changesets="changeset.hasNewChangesets"
				:last-activity="changeset.lastActivity"
			/>
			</template>
			<div class="pagination">
				<button class="next" @click="loadNextPage(listOffset-20)" v-if="listOffset != 0">Prev</button>
				<button class="next" @click="loadNextPage(listOffset+20)">Next</button>
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
	}
	.changeset-list {
		height: 100%;
		overflow: auto;
		flex: 0 0 auto;
	}
</style>