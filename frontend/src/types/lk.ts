/**
 * LK (личный кабинет ОмГУ) types.
 */

/** LK connection status. */
export interface LkStatus {
  has_credentials: boolean;
  last_sync_at: string | null;
}

/** Credentials for LK authentication. */
export interface LkCredentials {
  email: string;
  password: string;
}

/** Session grade from LK. */
export interface SessionGrade {
  id: number;
  session_number: string;
  subject_name: string;
  result: string;
  synced_at: string;
}

/** Semester discipline from LK curriculum. */
export interface SemesterDiscipline {
  id: number;
  semester_number: number;
  discipline_name: string;
  control_form: string;
  hours: number;
  synced_at: string;
}

/** Result of sync operation. */
export interface LkSyncResult {
  grades_synced: number;
  disciplines_synced: number;
  last_sync_at: string;
}

/** Result of import operation to app. */
export interface LkImportResult {
  semesters_created: number;
  semesters_updated: number;
  subjects_created: number;
  subjects_updated: number;
}

/** Student info from LK. */
export interface LkStudentInfo {
  full_name: string | null;
  group_name: string | null;
  faculty: string | null;
  course: number | null;
  speciality: string | null;
}
