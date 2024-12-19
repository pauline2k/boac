<template>
  <v-card class="w-100" flat>
    <div class="align-center d-flex flex-wrap pt-1">
      <v-text-field
        id="rename-curated-group-input"
        v-model="name"
        :aria-invalid="!name"
        :aria-label="`${describeCuratedGroupDomain(domain, true)} name`"
        class="v-input-details-override mr-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        hide-details
        label="Curated Group Name"
        maxlength="255"
        persistent-counter
        required
        :rules="[validationRules.valid]"
        @keyup.enter="rename"
        @keyup.esc="exitRenameMode"
      />
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-curated-group-confirm"
          :action="rename"
          aria-label="Rename Curated Group"
          color="primary"
          :disabled="!size(name) || isSaving"
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
    <div class="text-medium-emphasis">255 character limit <span v-if="size(name)">({{ 255 - size(name) }} left)</span></div>
    <span
      v-if="size(name) === 255"
      aria-live="polite"
      class="sr-only"
      role="alert"
    >
      Name cannot exceed 255 characters.
    </span>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {onMounted, ref} from 'vue'
import {renameCuratedGroup} from '@/api/curated'
import {size} from 'lodash'
import {storeToRefs} from 'pinia'
import {useCuratedGroupStore} from '@/stores/curated-group/index'
import {validateCohortName} from '@/lib/cohort'

const curatedStore = useCuratedGroupStore()
const {curatedGroupId, curatedGroupName, domain} = storeToRefs(curatedStore)
const isInvalid = ref(false)
const isSaving = ref(false)
const name = ref(undefined)
const validationRules = {
  valid: name => {
    const valid = validateCohortName({id: curatedGroupId.value, name})
    isInvalid.value = true !== valid
    return valid
  }
}

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
