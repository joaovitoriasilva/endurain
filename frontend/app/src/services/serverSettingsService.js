import {
  fetchGetRequest,
  fetchPostRequest,
  fetchPutRequest,
  fetchDeleteRequest,
  fetchPostFileRequest
} from '@/utils/serviceUtils'
import { fetchPublicGetRequest } from '@/utils/servicePublicUtils'

export const serverSettings = {
  // Server settings public
  getPublicServerSettings() {
    return fetchPublicGetRequest('public/server_settings')
  },
  // Server settings authenticated
  editServerSettings(data) {
    return fetchPutRequest('server_settings', data)
  },
  uploadLoginPhotoFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    return fetchPostFileRequest('server_settings/upload/login', formData)
  },
  deleteLoginPhotoFile() {
    return fetchDeleteRequest('server_settings/upload/login')
  }
}
