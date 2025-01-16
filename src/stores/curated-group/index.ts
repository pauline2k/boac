import {Student} from '@/lib/utils'
import {StoreDefinition, defineStore} from 'pinia'
import {find, isNil} from 'lodash'

const VALID_MODES = ['bulkAdd', 'rename']

export const useCuratedGroupStore: StoreDefinition = defineStore('curatedGroup', {
  state: () => ({
    curatedGroupId: NaN as number,
    curatedGroupName: undefined as undefined | string,
    domain: undefined as undefined | string,
    itemsPerPage: 50,
    mode: undefined as undefined | string,
    ownerId: undefined as undefined | number,
    pageNumber: undefined as undefined | number,
    referencingCohortIds: [] as number[],
    students: [] as Student[],
    totalStudentCount: undefined as undefined | number
  }),
  actions: {
    removeStudent(sid: string) {
      const deleteIndex = this.students.findIndex(student => student.sid === sid)
      if (deleteIndex > -1) {
        this.students.splice(deleteIndex, 1)
      }
    },
    resetMode() {
      this.mode = undefined
    },
    setCuratedGroupId(curatedGroupId: number) {
      this.curatedGroupId = curatedGroupId
    },
    setCuratedGroupName(curatedGroupName: string) {
      this.curatedGroupName = curatedGroupName
    },
    setDomain(domain: string) {
      this.domain = domain
    },
    setMode(mode: string) {
      if (isNil(mode)) {
        this.mode = undefined
      } else if (find(VALID_MODES, type => mode.match(type))) {
        this.mode = mode
      } else {
        throw new TypeError('Invalid mode: ' + mode)
      }
    },
    setOwnerId(ownerId: number) {
      this.ownerId = ownerId
    },
    setPageNumber(pageNumber: number) {
      this.pageNumber = pageNumber
    },
    setReferencingCohortIds(referencingCohortIds: number[]) {
      this.referencingCohortIds = referencingCohortIds
    },
    setStudents(students: Student[]) {
      this.students = students
    },
    setTotalStudentCount(totalStudentCount: number) {
      this.totalStudentCount = totalStudentCount
    }
  }
})
