export interface MatrixUser {
  id: string
  full_name: string
  department: string | null
  team: string | null
}

export interface MatrixCompetency {
  id: string
  name: string
  category_id: string
}

export interface MatrixData {
  users: MatrixUser[]
  competencies: MatrixCompetency[]
  scores: Record<string, Record<string, number>>
}
