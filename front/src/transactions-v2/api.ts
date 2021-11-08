import api from 'common-v2/api'

export function getSnapshot(entity_id: number, year: number) {
  return api.get('/snapshot', { params: { entity_id, year } })
}

export function getLots(entity_id: number) {
  return api.get('/lots', { params: { entity_id } })
}