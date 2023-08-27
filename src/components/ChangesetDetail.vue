<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed, ref } from 'vue'

const { result, loading, error, refetch } = useQuery(gql`
query MyQuery($csid: Int!) {
  getChangesetDetails(csid: $csid) {
    csid
    uid
    username
    ts
    comment
    discussion {
      username
      ts
      comment
    }
  }
}`, () => ({
    csid: changesetData.currentChangeset,
    }))

const changeset_details = computed(() => result.value?.getChangesetDetails ?? false)

function resolveChangeset() {
  
}

</script>

<template>
  <div :v-if="changeset_details" class="changeset-detail">
    <h1>Changeset {{ changesetData.currentChangeset }}</h1>
    <span>by {{ changeset_details.username }} on {{ changeset_details.ts }}</span>
    <section class="discussion"> 
      <h2>Discussion</h2>
      <div v-for="comment in changeset_details['discussion']" :key="comment['ts']">
        <span class="username">{{ comment.username }} at {{ comment.ts }} said:</span>
        <p>{{ comment.comment }}</p>
      </div>
      <p>Add comment to changeset:</p>
      <textarea></textarea>
    </section>
    <section class="changeset-viewer">
    </section>
    <section class="buttons">
      <button @click="resolveChangeset">Resolve changeset</button>
    </section>
  </div>
</template>