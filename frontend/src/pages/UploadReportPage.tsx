import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { UploadCloud } from "lucide-react";

import { FileDropzone } from "@/components/common/FileDropzone";
import { FormField } from "@/components/common/FormField";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { uploadReport } from "@/services/reportService";
import { getApiErrorMessage } from "@/utils/apiError";
import { reportUploadSchema, type ReportUploadFormValues } from "@/utils/validation";

export function UploadReportPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | undefined>();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ReportUploadFormValues>({ resolver: zodResolver(reportUploadSchema) });

  const uploadMutation = useMutation({
    mutationFn: ({ title, description }: ReportUploadFormValues) => {
      if (!file) throw new Error("Please select a file to upload.");
      return uploadReport(title, description, file);
    },
    onSuccess: (report) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      toast.success("Report uploaded successfully! Processing in the background.");
      navigate(`/reports/${report.id}`);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not upload your report."));
    },
  });

  function onSubmit(values: ReportUploadFormValues) {
    if (!file) {
      setFileError("Please select a file to upload.");
      return;
    }
    setFileError(undefined);
    uploadMutation.mutate(values);
  }

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div>
        <h1 className="text-2xl font-bold">Upload medical report</h1>
        <p className="text-sm text-muted-foreground">
          Supported formats: PDF, JPG, JPEG, PNG. Maximum size 20 MB.
        </p>
      </div>

      <Card variant="glass" className="max-w-2xl">
        <form className="flex flex-col gap-5" onSubmit={handleSubmit(onSubmit)} noValidate>
          <FileDropzone file={file} onFileSelected={setFile} error={fileError} />

          <FormField label="Title" htmlFor="title" error={errors.title?.message}>
            <Input id="title" placeholder="e.g. CT Scan — Chest, June 2026" {...register("title")} />
          </FormField>

          <FormField
            label="Description (optional)"
            htmlFor="description"
            error={errors.description?.message}
          >
            <Textarea
              id="description"
              placeholder="Any additional context about this report"
              {...register("description")}
            />
          </FormField>

          <Button
            type="submit"
            className="h-11 w-auto self-end px-8"
            isLoading={isSubmitting || uploadMutation.isPending}
          >
            <UploadCloud className="mr-2 h-4 w-4" aria-hidden="true" />
            Upload report
          </Button>
        </form>
      </Card>
    </div>
  );
}
