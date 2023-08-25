<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
defineProps<{
  changesetId: number,
  userName: string,
  hasResponse: boolean,
  lastActivity: string,
}>()

function viewDetails(csid: number) {
  changesetData.currentChangeset = csid
}
</script>

<template>
  <div class="changeset-card {% hasResponse ? 'has-response' : 'no-response' %}" @click="viewDetails(changesetId)">
	<span class="changeset-id">{{ changesetId }} by {{ userName }}</span>
  </div>
</template>

<style scoped>
  div span {
    display: block;
  }
</style>