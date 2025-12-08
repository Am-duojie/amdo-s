<template>
  <div />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
  const { pathMatch } = route.params
  const redirectPath = Array.isArray(pathMatch) ? pathMatch.join('/') : pathMatch
  if (redirectPath) {
    router.replace('/' + redirectPath)
  } else {
    router.replace('/')
  }
})
</script>

