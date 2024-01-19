<script setup lang="ts">
	import { useUserStore } from '@/stores/user';
	import { ref } from 'vue';
	const userData = useUserStore();
	import router from '@/router';

	const isLoggingIn = ref(false);

	function startAuth() {
		userData.auth.fetch('https://www.openstreetmap.org/api/0.6/user/details.json')
	}
	if (window.location.search.slice(1).split('&').some(p => p.startsWith('code='))) {
		userData.auth.authenticate(function() {
			isLoggingIn.value = true;
			setTimeout(() => {
				userData.getAuthDetails()
				router.push(`/`)
			}, 4000);
		});
	}
</script>
<template>
	<section>
		<h1>Login</h1>
	</section>
	<section class="login">
		<button v-if="userData.accessToken === '' && !isLoggingIn" @click="startAuth" class="trigger-login">Authorize with OSM</button>
		<p v-else-if="userData.accessToken === '' && isLoggingIn">Logging in...</p>
	</section>
</template>

<style>

</style>