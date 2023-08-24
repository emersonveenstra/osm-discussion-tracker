<script setup lang="ts">
import ChangesetCard from './ChangesetCard.vue'
</script>

<template>
	<section class="changeset-list">
		<ChangesetCard
			changeset-id="123455"
			user-name="emerson"
			has-response="false"
			num-changesets-after="0"
		/>
		<ChangesetCard
			changeset-id="123456"
			user-name="emerson"
			has-response="true"
			num-changesets-after="0"
		/>
		<ChangesetCard
			changeset-id="123457"
			user-name="emerson2"
			has-response="false"
			num-changesets-after="5"
		/>
		<ChangesetCard
			changeset-id="123458"
			user-name="emerson4"
			has-response="true"
			num-changesets-after="6"
		/>
	</section>
</template>