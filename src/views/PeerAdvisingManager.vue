<template>
  <div v-if="!loading" class="bg-sky-blue">
    <div class="pb-2 pt-4 px-4">
      <h1 id="page-header" class="mr-2">Peer Advising Management Dashboard</h1>
    </div>
    <v-tabs
      v-model="tab"
      aria-label="Peer Advising Management tab"
      :aria-orientation="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      class="ml-3"
      density="comfortable"
      :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      :items="tabs"
      mobile-breakpoint="md"
    >
      <template #tab="{item}">
        <v-tab
          :id="`peer-advising-management-tab-${item.key}s`"
          :aria-controls="`peer-advising-management-tab-panel-${item.key}s`"
          class="border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
          :class="{
            'bg-white border-b-0': item.key === tab,
            'bg-grey-lighten-4 border-b-md': item.key !== tab
          }"
          hide-slider
          min-width="120"
          :value="item.key"
          variant="text"
        >
          <template #default>
            <div class="font-size-12 font-weight-bold">
              <div
                :id="`peer-advising-management-count-${item.key}s`"
                class="text-uppercase"
                :class="{'text-primary': item.key === tab, 'text-black': item.key !== tab}"
                v-html="item.label"
              />
            </div>
          </template>
        </v-tab>
      </template>
      <template #item="{item}">
        <v-tabs-window-item
          :id="`peer-advising-management-tab-panel-${item.key}s`"
          :aria-labelledby="`peer-advising-management-tab-${item.key}s`"
          :aria-selected="item.key === tab"
          class="bg-white px-4"
          role="tabpanel"
          :value="item.key"
        >
          <div class="pt-3">
            <h2 class="font-size-16">{{ item.label }}</h2>
          </div>
          <div v-if="item.key === 'account'">
            <div class="align-center d-flex justify-space-between font-weight-bold">
              <div class="w-40">
                <PeerAdvisingAddStudent />
              </div>
              <div class="mr-3">
                <v-switch
                  id="toggle-inactive-students-button"
                  v-model="showInactiveStudents"
                  aria-label="Show Only My Notes"
                  color="primary"
                  density="compact"
                  hide-details
                  :label="`${showInactiveStudents ? 'Hide' : 'Show'} inactive students`"
                  role="switch"
                />
                <span aria-live="polite" class="sr-only">Showing {{ showInactiveStudents ? 'all students' : 'active students' }}</span>
              </div>
            </div>
            <div class="border-b-sm mt-6">
              <v-data-table
                density="compact"
                fixed-header
                :headers="headers"
                :header-props="{class: 'data-table-header-cell'}"
                hide-default-footer
                hide-no-data
                hover
                :items="peerAdvisingDepartment.members"
                :items-per-page="-1"
                mobile-breakpoint="md"
                :row-props="row => ({id: `row-topic-${normalizeId(row.item.topic)}`})"
              >
                <template #item.notesCreatedCount="{item}">
                  <div class="float-right" :class="{'font-weight-medium text-red': item.deletedAt}">
                    {{ item.notesCreatedCount }}
                  </div>
                </template>
                <template #item.actions="{item}">
                  <v-tooltip text="Delete">
                    <template #activator="{props}">
                      <v-btn
                        v-if="!item.deletedAt"
                        v-bind="props"
                        :id="`delete-topic-${normalizeId(item.topic)}`"
                        :aria-label="`Delete ${item.topic}`"
                        color="primary"
                        density="compact"
                        text="Remove"
                        variant="text"
                        @click="deletePeerAdvisor(item)"
                      />
                    </template>
                  </v-tooltip>
                  <v-tooltip text="Undelete">
                    <template #activator="{props}">
                      <v-btn
                        v-if="item.deletedAt"
                        v-bind="props"
                        :id="`undelete-topic-${normalizeId(item.topic)}`"
                        :aria-label="`Un-delete ${item.topic}`"
                        color="warning"
                        density="compact"
                        text="Restore"
                        variant="plain"
                        @click="undelete(item)"
                      />
                    </template>
                  </v-tooltip>
                </template>
              </v-data-table>
            </div>
          </div>
          <div v-if="item.key === 'templates'">
            BBB
          </div>
          <div v-if="item.key === 'reporting'">
            CCC
          </div>
        </v-tabs-window-item>
      </template>
    </v-tabs>
  </div>
</template>

<script setup>
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import {computed, onMounted, ref} from 'vue'
import {getPeerAdvisingDepartment} from '@/api/peer-advising'
import {alertScreenReader, normalizeId, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()

const headers = [
  {align: 'start', key: 'name', title: 'Topic', width: '60%'},
  {align: 'end', key: 'notesCreatedCount', title: 'Notes Created'},
  {align: 'end', key: 'createdAt', title: 'Date Added'},
  {align: 'end', key: 'actions', title: 'Actions', sortable: false},
]
const loading = computed(() => contextStore.loading)
const peerAdvisingDepartment = ref([])
const showInactiveStudents = ref(false)
const tab = ref(undefined)
const tabs = [
  {key: 'account', label: 'Account Management'},
  {key: 'templates', label: 'Note Templates'},
  {key: 'reporting', label: 'Reporting & Statistics'},
]

contextStore.loadingStart()

onMounted(() => {
  const peerAdvisingDeptId = toInt(useRoute().params.id)
  getPeerAdvisingDepartment(peerAdvisingDeptId).then(data => {
    peerAdvisingDepartment.value = data
    contextStore.loadingComplete('Peer Advising Management Dashboard is ready.')
  })
})

const deletePeerAdvisor = member => {
  alertScreenReader(member)
}

const undelete = member => {
  alertScreenReader(member)
}
</script>
