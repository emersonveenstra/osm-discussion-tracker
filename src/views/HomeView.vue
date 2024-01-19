<script setup lang="ts">
	import { useUserStore } from '@/stores/user';
	const userData = useUserStore();
	import HelpPage from '@/components/HelpPage.vue'
</script>
<template>
		<main class="home">
			<section class="header">
				<h1>OSM Discussion Tracker</h1>
			</section>
			<section class="login" v-if="userData.accessToken === ''">
				<a href='/login'>Please Login to OSM</a>
			</section>
			<section class="help">
				<HelpPage />
			</section>
		</main>
</template>

<style>

</style>