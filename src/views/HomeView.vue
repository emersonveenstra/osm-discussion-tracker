<script setup lang="ts">
import ChangesetList from '../components/ChangesetList.vue'
import ChangesetDetail from '../components/ChangesetDetail.vue'

</script>

<template>
  <main>
    <ChangesetList />
    <ChangesetDetail />
  </main>
</template>

<style scoped>
  main {
    display: flex;
    flex-flow: row nowrap;
  }
  .changeset-list {
    flex: 0 0 auto;
  }

  .changeset-detail {
    flex: 1 1 100%;
  }
</style>