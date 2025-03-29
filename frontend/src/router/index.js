import { createRouter, createWebHistory } from 'vue-router'
import DatasetView from '../views/DatasetView.vue'
import IndexView from '../views/IndexView.vue'
import ConfigView from '../views/ConfigView.vue'
import VectorSearchView from '../views/VectorSearchView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'index',
            component: IndexView
        },
        {
            path: '/dataset',
            name: 'dataset',
            component: DatasetView
        },
        {
            path: '/vector-search',
            name: 'vectorSearch',
            component: VectorSearchView
        },
        {
            path: '/config',
            name: 'config',
            component: ConfigView
        }
    ]
})

export default router