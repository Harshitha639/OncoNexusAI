import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { AxiosError } from "axios";
import { Stethoscope, UserRound } from "lucide-react";

import { FormField } from "@/components/common/FormField";
import { FullPageSpinner } from "@/components/common/Spinner";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Textarea } from "@/components/ui/Textarea";
import {
  createMyProfile,
  fetchMyProfile,
  updateMyProfile,
} from "@/services/patientProfileService";
import { getApiErrorMessage } from "@/utils/apiError";
import { medicalProfileSchema, type MedicalProfileFormValues } from "@/utils/validation";

export function MedicalProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["patient-profile"],
    queryFn: fetchMyProfile,
    retry: false,
    throwOnError: (error) => !(error instanceof AxiosError && error.response?.status === 404),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<MedicalProfileFormValues>({ resolver: zodResolver(medicalProfileSchema) });

  useEffect(() => {
    if (profile) {
      reset({
        family_history: profile.family_history ?? "",
        allergies: profile.allergies ?? "",
        current_medications: profile.current_medications ?? "",
        smoking_status: profile.smoking_status ?? undefined,
        alcohol_consumption: profile.alcohol_consumption ?? undefined,
      });
    }
  }, [profile, reset]);

  const saveMutation = useMutation({
    mutationFn: (values: MedicalProfileFormValues) =>
      profile ? updateMyProfile(values) : createMyProfile(values),
    onSuccess: (updated) => {
      queryClient.setQueryData(["patient-profile"], updated);
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Medical profile saved successfully.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not save your medical profile."));
    },
  });

  if (isLoading) {
    return <FullPageSpinner label="Loading your medical profile..." />;
  }

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div>
        <h1 className="text-2xl font-bold">Medical profile</h1>
        <p className="text-sm text-muted-foreground">
          Family history, allergies, medications, and lifestyle factors.
        </p>
      </div>

      <div className="flex gap-2">
        <Link
          to="/profile/patient"
          className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-muted-foreground hover:bg-muted"
        >
          <UserRound className="h-4 w-4" aria-hidden="true" /> Patient profile
        </Link>
        <span className="flex items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary">
          <Stethoscope className="h-4 w-4" aria-hidden="true" /> Medical profile
        </span>
      </div>

      <Card variant="glass" className="max-w-3xl">
        <form
          className="flex flex-col gap-4"
          onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
          noValidate
        >
          <FormField
            label="Family history"
            htmlFor="family_history"
            error={errors.family_history?.message}
          >
            <Textarea
              id="family_history"
              placeholder="e.g. Mother — breast cancer at age 52"
              {...register("family_history")}
            />
          </FormField>

          <FormField label="Allergies" htmlFor="allergies" error={errors.allergies?.message}>
            <Textarea
              id="allergies"
              placeholder="e.g. Penicillin, latex"
              {...register("allergies")}
            />
          </FormField>

          <FormField
            label="Current medications"
            htmlFor="current_medications"
            error={errors.current_medications?.message}
          >
            <Textarea
              id="current_medications"
              placeholder="e.g. Tamoxifen 20mg daily"
              {...register("current_medications")}
            />
          </FormField>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormField
              label="Smoking status"
              htmlFor="smoking_status"
              error={errors.smoking_status?.message}
            >
              <Select id="smoking_status" {...register("smoking_status")}>
                <option value="">Select...</option>
                <option value="never">Never</option>
                <option value="former">Former</option>
                <option value="current">Current</option>
              </Select>
            </FormField>

            <FormField
              label="Alcohol consumption"
              htmlFor="alcohol_consumption"
              error={errors.alcohol_consumption?.message}
            >
              <Select id="alcohol_consumption" {...register("alcohol_consumption")}>
                <option value="">Select...</option>
                <option value="never">Never</option>
                <option value="occasional">Occasional</option>
                <option value="regular">Regular</option>
                <option value="frequent">Frequent</option>
              </Select>
            </FormField>
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              className="h-11 w-auto px-8"
              isLoading={isSubmitting || saveMutation.isPending}
              disabled={!isDirty && Boolean(profile)}
            >
              Save changes
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
