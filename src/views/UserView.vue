<script setup lang="ts">
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
	async function hideUserModal() {
		userData.userModalID = 0
	}
</script>
<template>
	<section>hi</section>
	<button @click="hideUserModal">Close</button>
</template>