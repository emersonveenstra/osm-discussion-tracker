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
    username
  }
}`, {
    uid: 9490212,
  })

const watched_changesets = computed(() => result.value?.watchedChangesets)

</script>

<template>
	<section class="changeset-list">
		<p>Your watched changesets</p>
		<ChangesetCard v-for="changeset in watched_changesets" :key="changeset.csid"
			:changeset-id="changeset.csid"
			:user-name="changeset.username"
			:has-response="changeset.hasResponse"
			:last-activity="changeset.lastActivity"
		/>
	</section>
</template>