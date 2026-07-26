import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { FileText, Search, Trash2, Upload } from "lucide-react";

import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { deleteReport, searchReports } from "@/services/reportService";
import { getApiErrorMessage } from "@/utils/apiError";
import type { OcrStatus, ReportFileType } from "@/types/report";

const OCR_STATUS_VARIANT: Record<OcrStatus, BadgeVariant> = {
  pending: "default",
  processing: "warning",
  completed: "success",
  failed: "destructive",
};

export function ReportHistoryPage() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [fileType, setFileType] = useState<ReportFileType | "">("");
  const [ocrStatus, setOcrStatus] = useState<OcrStatus | "">("");
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["reports", { query, fileType, ocrStatus }],
    queryFn: () =>
      searchReports({
        query: query || undefined,
        file_type: fileType || undefined,
        ocr_status: ocrStatus || undefined,
        page: 1,
        page_size: 50,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Report deleted successfully.");
      setPendingDeleteId(null);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not delete this report."));
      setPendingDeleteId(null);
    },
  });

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Report history</h1>
          <p className="text-sm text-muted-foreground">All your uploaded medical reports.</p>
        </div>
        <Link to="/reports/upload">
          <Button className="h-10 w-auto px-5">
            <Upload className="mr-2 h-4 w-4" aria-hidden="true" />
            Upload report
          </Button>
        </Link>
      </div>

      <Card variant="glass" className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="search" className="mb-1.5 block text-sm font-medium">
            Search
          </label>
          <div className="relative">
            <Search
              className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              id="search"
              className="pl-9"
              placeholder="Search by title, description, or extracted text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>
        </div>
        <div className="sm:w-40">
          <label htmlFor="file_type" className="mb-1.5 block text-sm font-medium">
            File type
          </label>
          <Select
            id="file_type"
            value={fileType}
            onChange={(event) => setFileType(event.target.value as ReportFileType | "")}
          >
            <option value="">All types</option>
            <option value="pdf">PDF</option>
            <option value="jpg">JPG</option>
            <option value="jpeg">JPEG</option>
            <option value="png">PNG</option>
          </Select>
        </div>
        <div className="sm:w-44">
          <label htmlFor="ocr_status" className="mb-1.5 block text-sm font-medium">
            OCR status
          </label>
          <Select
            id="ocr_status"
            value={ocrStatus}
            onChange={(event) => setOcrStatus(event.target.value as OcrStatus | "")}
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </Select>
        </div>
      </Card>

      {isLoading ? (
        <FullPageSpinner label="Loading reports..." />
      ) : !data || data.reports.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No reports found"
          description="Try adjusting your search or filters, or upload a new report."
          action={
            <Link to="/reports/upload" className="text-sm font-medium text-primary hover:underline">
              Upload a report →
            </Link>
          }
        />
      ) : (
        <div className="flex flex-col gap-3">
          {data.reports.map((report) => (
            <Card
              key={report.id}
              variant="glass"
              className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between"
            >
              <Link to={`/reports/${report.id}`} className="flex flex-1 flex-col gap-1">
                <span className="font-semibold hover:text-primary">{report.title}</span>
                {report.description && (
                  <span className="line-clamp-1 text-sm text-muted-foreground">
                    {report.description}
                  </span>
                )}
                <span className="text-xs text-muted-foreground">
                  {report.original_filename} ·{" "}
                  {new Date(report.created_at).toLocaleDateString(undefined, {
                    dateStyle: "medium",
                  })}
                </span>
              </Link>
              <div className="flex items-center gap-2">
                <Badge variant="default" className="uppercase">
                  {report.file_type}
                </Badge>
                <Badge variant={OCR_STATUS_VARIANT[report.ocr_status]}>{report.ocr_status}</Badge>
                {report.has_ai_summary && <Badge variant="info">AI summary</Badge>}
                <button
                  type="button"
                  aria-label="Delete report"
                  onClick={() => setPendingDeleteId(report.id)}
                  className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={pendingDeleteId !== null}
        title="Delete this report?"
        description="This will permanently delete the report file and any AI summary generated from it. This action cannot be undone."
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
        onConfirm={() => pendingDeleteId && deleteMutation.mutate(pendingDeleteId)}
        onCancel={() => setPendingDeleteId(null)}
      />
    </div>
  );
}
