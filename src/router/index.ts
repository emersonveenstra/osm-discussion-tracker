import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ChangesetView from '@/views/ChangesetView.vue'
import UserView from '@/views/UserView.vue'
import HelpView from '@/views/HelpView.vue'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'home',
			component: HomeView
		},
		{
			path: '/changeset/:changeset?',
			name: 'changeset',
			component: ChangesetView,
			strict: true
		},
		{
			path: '/user/:username?',
			name: 'user',
			component: UserView,
			strict: true
		},
		{
			path: '/help',
			name: 'help',
			component: HelpView,
		}
	]
})

export default router
