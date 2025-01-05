<template>
  <div v-if="!loading" class="default-margins">
    <div class="align-center d-flex">
      <h1 id="page-header">Everyone's {{ modeLabel }}s</h1>
      <div class="align-center d-flex font-size-13 mb-1 ml-1">
        <v-btn
          v-if="countExpandedDepartments"
          id="collapse-all-departments"
          color="primary"
          slim
          variant="text"
          @click="collapseAllDepartments"
        >
          Collapse all<span class="sr-only"> department panels</span>
        </v-btn>
        <div v-if="countExpandedDepartments && countExpandedDepartments < departments.length" class="mb-1">|</div>
        <v-btn
          v-if="countExpandedDepartments < departments.length"
          id="collapse-all-departments"
          color="primary"
          slim
          variant="text"
          @click="expandAllDepartments"
        >
          Expand all
        </v-btn>
      </div>
    </div>
    <div v-if="currentUser.canAccessAdmittedStudents" class="pl-1">
      <v-icon class="mr-1 vertical-bottom" color="warning" :icon="mdiStar" />
      <span class="sr-only">Star icon</span>denotes a {{ modeLabel }} of admitted students.
    </div>
    <v-expansion-panels
      v-model="panels"
      class="mt-1"
      flat
      multiple
    >
      <template
        v-for="department in departments"
        :key="department.id"
      >
        <v-expansion-panel
          :id="`department-${department.id}`"
          :bg-color="department.isOpen ? 'pale-blue' : 'transparent'"
          class="sortable-group"
          :class="department.isOpen ? 'border-1 pb-8' : 'border-0'"
          hide-actions
          rounded
          :value="department.code"
          @group:selected="open => onClickExpansionPanel(department, open)"
        >
          <v-expansion-panel-title
            :id="`department-${department.id}-expansion-panel`"
            class="bg-transparent pl-2 py-1 w-100"
            hide-actions
          >
            <template #default="{expanded}">
              <div class="d-flex justify-space-between w-100">
                <div class="align-center d-flex">
                  <div class="expand-icon-container">
                    <v-progress-circular
                      v-if="department.isFetching"
                      color="primary"
                      indeterminate
                      size="x-small"
                      width="2"
                    />
                    <v-icon
                      v-if="!department.isFetching"
                      color="primary"
                      :icon="expanded ? mdiMenuDown : mdiMenuRight"
                      size="large"
                    />
                  </div>
                  <h3 class="page-section-header-sub pr-8 text-primary">
                    <span class="sr-only">{{ `${department.isOpen ? 'Hide' : 'Show'} details for ${department.name} ` }}</span>
                    {{ department.name }}
                  </h3>
                </div>
              </div>
            </template>
          </v-expansion-panel-title>
          <v-expansion-panel-text :id="`department-${department.id}-details`" class="bg-transparent">
            <div
              v-for="(user, index) in department.users"
              :key="index"
              class="ml-14"
              :class="{'mt-3': index > 0}"
            >
              <h2 :id="`${mode}-list-${index}-heading`" class="font-size-14">
                <span class="sr-only">{{ modeLabel }}s of</span>
                <span v-if="user.name">{{ user.name }}</span>
                <span v-if="!user.name">UID: {{ user.uid }}</span>
              </h2>
              <ul :aria-labelledby="`${mode}-list-${index}-heading`">
                <li v-for="object in (mode === 'cohort' ? user.cohorts : user.curatedGroups)" :key="object.id" class="ml-8">
                  <span v-if="object.domain === 'admitted_students'" class="mr-1">
                    <v-icon class="vertical-bottom" color="warning" :icon="mdiStar" />
                    <span class="sr-only">Star: Admitted Students {{ mode }}</span>
                  </span>
                  <router-link :to="`/${mode}/${object.id}`">{{ object.name }}</router-link> ({{ object.totalStudentCount }}<span class="sr-only">students</span>)
                </li>
              </ul>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </template>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {each, filter as _filter, get, isNil, map, startsWith, toLower} from 'lodash'
import {getDepartments} from '@/api/user'
import {getUsersWithCohortsByDeptCode} from '@/api/cohort'
import {getUsersWithCuratedGroupsByDeptCode} from '@/api/curated'
import {mdiMenuDown, mdiMenuRight, mdiStar} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const countExpandedDepartments = computed(() => _filter(departments.value, ['isOpen', true]).length)
const currentUser = contextStore.currentUser
const departments = ref([])
const loading = computed(() => contextStore.loading)
const mode = ref(undefined)
const modeLabel = ref(undefined)
const panels = ref([])

contextStore.loadingStart()

onMounted(() => {
  const param = toLower(get(useRoute().params, 'mode'))
  mode.value = startsWith(param, 'cohort') ? 'cohort' : 'curated'
  modeLabel.value = mode.value === 'cohort' ? 'Cohort' : 'Curated Group'
  getDepartments().then(data => {
    departments.value = data
    contextStore.loadingComplete('List of departments has loaded')
  })
})

const collapseAllDepartments = () => {
  panels.value = []
  each(departments.value, department => department.isOpen = false)
}

const expandAllDepartments = () => {
  panels.value = map(departments.value, 'code')
  each(departments.value, department => department.isOpen = true)
}

const onClickExpansionPanel = (department, isOpen) => {
  department.isOpen = isOpen.value
  if (isOpen) {
    alertScreenReader(`Showing ${mode.value}s of ${department.name} department`)
    if (isNil(department.users)) {
      department.isFetching = true
      const api = mode.value === 'cohort' ? getUsersWithCohortsByDeptCode : getUsersWithCuratedGroupsByDeptCode
      api(department.code).then(data => {
        department.users = data
        department.isFetching = false
      })
    }
  } else {
    alertScreenReader(`Hiding users of ${department.name} department`)
  }
}
</script>

<style scoped>
.expand-icon-container {
  max-width: 40px;
  min-width: 40px;
  text-align: center;
}
.sortable-group {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>

<style lang="scss">
.sortable-group {
  &.v-expansion-panel::after {
    border: none !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 0;
  }
}
</style>
