import http from './index'

export function getMyCard() { return http.get('/mentor/me') }
export function createMyCard(data) { return http.post('/mentor/me', data) }
export function updateMyCard(data) { return http.put('/mentor/me', data) }
export function listColleges() { return http.get('/mentor/colleges') }
export function listMentors(params) { return http.get('/mentor/list', { params }) }
export function getMentorDetail(id) { return http.get(`/mentor/${id}`) }
