<template>
  <component
    :is="isAutocomplete ? 'v-autocomplete' : 'v-combobox'"
    :id="`${idPrefix}-input`"
    ref="container"
    v-model="model"
    :aria-required="required"
    autocomplete="list"
    :base-color="color"
    bg-color="surface"
    :class="clazz"
    :clearable="clearable"
    :color="color"
    :density="density"
    :disabled="disabled"
    hide-details
    hide-no-data
    :items="items"
    :list-props="{ariaLive: 'off'}"
    :loading="isBusy"
    :maxlength="maxlength"
    :menu-icon="null"
    :menu-props="mergedMenuProps"
    :min-width="minWidth"
    persistent-clear
    :placeholder="placeholder || label"
    return-object
    :type="inputType"
    variant="outlined"
    @blur="isEmpty(query) ? onClear() : noop()"
    @keydown.enter.stop.prevent="onSubmit"
    @update:focused="onFocusInput"
    @update:menu="onToggleMenu"
    @update:search="onUpdateSearch"
  >
    <template #loader="{isActive}">
      <v-progress-circular
        v-if="isActive"
        class="mr-5"
        color="primary"
        indeterminate
        size="x-small"
        width="2"
      />
    </template>
    <template #clear>
      <v-btn
        v-if="!isBusy"
        :id="`${idPrefix}-clear-btn`"
        :aria-label="`Clear ${label} input`"
        class="d-flex align-self-center v-icon"
        :class="{'disabled-opacity': !model}"
        density="compact"
        :disabled="!model"
        exact
        :icon="mdiCloseCircle"
        :ripple="false"
        variant="text"
        @keydown.enter.stop.prevent="onClearInput"
        @click.stop.prevent="onClearInput"
      />
    </template>
    <template #item="{index, item}">
      <v-list-item
        :id="`${idPrefix}-option-${index}`"
        :aria-selected="index === focusedListItemIndex"
        class="font-size-18"
        @click="() => onSelectItem(item)"
        @focus="e => onFocusListItem(e, index)"
      >
        {{ item.props.title }}
      </v-list-item>
    </template>
    <template v-if="isAutocomplete" #selection="{item}">
      {{ item.props.title }}
    </template>
  </component>
  <span aria-live="polite" class="sr-only">{{ resultsSummary }}</span>
</template>

<script setup>
import {get, filter, includes, isEmpty, noop} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  ariaDescription: {
    default: 'Expect auto-suggest.',
    required: false,
    type: String
  },
  clazz: {
    default: '',
    required: false,
    type: [String, Object]
  },
  clearable: {
    required: true,
    type: Boolean
  },
  color: {
    default: 'on-surface',
    required: false,
    type: String
  },
  density: {
    default: 'comfortable',
    required: false,
    type: String
  },
  disabled: {
    required: false,
    type: Boolean
  },
  filterResults: {
    default: () => {},
    required: false,
    type: Function
  },
  getValue: {
    required: true,
    type: Function
  },
  idPrefix: {
    required: true,
    type: String
  },
  inputType: {
    default: 'text',
    required: false,
    type: String
  },
  isAutocomplete: {
    required: false,
    type: Boolean
  },
  isBusy: {
    required: false,
    type: Boolean
  },
  items: {
    required: true,
    type: Array
  },
  label: {
    required: true,
    type: String
  },
  listLabel: {
    required: true,
    type: String
  },
  maxlength: {
    default: undefined,
    required: false,
    type: [String, Number]
  },
  menuProps: {
    default: () => {},
    required: false,
    type: Object
  },
  minWidth: {
    default: undefined,
    required: false,
    type: [String, Number]
  },
  onClear: {
    default: () => {},
    required: false,
    type: Function
  },
  onToggleMenu: {
    default: () => {},
    required: false,
    type: Function
  },
  onSubmit: {
    default: () => {},
    required: false,
    type: Function
  },
  openOnFocus: {
    required: false,
    type: Boolean
  },
  placeholder: {
    default: undefined,
    required: false,
    type: String
  },
  required: {
    required: false,
    type: Boolean
  },
  setValue: {
    required: true,
    type: Function
  },
  whenItemSelected: {
    default: () => {},
    required: false,
    type: Function
  }
})

