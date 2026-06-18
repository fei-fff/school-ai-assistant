/**
 * Knowledge API — upload, process, query, list.
 */
import http from './index'

export function uploadDocument(formData) {
  return http.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function processDocument(docId, params = {}) {
  return http.post(`/knowledge/process/${docId}`, null, { params })
}

export function processSingleTask(docId, taskName) {
  return http.post(`/knowledge/process/${docId}/${taskName}`)
}

export function queryKnowledge(params) {
  return http.post('/knowledge/query', null, { params })
}

export function listDocuments(params) {
  return http.get('/knowledge/documents', { params })
}

export function getDocumentDetail(docId) {
  return http.get(`/knowledge/documents/${docId}`)
}

export function getDocumentStatus(docId) {
  return http.get(`/knowledge/documents/${docId}/status`)
}

export function deleteDocument(docId) {
  return http.delete(`/knowledge/documents/${docId}`)
}
