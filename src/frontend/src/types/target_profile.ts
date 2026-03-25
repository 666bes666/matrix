export interface TargetProfileCreate {
  name: string
  department_id: string
  position?: string
  description?: string
}

export interface TargetProfileUpdate {
  name?: string
  position?: string
  description?: string
}

export interface TargetProfileCompetencyInput {
  competency_id: string
  required_level: number
  is_mandatory?: boolean
}

export interface CompetencyBrief {
  id: string
  name: string
}

export interface TargetProfileCompetencyRead {
  competency_id: string
  required_level: number
  is_mandatory: boolean
  competency: CompetencyBrief
}

export interface DepartmentBrief {
  id: string
  name: string
}

export interface TargetProfileRead {
  id: string
  name: string
  department_id: string
  department: DepartmentBrief
  position: string | null
  description: string | null
  competencies: TargetProfileCompetencyRead[]
  created_at: string
  updated_at: string
}

export interface GapItem {
  competency_id: string
  competency_name: string
  required_level: number
  is_mandatory: boolean
  current_score: number | null
}
