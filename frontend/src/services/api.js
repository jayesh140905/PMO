import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'x-user-email': 'admin@vigorousone.ai' }
})

export const fetchDashboard = async () => (await api.get('/dashboards/control-tower')).data
export const createProject = async (payload) => (await api.post('/projects', payload)).data
export const uploadMeeting = async (payload) => (await api.post('/inputs/upload', payload)).data

export default api
