<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useCheckedCardsStore } from '@/stores/checkedCards';
const checkedCards = useCheckedCardsStore();
defineProps<{
	changesetId: number,
	userName: string,
	hasResponse: boolean,
	lastActivity: string,
	changesetComment: string,
	status: string
}>()

function viewDetails(csid: number) {
	changesetData.currentChangeset = csid
	window.location.hash = `#${csid}`
}

</script>

<template>
	<div class="changeset-card" :class="{ hasResponse: (hasResponse && status == 'watching'), isCurrentChangeset: (changesetData.currentChangeset == changesetId) }">
		<span class="check">
			<input type="checkbox" :value="changesetId" v-model="checkedCards.currentCheckedCards">
		</span>
		<div class="info" @click="viewDetails(changesetId)">
			<span class="changeset-creator">{{ userName }}</span>
			<span class="changeset-comment">{{ changesetComment }}</span>
			<ul class="changeset-flags">
				<li class="flag needs-reply" v-if="hasResponse">Needs response</li>
			</ul>
			<span class="changeset-id">{{ changesetId }}</span>
		</div>
		<span class="icon">
			<font-awesome-icon v-if="status == 'resolved'" :icon="['far', 'square-check']" />
			<font-awesome-icon v-else-if="status === 'snoozed'" :icon="['far', 'hourglass-half']" />
			<font-awesome-icon v-else :icon="['far', 'bell']" />
		</span>
	</div>
</template>

<style scoped>
	.changeset-card {
		border-bottom: 1px solid black;
		cursor: pointer;
		display: flex;
		flex-flow: row nowrap;
		align-items: center;
	}
	.changeset-card span {
		font-size: 12px;
		display: block;
		padding-bottom: 4px;
	}
	.check {
		padding: 0 8px;
		flex: 0 0 auto;
	}
	.info {
		flex: 1 1 100%;
	}

	.icon {
		padding: 0 8px;
	}
	.changeset-creator {
		font-weight: bold;
	}

	.hasNewChangesets {
		color: rgb(212, 212, 18);
	}

	.hasResponse {
		color: green;
	}

	.isCurrentChangeset {
		background-color: gray;
	}
</style>