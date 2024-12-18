import axios from 'axios'
import {DateTime} from 'luxon'
import {each, isNil, trim, truncate} from 'lodash'
import {useContextStore} from '@/stores/context'

export default {
  apiBaseUrl: () => useContextStore().config.apiBaseUrl,
  createDownloadFilename: (prefix: string, extension: string): string => {
    const normalized = trim(prefix.replace(/[^a-zA-Z0-9\s-]/g, '')).replace(/\s/g, '-')
    const filename = truncate(normalized ? normalized.toLowerCase() : 'students', {length: 100, omission: ''})
    const now = DateTime.now().toFormat('yyyy-MM-dd_HH-mm-ss')
    return `${filename}_${now}.${extension}`
  },
  postMultipartFormData: (path: string, data: object) => {
    const formData = new FormData()
    each(data, (value, key) => {
      if (!isNil(value)) {
        formData.append(key, value)
      }
    })
    const apiBaseUrl = useContextStore().config.apiBaseUrl
    const config = {headers: {'Content-Type': 'multipart/form-data'}}
    return axios.post(`${apiBaseUrl}${path}`, formData, config)
      .then(response => response.data)
      .catch(error => {
        // eslint-disable-next-line no-console
        console.log(error)
        return error
      }
    )
  }
}
