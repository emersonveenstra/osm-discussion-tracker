<script setup lang="ts">
import ChangesetList from './components/ChangesetList.vue'
</script>

<template>
	<p>ODT is being sunset at the end of February. See the <a href="https://github.com/emersonveenstra/osm-discussion-tracker/issues/36">Github issue</a> for more information</p>
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
	p {
		display: block;
		width: 100%;
		background: orange;
		text-align: center;
	}
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