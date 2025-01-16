import {cloneDeep, find, isNil, size} from 'lodash'
import {StoreDefinition, defineStore} from 'pinia'

const EDIT_MODE_TYPES = ['add', 'apply', 'edit-[0-9]+', 'rename']

export const useCohortStore: StoreDefinition = defineStore('cohort', {
  state: () => ({
    cohortId: undefined as number | undefined,
    cohortName: undefined as string | null | undefined,
    cohortOwnerUid: undefined,
    domain: undefined as string | null | undefined,
    editMode: undefined as string | null | undefined,
    filterOptionGroups: [] as object[],
    filters: [] as object[],
    isCompactView: false,
    isModifiedSinceLastSearch: false,
    isOwnedByCurrentUser: false,
    orderBy: undefined,
    originalFilters: [] as object[],
    pagination: {
      currentPage: undefined as number | null | undefined,
      itemsPerPage: 50
    },
    students: undefined,
    termId: undefined,
    totalStudentCount: undefined
  }),
  getters: {
    cohortOwner: state => state.isOwnedByCurrentUser ? 'me' : state.cohortOwnerUid,
    showApplyButton: state => state.isModifiedSinceLastSearch === true && !!size(state.filters),
    showSaveButton: state => state.isModifiedSinceLastSearch === false,
    showSortBy: state => !state.isModifiedSinceLastSearch && (state.totalStudentCount || 0) > 1
  },
  actions: {
    addFilter(filter: object) {
      return this.filters.push(filter)
    },
    removeFilter(index: number) {
      this.filters.splice(index, 1)
      this.isModifiedSinceLastSearch = true
    },
    renameCohort(name: string) {
      this.cohortName = name
    },
    resetSession() {
      this.editMode = undefined
      this.cohortId = undefined
      this.cohortName = undefined
      this.cohortOwnerUid = undefined
      this.isModifiedSinceLastSearch = true
      this.isOwnedByCurrentUser = true
      this.filters = []
      this.students = undefined
      this.totalStudentCount = undefined
      this.pagination.currentPage = 1
    },
    restoreOriginalFilters() {
      this.filters = cloneDeep(this.originalFilters)
    },
    setCurrentPage(currentPage: number) {
      this.pagination.currentPage = currentPage
    },
    setCompactView(compactView: boolean) {
      return this.isCompactView = compactView
    },
    setDomain(domain: string) {
      this.domain = domain
    },
    setEditMode(editMode: string | null) {
      if (isNil(editMode)) {
        this.editMode = null
      } else if (find(EDIT_MODE_TYPES, type => editMode.match(type))) {
        // Valid mode
        this.editMode = editMode
      } else {
        throw new TypeError('Invalid page mode: ' + editMode)
      }
    },
    setModifiedSinceLastSearch(value: boolean) {
      this.isModifiedSinceLastSearch = value
    },
    // Store an unmodified copy of the most recently applied filters in case of cancellation.
    stashOriginalFilters() {
      this.originalFilters = cloneDeep(this.filters)
    },
    toggleCompactView() {
      this.isCompactView = !this.isCompactView
    },
    updateFilterOptions(filterOptionGroups: object[]) {
      this.filterOptionGroups = filterOptionGroups
    },
    updateExistingFilter({index, updatedFilter}) {
      this.filters[index] = updatedFilter
    },
    updateSession(cohort, filters, students, totalStudentCount) {
      this.editMode = null
      this.cohortId = cohort && cohort.id
      this.cohortName = cohort && cohort.name
      this.cohortOwnerUid = cohort && cohort.owner && cohort.owner.uid
      this.isOwnedByCurrentUser = !cohort || cohort.isOwnedByCurrentUser
      this.filters = filters || []
      this.students = students
      this.totalStudentCount = totalStudentCount
      this.pagination.currentPage = 1
      if (!this.cohortId) {
        // If cohortId is null then show 'Save Cohort' for unsaved search results
        this.isModifiedSinceLastSearch = true
      }
    },
    updateStudents({students, totalStudentCount}) {
      this.students = students
      this.totalStudentCount = totalStudentCount
    }
  }
})
