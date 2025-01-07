<template>
  <v-card class="w-100" flat>
    <div class="align-start d-flex flex-wrap pt-1">
      <v-text-field
        id="rename-curated-group-input"
        v-model="name"
        :aria-invalid="!name"
        :aria-label="`${describeCuratedGroupDomain(domain, true)} name`"
        class="v-input-details-override mb-1 mr-3"
        density="comfortable"
        :disabled="isSaving"
        label="Curated Group Name"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[() => isValidName]"
        validate-on="lazy input"
        @keyup.enter="rename"
        @keyup.esc="exitRenameMode"
      >
        <template #details>
          <div class="pt-1">
            {{ size(name) ? `${maxlength} character limit (${maxlength - size(name)} left)` : `${maxlength} character limit` }}
          </div>
        </template>
      </v-text-field>
      <span
        v-if="size(name) === maxlength"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Name cannot exceed {{ maxlength }} characters.
      </span>
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-curated-group-confirm"
          :action="rename"
          aria-label="Rename Curated Group"
          :disabled="isValidName !== true || isSaving"
          :in-progress="isSaving"
          size="large"
          :text="isSaving ? 'Renaming' : 'Rename'"
        />
        <v-btn
          id="rename-curated-group-cancel"
          aria-label="Cancel Rename Curated Group"
          class="ml-1"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="text"
          @click="exitRenameMode"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {computed, onMounted, ref} from 'vue'
import {renameCuratedGroup} from '@/api/curated'
import {size} from 'lodash'
import {storeToRefs} from 'pinia'
import {useCuratedGroupStore} from '@/stores/curated-group/index'
import {validateCohortName} from '@/lib/cohort'

const curatedStore = useCuratedGroupStore()
const {curatedGroupId, curatedGroupName, domain} = storeToRefs(curatedStore)
const isSaving = ref(false)
const isValidName = computed(() => validateCohortName({id: curatedGroupId.value, name: name.value}))
const maxlength = 255
const name = ref(undefined)

onMounted(() => {
  name.value = curatedGroupName.value
})

const exitRenameMode = () => {
  curatedStore.resetMode()
  alertScreenReader('Canceled rename')
  putFocusNextTick('rename-curated-group-button')
}

const rename = () => {
  if (validateCohortName({name: name.value}) !== true) {
    putFocusNextTick('rename-curated-group-input')
  } else {
    isSaving.value = true
    renameCuratedGroup(curatedGroupId.value, name.value).then(curatedGroup => {
      curatedStore.setCuratedGroupName(curatedGroup.name)
      setPageTitle(curatedGroupName.value)
      exitRenameMode()
      isSaving.value = false
      alertScreenReader(`Renamed ${describeCuratedGroupDomain(domain.value, false)}`)
      putFocusNextTick('rename-curated-group-button"')
    })
  }
}
</script>
