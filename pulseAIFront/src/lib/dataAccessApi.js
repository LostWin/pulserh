import { api } from './api';

export const dataAccessApi = {
  listResources: () => api.get('/admin/data-access/resources'),
  listPolicies: ({ resource, scope }) => api.get(`/admin/data-access/policies?resource=${encodeURIComponent(resource)}&scope=${encodeURIComponent(scope)}`),
  createPolicy: (payload) => api.post('/admin/data-access/policies', payload),
  updatePolicy: (policyId, payload) => api.put(`/admin/data-access/policies/${policyId}`, payload),
  deletePolicy: (policyId) => api.delete(`/admin/data-access/policies/${policyId}`),
  preview: (payload) => api.post('/admin/data-access/preview', payload),
};
