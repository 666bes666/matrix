import { apiClient } from './client'
import type {
  CampaignRead,
  CampaignCreate,
  AssessmentRead,
  AssessmentCreate,
  AssessmentScoreSubmit,
} from '../types/assessment'

export const assessmentsApi = {
  listCampaigns: (status?: string) =>
    apiClient
      .get<CampaignRead[]>('/assessments/campaigns', { params: { status } })
      .then((r) => r.data),

  getCampaign: (id: string) =>
    apiClient.get<CampaignRead>(`/assessments/campaigns/${id}`).then((r) => r.data),

  createCampaign: (data: CampaignCreate) =>
    apiClient.post<CampaignRead>('/assessments/campaigns', data).then((r) => r.data),

  createAssessment: (data: AssessmentCreate) =>
    apiClient.post<AssessmentRead>('/assessments', data).then((r) => r.data),

  listAssessments: (params?: { campaign_id?: string; assessee_id?: string }) =>
    apiClient.get<AssessmentRead[]>('/assessments', { params }).then((r) => r.data),

  getAssessment: (id: string) =>
    apiClient.get<AssessmentRead>(`/assessments/${id}`).then((r) => r.data),

  submitScores: (id: string, data: AssessmentScoreSubmit) =>
    apiClient.post<AssessmentRead>(`/assessments/${id}/scores`, data).then((r) => r.data),
}
