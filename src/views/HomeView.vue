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
query MyQuery($uid: Int!, $limit: Int!, $offset: Int!) {
  watchedChangesets(uid: $uid, limit: $limit, offset: $offset) {
    csid
	lastActivity
    ts
    hasResponse
	hasNewChangesets
    username
  }
}`, {
    uid: userData.userID,
    limit: 20,
    offset: computed(() => listOffset.value),
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

function loadNextPage(newOffset: number) {
  listOffset.value = newOffset;
  console.log(listOffset.value)
}
</script>

<template>
  <main>
    <section class="changeset-list">
      <p>Your watched changesets</p>
      <template v-for="changeset in watched_changesets"  :key="changeset.csid">
        <ChangesetCard
        :changeset-id="changeset.csid"
        :user-name="changeset.username"
        :has-response="changeset.hasResponse"
        :has-new-changesets="changeset.hasNewChangesets"
        :last-activity="changeset.lastActivity"
      />
      </template>
      <div class="pagination">
        <button class="next" @click="loadNextPage(listOffset-1)" v-if="listOffset != 0">Prev</button>
        <button class="next" @click="loadNextPage(listOffset+1)">Next</button>
      </div>
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