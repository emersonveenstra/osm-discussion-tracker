<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
defineProps<{
  changesetId: number,
  userName: string,
  hasResponse: boolean,
  lastActivity: string,
  hasNewChangesets: boolean,
}>()

function viewDetails(csid: number) {
  changesetData.currentChangeset = csid
}
</script>

<template>
  <div class="changeset-card" :class="{ hasResponse: hasResponse, hasNewChangesets: hasNewChangesets }" @click="viewDetails(changesetId)">
    <span class="changeset-id">{{ changesetId }}</span>
    <span class="changeset-creator">by {{ userName }}</span>
    <span v-if="hasResponse">User has new comment for you!</span>
    <span v-else-if="hasNewChangesets">User has made changesets after this comment</span>
  </div>
</template>

<style scoped>
  div {
    border-bottom: 1px solid black;
    padding: 10px;
    cursor: pointer;
  }
  div span {
    display: block;
    font-size: 14px;
  }
  .changeset-id {
    font-weight: bold;
  }

  .hasNewChangesets {
    color: rgb(212, 212, 18);
  }

  .hasResponse {
    color: green;
  }
</style>