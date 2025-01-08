import {concat, each, filter, find, get, includes, isEmpty, isNaN, isNil, map, startsWith} from 'lodash'
import {DegreeProgressCourses} from '@/stores/degree-edit-session'
import {useDegreeStore} from '@/stores/degree-edit-session'

export const MAX_UNITS_ALLOWED: 10 = 10

export function categoryHasCourse(category, course): boolean {
  let courses: any[] = []
  const extractCourses = c => {
    courses = courses.concat(c.courses)
    each(c.courseRequirements, r => courses = courses.concat(r.courses))
  }
  extractCourses(category)
  each(category.subcategories, subcategory => extractCourses(subcategory))
  return map(courses, getCourseKey).includes(getCourseKey(course))
}

export function findCategoryById(categoryId) {
  const categories: any[] = useDegreeStore().categories
  return categoryId ? find(flattenCategories(categories), ['id', categoryId]) : null
}

export function flattenCategories(categories): any[] {
  let flattened: any[] = []
  each(categories, category => {
    flattened.push(category)
    each(concat(category.courseRequirements, category.subcategories || []), child => {
      flattened.push(child)
      if (child.courseRequirements) {
        flattened = concat(flattened, child.courseRequirements)
      }
    })
  })
  return flattened
}

export function getAssignedCourses(category, ignoreCourseId): any[] {
  const assigned: any[] = []
  each(flattenCategories([category]), c => {
    each(c.courses, course => {
      if ((course.sectionId || course.manuallyCreatedBy) && (!ignoreCourseId || course.id !== ignoreCourseId)) {
        assigned.push(course)
      }
    })
  })
  return assigned
}

export function getCourseKey(course: any) {
  return course && `${course.termId}-${course.sectionId}-${course.manuallyCreatedAt}-${course.manuallyCreatedBy}`
}

export function getItemsForCoursesTable(category) {
  const courses: DegreeProgressCourses = useDegreeStore().courses
  if (courses) {
    const categoryCourseIds: number[] = map(category.courses, 'id')
    const predicate = c => includes(categoryCourseIds, c.id)
    return filter(courses.assigned.concat(courses.unassigned), predicate)
      .concat(category.courseRequirements)
  } else {
    return category.courseRequirements
  }
}

export function isCampusRequirement(courseRequirement: any): boolean {
  return startsWith(courseRequirement.categoryType, 'Campus Requirement')
}

export function isValidUnits(value, maxAllowed: number): boolean {
  return !isNaN(value) && value > 0 && value <= maxAllowed
}

export function unitsWereEdited(course: any): boolean {
  return !get(course, 'manuallyCreatedBy') && !isNil(get(course, 'units')) && !isNil(get(course, 'sis.units')) && (course.units !== course.sis.units)
}
export function validateUnitRange(unitsLower, unitsUpper, maxAllowed, showUnitsUpperInput?: boolean): any {
  const invalid = message => ({valid: false, message})
  const message = `must be a number between 0 and ${maxAllowed}`
  if (isValidUnits(unitsLower, maxAllowed)) {
    if (isNil(unitsUpper)) {
      return {valid: true}
    } else {
      if (isValidUnits(unitsUpper, maxAllowed)) {
        const empty = isEmpty(unitsLower) && isEmpty(unitsUpper)
        return empty || parseFloat(unitsLower) <= parseFloat(unitsUpper) ? {valid: true} : invalid('Units upper range value must be greater than lower range value.')
      } else {
        return invalid(`Units upper range value ${message}.`)
      }
    }
  } else {
    return invalid(showUnitsUpperInput ? `Units lower range value ${message}.` : `Units ${message}`)
  }
}
