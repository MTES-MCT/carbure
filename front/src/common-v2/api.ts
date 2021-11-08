import axios from 'axios'

export interface Api<T> {
  status: 'success' | 'error',
  data?: T
  error?: string
}

export const api = axios.create({
  baseURL: `${window.location.origin}/api`,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFTOKEN',
})

export default api