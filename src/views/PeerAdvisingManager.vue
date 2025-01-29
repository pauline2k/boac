<template>
  <div>
    Peer Advising Manager
    <pre>
      {{ peerAdvisors }}
    </pre>
  </div>
</template>

<script setup>
import {getPeerAdvisingDepartment} from '@/api/peer-advising'
import {onMounted, ref} from 'vue'
import {toInt} from '@/lib/utils'
import {useRoute} from 'vue-router'

const peerAdvisors = ref([])

onMounted(() => {
  const peerAdvisingDeptId = toInt(useRoute().params.id)
  getPeerAdvisingDepartment(peerAdvisingDeptId).then(data => {
    peerAdvisors.value = data
  })
})
</script>
