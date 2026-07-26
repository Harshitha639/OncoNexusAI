import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { AlertTriangle, FileText, Gauge, Sparkles } from "lucide-react";

import { AlertBanner } from "@/components/common/AlertBanner";
import { FullPageSpinner } from "@/components/common/Spinner";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { fetchReportDetail, fetchReportSummary, generateReportSummary } from "@/services/reportService";
import { getApiErrorMessage } from "@/utils/apiError";
import type { OcrStatus } from "@/types/report";

const OCR_STATUS_VARIANT: Record<OcrStatus, BadgeVariant> = {
  pending: "default",
  processing: "warning",
  completed: "success",
  failed: "destructive",
};

function riskBadge(score: number | null) {
  if (score === null) return null;
  if (score < 34) return <Badge variant="success">Low risk ({Math.round(score)})</Badge>;
  if (score < 67) return <Badge variant="warning">Moderate risk ({Math.round(score)})</Badge>;
  return <Badge variant="destructive">High risk ({Math.round(score)})</Badge>;
}

export function ReportDetailsPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const queryClient = useQueryClient();

  const { data: report, isLoading } = useQuery({
    queryKey: ["report", reportId],
    queryFn: () => fetchReportDetail(reportId as string),
    enabled: Boolean(reportId),
    refetchInterval: (query) => {
      const status = query.state.data?.ocr_status;
      return status === "pending" || status === "processing" ? 3000 : false;
    },
  });

  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ["report-summary", reportId],
    queryFn: () => fetchReportSummary(reportId as string),
    enabled: Boolean(reportId) && report?.has_ai_summary === true,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateReportSummary(reportId as string),
    onSuccess: (result) => {
      queryClient.setQueryData(["report-summary", reportId], result);
      queryClient.invalidateQueries({ queryKey: ["report", reportId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("AI summary generated successfully.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not generate the AI summary."));
    },
  });

  if (isLoading || !report) {
    return <FullPageSpinner label="Loading report..." />;
  }

  const canGenerateSummary = report.ocr_status === "completed";

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{report.title}</h1>
          {report.description && (
            <p className="text-sm text-muted-foreground">{report.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="default" className="uppercase">
            {report.file_type}
          </Badge>
          <Badge variant={OCR_STATUS_VARIANT[report.ocr_status]}>OCR: {report.ocr_status}</Badge>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Extracted text */}
        <Card variant="glass" className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" aria-hidden="true" />
            <h2 className="text-base font-semibold">Extracted text</h2>
          </div>

          {report.ocr_status === "completed" && report.extracted_text && (
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-muted p-4 text-sm">
              {report.extracted_text}
            </pre>
          )}
          {(report.ocr_status === "pending" || report.ocr_status === "processing") && (
            <AlertBanner variant="info" message="Text extraction is still in progress. This page refreshes automatically." />
          )}
          {report.ocr_status === "failed" && (
            <AlertBanner
              variant="error"
              message={report.ocr_error ?? "Text extraction failed for this report."}
            />
          )}
        </Card>

        {/* AI summary */}
        <Card variant="glass" className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
              <h2 className="text-base font-semibold">AI report summary</h2>
            </div>
            <Button
              className="h-9 w-auto px-4"
              isLoading={generateMutation.isPending}
              disabled={!canGenerateSummary}
              onClick={() => generateMutation.mutate()}
            >
              {report.has_ai_summary ? "Regenerate" : "Generate summary"}
            </Button>
          </div>

          {!canGenerateSummary && (
            <AlertBanner
              variant="info"
              message="AI summary generation will be available once text extraction (OCR) completes."
            />
          )}

          {isSummaryLoading && <p className="text-sm text-muted-foreground">Loading summary...</p>}

          {summary && summary.status === "completed" && (
            <div className="flex flex-col gap-4 text-sm">
              {summary.risk_score !== null && (
                <div className="flex items-center gap-2">
                  <Gauge className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  {riskBadge(summary.risk_score)}
                </div>
              )}

              {(summary.cancer_type || summary.cancer_stage) && (
                <p>
                  <span className="font-semibold">Cancer type / stage:</span>{" "}
                  {summary.cancer_type ?? "Not identified"}
                  {summary.cancer_stage ? ` · Stage ${summary.cancer_stage}` : ""}
                </p>
              )}

              {summary.patient_friendly_summary && (
                <div>
                  <h3 className="mb-1 font-semibold">Patient-friendly summary</h3>
                  <p className="text-muted-foreground">{summary.patient_friendly_summary}</p>
                </div>
              )}

              {summary.medical_summary && (
                <div>
                  <h3 className="mb-1 font-semibold">Medical summary</h3>
                  <p className="text-muted-foreground">{summary.medical_summary}</p>
                </div>
              )}

              {summary.important_findings && summary.important_findings.length > 0 && (
                <div>
                  <h3 className="mb-1 font-semibold">Important findings</h3>
                  <ul className="list-inside list-disc text-muted-foreground">
                    {summary.important_findings.map((finding, index) => (
                      <li key={index}>{finding}</li>
                    ))}
                  </ul>
                </div>
              )}

              {summary.abnormal_values && summary.abnormal_values.length > 0 && (
                <div>
                  <h3 className="mb-1 flex items-center gap-1.5 font-semibold">
                    <AlertTriangle className="h-4 w-4 text-amber-500" aria-hidden="true" />
                    Abnormal values
                  </h3>
                  <div className="overflow-hidden rounded-lg border border-border">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-3 py-2">Test</th>
                          <th className="px-3 py-2">Value</th>
                          <th className="px-3 py-2">Reference range</th>
                          <th className="px-3 py-2">Severity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {summary.abnormal_values.map((entry, index) => (
                          <tr key={index} className="border-t border-border">
                            <td className="px-3 py-2">{entry.name}</td>
                            <td className="px-3 py-2">{entry.value}</td>
                            <td className="px-3 py-2">{entry.reference_range ?? "—"}</td>
                            <td className="px-3 py-2 capitalize">{entry.severity ?? "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {summary.biomarkers && summary.biomarkers.length > 0 && (
                <div>
                  <h3 className="mb-1 font-semibold">Biomarkers</h3>
                  <div className="overflow-hidden rounded-lg border border-border">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-3 py-2">Name</th>
                          <th className="px-3 py-2">Value</th>
                          <th className="px-3 py-2">Reference range</th>
                        </tr>
                      </thead>
                      <tbody>
                        {summary.biomarkers.map((entry, index) => (
                          <tr key={index} className="border-t border-border">
                            <td className="px-3 py-2">{entry.name}</td>
                            <td className="px-3 py-2">{entry.value}</td>
                            <td className="px-3 py-2">{entry.reference_range ?? "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {summary.recommendations && (
                <div>
                  <h3 className="mb-1 font-semibold">Recommendations</h3>
                  <p className="text-muted-foreground">{summary.recommendations}</p>
                </div>
              )}

              {summary.follow_up_suggestions && (
                <div>
                  <h3 className="mb-1 font-semibold">Follow-up suggestions</h3>
                  <p className="text-muted-foreground">{summary.follow_up_suggestions}</p>
                </div>
              )}

              {summary.risk_indicators && summary.risk_indicators.length > 0 && (
                <div>
                  <h3 className="mb-1 font-semibold">Risk indicators</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {summary.risk_indicators.map((indicator, index) => (
                      <Badge key={index} variant="warning">
                        {indicator}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {summary && summary.status === "failed" && (
            <AlertBanner
              variant="error"
              message={summary.error_message ?? "AI summary generation failed."}
            />
          )}

          {!summary && canGenerateSummary && !report.has_ai_summary && (
            <p className="text-sm text-muted-foreground">
              No AI summary yet — click "Generate summary" to analyze this report with Gemini.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
