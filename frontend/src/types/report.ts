/** Mirrors the backend's `app.schemas.report` contracts. */

export type ReportFileType = "pdf" | "jpg" | "jpeg" | "png";
export type OcrStatus = "pending" | "processing" | "completed" | "failed";
export type AiSummaryStatus = "pending" | "processing" | "completed" | "failed";

export interface MedicalReport {
  id: string;
  patient_id: string;
  title: string;
  description: string | null;
  original_filename: string;
  file_type: ReportFileType;
  file_size_bytes: number;
  ocr_status: OcrStatus;
  ocr_engine: string | null;
  has_ai_summary: boolean;
  created_at: string;
  updated_at: string;
}

export interface MedicalReportDetail extends MedicalReport {
  extracted_text: string | null;
  ocr_error: string | null;
}

export interface BiomarkerEntry {
  name: string;
  value: string;
  reference_range?: string | null;
}

export interface AbnormalValueEntry {
  name: string;
  value: string;
  reference_range?: string | null;
  severity?: string | null;
}

export interface ReportAnalysis {
  id: string;
  report_id: string;
  status: AiSummaryStatus;
  error_message: string | null;
  patient_friendly_summary: string | null;
  medical_summary: string | null;
  important_findings: string[] | null;
  cancer_type: string | null;
  cancer_stage: string | null;
  biomarkers: BiomarkerEntry[] | null;
  abnormal_values: AbnormalValueEntry[] | null;
  recommendations: string | null;
  follow_up_suggestions: string | null;
  risk_indicators: string[] | null;
  risk_score: number | null;
  model_used: string | null;
  created_at: string;
  updated_at: string;
}
