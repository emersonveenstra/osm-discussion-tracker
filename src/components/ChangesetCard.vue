<script setup lang="ts">
import router from '@/router';
import { useCheckedCardsStore } from '@/stores/checkedCards';
const checkedCards = useCheckedCardsStore();
defineProps<{
	changesetId: number,
	userName: string,
	notices: string[],
	comment: string,
	lastActivity: string,
	status: string
}>()

function viewDetails(csid: number) {
	router.push(`/changeset/${csid}`)
}

</script>

<template>
	<div class="changeset-card" :class="{isCurrentChangeset: (parseInt($route.params.changeset, 10) == changesetId) }">
		<span class="check">
			<input type="checkbox" :value="changesetId" v-model="checkedCards.currentCheckedCards">
		</span>
		<a class="info" :href="`/changeset/${changesetId}`" @click.stop.prevent="viewDetails(changesetId)">
			<span class="changeset-creator">{{ userName }}</span>
			<span class="changeset-comment">{{ comment }}</span>
			<ul class="changeset-notices" v-for="notice in notices" :key="notice.toLocaleLowerCase().replace(' ', '-')">
				<li class="notice" :class="notice.toLocaleLowerCase().replace(' ', '-')">{{ notice }}</li>
			</ul>
			<span class="changeset-id">{{ changesetId }}</span>
		</a>
		<span class="icon">
			<font-awesome-icon v-if="status == 'resolved'" :icon="['far', 'square-check']" />
			<font-awesome-icon v-else-if="status == 'snoozed'" :icon="['far', 'hourglass-half']" />
			<font-awesome-icon v-else-if="status == 'watched'" :icon="['far', 'bell']" />
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
		text-decoration: none;
		color: inherit;
		padding-top: 4px;
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

	.changeset-notices {
		list-style: none;
		padding: 0;
		margin-bottom: 10px;
	}

	.changeset-notices li {
		background: lightblue;
		border-radius: 5px;
		font-size: 12px;
		display: inline-block;
		padding: 2px 5px;
	}
</style>