const comboboxWrapper = ref(undefined)
const container = ref()
const focusedListItemIndex = ref(undefined)
const input = ref(undefined)
const mergedMenuProps = ref({
  id: `${props.idPrefix}-menu`,
  closeOnContentClick: true,
  ...props.menuProps
})
const model = defineModel({
  get() {
    return props.getValue()
  },
  set(v) {
    props.setValue(v)
  },
  type: String
})
const query = ref(undefined)
const resultsSummary = ref(undefined)
const resultsSummaryInterval = ref(undefined)

onMounted(() => {
  comboboxWrapper.value = container.value.$el.querySelector('div[role="combobox"]')
  input.value = container.value.$el.querySelector('input')
  if (comboboxWrapper.value) {
    comboboxWrapper.value.removeAttribute('role')
    comboboxWrapper.value.removeAttribute('aria-expanded')
  }
  if (input.value) {
    input.value.setAttribute('role', 'combobox')
    input.value.setAttribute('aria-autocomplete', 'list')
    input.value.setAttribute('aria-controls', `${props.idPrefix}-menu`)
    input.value.setAttribute('aria-expanded', false)
    input.value.setAttribute('aria-label', props.label)
  }
})

const onClearInput = () => {
  model.value = null
  props.onClear()
  alertScreenReader('Cleared.')
  putFocusNextTick(`${props.idPrefix}-input`)
}

const onUpdateSearch = q => {
  query.value = q
  props.filterResults(q)
  clearInterval(resultsSummaryInterval.value)
  resultsSummaryInterval.value = setInterval(setResultsSummary, 1000)
}

const onFocusListItem = (event, index) => {
  input.value.setAttribute('aria-activedescendant', event.target.id)
  focusedListItemIndex.value = index
}

const onToggleMenu = isOpen => {
  props.onToggleMenu(isOpen)
  nextTick(() => {
    if (isOpen) {
      const menu = document.getElementById(`${props.idPrefix}-menu`)
      const listbox = menu && menu.querySelector('[role="listbox"]')
      if (listbox) {
        listbox.setAttribute('aria-label', props.listLabel)
      }
      input.value.setAttribute('aria-expanded', true)
    }
    else {
      input.value.setAttribute('aria-expanded', false)
      input.value.removeAttribute('aria-activedescendant')
      clearInterval(resultsSummaryInterval.value)
    }
  })
}

const onFocusInput = isFocused => {
  // Passing open-on-focus via menuProps (https://vuetifyjs.com/en/api/v-menu/#props-open-on-focus)
  // doesn't seem to have an effect, thus this workaround.
  if (props.openOnFocus && isFocused && !container.value.menu) {
    container.value.menu = true
  }
}

const onSelectItem = item => {
  model.value = get(item.raw, 'value', item.raw)
  if (props.isAutocomplete) {
    container.value.search = ''
  }
  nextTick(props.whenItemSelected)
}

const setResultsSummary = () => {
  const menuOverlay = document.getElementById(`${props.idPrefix}-menu`)
  const listbox = menuOverlay && menuOverlay.querySelector('[role="listbox"]')
  clearInterval(resultsSummaryInterval.value)
  if (listbox) {
    const suggestions = filter(listbox.children, child => includes(child.classList, 'v-list-item'))
    resultsSummary.value = pluralize('result', suggestions.length)
  } else {
    resultsSummary.value = ''
  }
}
</script>

<style scoped>
:deep(.v-field__loader) {
  display: flex;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  padding-right: 1px;
  top: 0;
}
:deep(.v-field) {
  color: inherit !important;
}
</style>
