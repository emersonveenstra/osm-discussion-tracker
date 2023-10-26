<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
import ChangesetDetail from '../components/ChangesetDetail.vue'

import ChangesetCard from '../components/ChangesetCard.vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed } from 'vue'
import { Changeset } from '@/classes/Changeset';

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
}`, {
    uid: userData.userID,
  })

const watched_changesets = computed(() => result.value?.watchedChangesets)

onResult(queryResult => {
  console.log(queryResult)
  if (queryResult.loading)
    return;
  for (const changeset of watched_changesets.value) {
    console.log(changeset)
    if (!changesetData.watchedChangesets.has(changeset.csid))
      changesetData.watchedChangesets.set(changeset.csid, new Changeset(changeset.csid, changeset.username, changeset.ts, changeset.hasResponse, changeset.hasNewChangesets))
  }
})
</script>

<template>
  <main>
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
    <ChangesetDetail v-if="changesetData.currentChangeset !== 0" />
  </main>
</template>

<style scoped>
  main {
    display: flex;
    flex-flow: row nowrap;
  }

  .changeset-detail {
    flex: 1 1 100%;
  }
</style>