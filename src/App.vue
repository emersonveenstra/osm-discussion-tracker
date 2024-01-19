<script setup lang="ts">
import ChangesetList from './components/ChangesetList.vue'
</script>

<template>
	<main>
		<aside>
			<ChangesetList />
		</aside>
		<section class="view">
			<router-view></router-view>
		</section>
	</main>
</template>

<style scoped>
	main {
		display: flex;
		flex-flow: row nowrap;
		height: 100vh;
	}

	.view {
		flex: 1 1 100%;
		height: 100%;
		overflow: auto;
	}
	aside {
		height: 100%;
		overflow: auto;
		flex: 0 0 auto;
		width: 30%;
		max-width: 300px;
		display: flex;
		flex-flow: column;
	}
</style>