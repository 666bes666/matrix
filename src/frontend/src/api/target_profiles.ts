import { apiClient } from './client'
import type {
  TargetProfileRead,
  TargetProfileCreate,
  TargetProfileUpdate,
  TargetProfileCompetencyInput,
  GapItem,
} from '../types/target_profile'

export const targetProfilesApi = {
  list: (department_id?: string) =>
    apiClient
      .get<TargetProfileRead[]>('/target-profiles', { params: { department_id } })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<TargetProfileRead>(`/target-profiles/${id}`).then((r) => r.data),

  create: (data: TargetProfileCreate) =>
    apiClient.post<TargetProfileRead>('/target-profiles', data).then((r) => r.data),

  update: (id: string, data: TargetProfileUpdate) =>
    apiClient.patch<TargetProfileRead>(`/target-profiles/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/target-profiles/${id}`),

  setCompetencies: (id: string, competencies: TargetProfileCompetencyInput[]) =>
    apiClient
      .put<TargetProfileRead>(`/target-profiles/${id}/competencies`, competencies)
      .then((r) => r.data),

  getGap: (id: string, userId: string) =>
    apiClient.get<GapItem[]>(`/target-profiles/${id}/gap/${userId}`).then((r) => r.data),
}
