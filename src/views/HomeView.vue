<script setup lang="ts">
	import { useUserStore } from '@/stores/user';
	const userData = useUserStore();
	import HelpPage from '@/components/HelpPage.vue'
</script>
<template>
		<div class="home">
			<div class="header">
				<h1>OSM Discussion Tracker</h1>
			</div>
			<section class="help">
				<HelpPage />
			</section>
		</div>
</template>

<style>
	.home {
		display: flex;
		flex-direction: column;
		padding: 10px 20px;
		height: 100%;
	}

	.login {
		flex: 1 1 100%;
		justify-content: center;
		align-items: center;
		display: flex;
	}

	h1 {
		margin: 10px 0;
	}
</style>