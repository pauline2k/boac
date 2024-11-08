<template>
  <div class="d-flex justify-space-around">
    <v-menu
      transition="slide-y-transition"
      variant="link"
      @update:model-value="isOpen => isMenuOpen = isOpen"
    >
      <template #activator="{ props }">
        <button
          id="header-dropdown-under-name"
          bg-primary
          class="button-menu header-button-menu pr-0 pl-1 text-body-1 text-white"
          :class="{'button-menu-active': isMenuOpen}"
          v-bind="props"
        >
          {{ currentUser.firstName || `UID:${currentUser.uid}` }}
          <v-icon :icon="mdiMenuDown" size="24" />
        </button>
      </template>
      <v-list variant="flat" class="remove-scroll">
        <v-list-item-action v-if="currentUser.canReadDegreeProgress">
          <v-btn
            id="header-menu-degree-check"
            :aria-current="route.path === '/degrees' ? 'page' : false"
            class="justify-start w-100"
            to="/degrees"
            variant="text"
          >
            Degree Checks
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin || myDirectorDepartment">
          <v-btn
            id="header-menu-analytics"
            :aria-current="route.path.startsWith('/analytics') ? 'page' : false"
            :to="currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${myDirectorDepartment.toLowerCase()}`"
            class="justify-start w-100"
            variant="text"
          >
            Flight Data Recorder
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-flight-deck"
            :aria-current="route.path === '/admin' ? 'page' : false"
            class="justify-start w-100"
            to="/admin"
            variant="text"
          >
            Flight Deck
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-passengers"
            :aria-current="route.path === '/admin/passengers' ? 'page' : false"
            class="justify-start w-100"
            to="/admin/passengers"
            variant="text"
          >
            Passenger Manifest
          </v-btn>
        </v-list-item-action>
        <v-list-item-action
          v-if="!currentUser.isAdmin"
        >
          <v-btn
            id="header-menu-profile"
            :aria-current="route.path === '/profile' ? 'page' : false"
            class="justify-start w-100"
            to="/profile"
            variant="text"
          >
            Profile
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            class="justify-start w-100"
            :href="`mailto:${contextStore.config.supportEmailAddress}`"
            target="_blank"
            variant="text"
          >
            Feedback/Help<span class="sr-only">: Email the BOA team (opens in new window)</span>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            id="header-menu-log-out"
            class="justify-start w-100"
            variant="text"
            @click="logOut"
          >
            Log Out
          </v-btn>
        </v-list-item-action>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
import {getCasLogoutUrl} from '@/api/auth'
import {mdiMenuDown} from '@mdi/js'
import {myDeptCodes} from '@/berkeley'
import {reactive, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
const deptCodes = myDeptCodes(['director'])
const isMenuOpen = ref(false)
const myDirectorDepartment = deptCodes && deptCodes[0]
const route = useRoute()

const logOut = () => getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
</script>

<style scoped>
.header-button-menu {
  height: 46px;
}
.remove-scroll {
  overflow: hidden !important;
}
</style>
