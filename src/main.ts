import './assets/base.css'

import { createApp, provide, h } from 'vue'
import { DefaultApolloClient } from '@vue/apollo-composable'
import { apolloClient } from '@/apollo-client'
import { createPinia } from 'pinia'

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faBell, faSquareCheck, faHourglassHalf } from '@fortawesome/free-regular-svg-icons'
import { faCaretDown, faRotateRight } from '@fortawesome/free-solid-svg-icons'
library.add(faBell, faSquareCheck, faHourglassHalf, faCaretDown, faRotateRight)

import App from './App.vue'
import router from './router'

const app = createApp({
	setup () {
		provide(DefaultApolloClient, apolloClient)
	},
	
	render: () => h(App),
})

app.use(createPinia())
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')
