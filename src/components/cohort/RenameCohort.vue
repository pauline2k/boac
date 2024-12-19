<template>
  <v-card flat>
    <div class="align-center d-flex flex-wrap">
      <v-text-field
        id="rename-cohort-input"
        v-model="name"
        aria-label="Cohort name"
        class="v-input-details-override mr-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        hide-details
        label="Cohort Name"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[validationRules.valid]"
        validate-on="lazy input"
        @keyup.enter="submit"
        @keyup.esc="cancel"
      />
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-cohort-confirm"
          :action="submit"
          aria-label="Rename Cohort"
          :disabled="isInvalid || isSaving"
          :in-progress="isSaving"
          size="large"
          text="Rename"
        />
        <v-btn
          id="rename-cohort-cancel"
          aria-label="Cancel Rename Cohort"
          class="ml-1"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="text"
          @click="cancel"
        />
      </div>
    </div>
    <div id="name-cohort-counter" class="text-left font-size-13 text-no-wrap ml-4 mt-1">
      <span class="sr-only">Cohort name has a </span>{{ maxlength }} character limit <span v-if="size(name)">({{ maxlength - size(name) }} left)</span>
      <span
        v-if="size(name) === 255"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Cohort name cannot exceed 255 characters.
      </span>
    </div>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader} from '@/lib/utils'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {onMounted, ref} from 'vue'
import {saveCohort} from '@/api/cohort'
import {size} from 'lodash'
import {storeToRefs} from 'pinia'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {validateCohortName} from '@/lib/cohort'

const cohortStore = useCohortStore()
const {cohortId, cohortName, filters} = storeToRefs(cohortStore)
const isInvalid = ref(true)
const isSaving = ref(false)
const maxlength = ref(255)
const name = ref(undefined)
const validationRules = {
  valid: name => {
    const valid = validateCohortName({id: cohortId.value, name})
    isInvalid.value = true !== valid
    return valid
  }
}

onMounted(() => {
  name.value = cohortName.value
})

const cancel = () => {
  cohortStore.setEditMode(null)
  alertScreenReader(`Cancel renaming of cohort '${name.value}'`)
  putFocusNextTick('rename-cohort-button')
}

const submit = () => {
  if (true !== validateCohortName({id: cohortId.value, name: name.value})) {
    putFocusNextTick('rename-cohort-input')
  } else {
    isSaving.value = true
    alertScreenReader('Renaming cohort')
    cohortStore.renameCohort(name.value)
    saveCohort(cohortId.value, cohortName.value, filters.value).then(() => {
      isSaving.value = false
      alertScreenReader(`Cohort renamed to '${name.value}'`)
      setPageTitle(name.value)
      cohortStore.setEditMode(null)
      putFocusNextTick('cohort-name')
    })
  }
}
</script>
