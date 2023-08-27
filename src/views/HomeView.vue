<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import ChangesetList from '../components/ChangesetList.vue'
import ChangesetDetail from '../components/ChangesetDetail.vue'

</script>

<template>
  <main>
    <ChangesetList />
    <ChangesetDetail v-if="changesetData.currentChangeset !== 0"/>
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