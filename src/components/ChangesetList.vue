<script setup lang="ts">
import ChangesetCard from './ChangesetCard.vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed } from 'vue'

const { result, loading, error, refetch } = useQuery(gql`
query MyQuery($uid: Int!) {
  watchedChangesets(uid: $uid) {
    csid
	lastActivity
    ts
    hasResponse
	hasNewChangesets
    username
  }
}`, {
    uid: 11548585,
  })

const watched_changesets = computed(() => result.value?.watchedChangesets)

</script>

<template>
	<section class="changeset-list">
		<p>Your watched changesets</p>
		<template v-for="changeset in watched_changesets"  :key="changeset.csid">
			<ChangesetCard v-if="changeset.hasResponse"
			:changeset-id="changeset.csid"
			:user-name="changeset.username"
			:has-response="changeset.hasResponse"
			:has-new-changesets="changeset.hasNewChangesets"
			:last-activity="changeset.lastActivity"
		/>
		</template>
		<template v-for="changeset in watched_changesets"  :key="changeset.csid">
			<ChangesetCard v-if="changeset.hasNewChangesets && !changeset.hasResponse"
			:changeset-id="changeset.csid"
			:user-name="changeset.username"
			:has-response="changeset.hasResponse"
			:has-new-changesets="changeset.hasNewChangesets"
			:last-activity="changeset.lastActivity"
		/>
		</template>
		<template v-for="changeset in watched_changesets"  :key="changeset.csid">
			<ChangesetCard v-if="!changeset.hasResponse && !changeset.hasNewChangesets"
			:changeset-id="changeset.csid"
			:user-name="changeset.username"
			:has-response="changeset.hasResponse"
			:has-new-changesets="changeset.hasNewChangesets"
			:last-activity="changeset.lastActivity"
		/>
		</template>
	</section>
</template>

<style scoped>
	.changeset-list {
		flex: 0 0 auto;
	}
	p {
		padding: 10px;
		border-bottom: 1px solid black;
	}
</style>