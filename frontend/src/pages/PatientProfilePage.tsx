import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { AxiosError } from "axios";
import { HeartPulse, Stethoscope, UserRound } from "lucide-react";

import { FormField } from "@/components/common/FormField";
import { FullPageSpinner } from "@/components/common/Spinner";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import {
  createMyProfile,
  fetchMyProfile,
  updateMyProfile,
} from "@/services/patientProfileService";
import { getApiErrorMessage } from "@/utils/apiError";
import { patientProfileSchema, type PatientProfileFormValues } from "@/utils/validation";

export function PatientProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["patient-profile"],
    queryFn: fetchMyProfile,
    retry: false,
    // A 404 (no profile yet) is an expected, normal state here.
    throwOnError: (error) => !(error instanceof AxiosError && error.response?.status === 404),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<PatientProfileFormValues>({ resolver: zodResolver(patientProfileSchema) });

  useEffect(() => {
    if (profile) {
      reset({
        date_of_birth: profile.date_of_birth ?? "",
        gender: profile.gender ?? undefined,
        phone_number: profile.phone_number ?? "",
        blood_group: profile.blood_group ?? undefined,
        height_cm: profile.height_cm ?? undefined,
        weight_kg: profile.weight_kg ?? undefined,
        address: profile.address ?? "",
        emergency_contact_name: profile.emergency_contact_name ?? "",
        emergency_contact_phone: profile.emergency_contact_phone ?? "",
        emergency_contact_relationship: profile.emergency_contact_relationship ?? "",
      });
    }
  }, [profile, reset]);

  const saveMutation = useMutation({
    mutationFn: (values: PatientProfileFormValues) =>
      profile ? updateMyProfile(values) : createMyProfile(values),
    onSuccess: (updated) => {
      queryClient.setQueryData(["patient-profile"], updated);
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Profile saved successfully.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not save your profile."));
    },
  });

  if (isLoading) {
    return <FullPageSpinner label="Loading your profile..." />;
  }

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div>
        <h1 className="text-2xl font-bold">Patient profile</h1>
        <p className="text-sm text-muted-foreground">
          Your personal and demographic information.
        </p>
      </div>

      <div className="flex gap-2">
        <span className="flex items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary">
          <UserRound className="h-4 w-4" aria-hidden="true" /> Patient profile
        </span>
        <Link
          to="/profile/medical"
          className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-muted-foreground hover:bg-muted"
        >
          <Stethoscope className="h-4 w-4" aria-hidden="true" /> Medical profile
        </Link>
      </div>

      <Card variant="glass" className="max-w-3xl">
        <form
          className="grid grid-cols-1 gap-4 sm:grid-cols-2"
          onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
          noValidate
        >
          <FormField label="Date of birth" htmlFor="date_of_birth" error={errors.date_of_birth?.message}>
            <Input id="date_of_birth" type="date" {...register("date_of_birth")} />
          </FormField>

          <FormField label="Gender" htmlFor="gender" error={errors.gender?.message}>
            <Select id="gender" {...register("gender")}>
              <option value="">Select...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </Select>
          </FormField>

          <FormField label="Phone number" htmlFor="phone_number" error={errors.phone_number?.message}>
            <Input id="phone_number" placeholder="+1 555 010 0000" {...register("phone_number")} />
          </FormField>

          <FormField label="Blood group" htmlFor="blood_group" error={errors.blood_group?.message}>
            <Select id="blood_group" {...register("blood_group")}>
              <option value="">Select...</option>
              {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown"].map((bg) => (
                <option key={bg} value={bg}>
                  {bg === "unknown" ? "Unknown" : bg}
                </option>
              ))}
            </Select>
          </FormField>

          <FormField label="Height (cm)" htmlFor="height_cm" error={errors.height_cm?.message}>
            <Input id="height_cm" type="number" step="0.1" {...register("height_cm")} />
          </FormField>

          <FormField label="Weight (kg)" htmlFor="weight_kg" error={errors.weight_kg?.message}>
            <Input id="weight_kg" type="number" step="0.1" {...register("weight_kg")} />
          </FormField>

          <div className="sm:col-span-2">
            <FormField label="Address" htmlFor="address" error={errors.address?.message}>
              <Input id="address" placeholder="Street, city, state, ZIP" {...register("address")} />
            </FormField>
          </div>

          <div className="sm:col-span-2 mt-2 flex items-center gap-2 text-sm font-semibold text-muted-foreground">
            <HeartPulse className="h-4 w-4" aria-hidden="true" /> Emergency contact
          </div>

          <FormField
            label="Contact name"
            htmlFor="emergency_contact_name"
            error={errors.emergency_contact_name?.message}
          >
            <Input id="emergency_contact_name" {...register("emergency_contact_name")} />
          </FormField>

          <FormField
            label="Contact phone"
            htmlFor="emergency_contact_phone"
            error={errors.emergency_contact_phone?.message}
          >
            <Input id="emergency_contact_phone" {...register("emergency_contact_phone")} />
          </FormField>

          <div className="sm:col-span-2">
            <FormField
              label="Relationship"
              htmlFor="emergency_contact_relationship"
              error={errors.emergency_contact_relationship?.message}
            >
              <Input
                id="emergency_contact_relationship"
                placeholder="e.g. Spouse, Parent, Sibling"
                {...register("emergency_contact_relationship")}
              />
            </FormField>
          </div>

          <div className="sm:col-span-2 flex justify-end">
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
