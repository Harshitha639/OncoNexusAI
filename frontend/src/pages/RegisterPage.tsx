import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";

import { AlertBanner } from "@/components/common/AlertBanner";
import { FormField } from "@/components/common/FormField";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/contexts/AuthContext";
import { getApiErrorMessage } from "@/utils/apiError";
import { registerSchema, type RegisterFormValues } from "@/utils/validation";

const ROLE_OPTIONS: Array<{ value: RegisterFormValues["role"]; label: string }> = [
  { value: "patient", label: "Patient" },
  { value: "doctor", label: "Doctor" },
  { value: "caregiver", label: "Caregiver" },
  { value: "admin", label: "Admin" },
];

export function RegisterPage() {
  const { register: registerAccount } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "patient" },
  });

  async function onSubmit(values: RegisterFormValues) {
    setServerError(null);
    try {
      await registerAccount({
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        role: values.role,
      });
      navigate("/login", { state: { justRegistered: true } });
    } catch (error) {
      setServerError(getApiErrorMessage(error, "Could not create your account."));
    }
  }

  return (
    <Card>
      <h1 className="mb-1 text-2xl font-bold">Create your account</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Join OncoNexus AI to get started with personalized cancer care support.
      </p>

      {serverError && (
        <div className="mb-4">
          <AlertBanner variant="error" message={serverError} />
        </div>
      )}

      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormField label="Full name" htmlFor="full_name" error={errors.full_name?.message}>
          <Input
            id="full_name"
            autoComplete="name"
            placeholder="Jane Doe"
            {...register("full_name")}
          />
        </FormField>

        <FormField label="Email" htmlFor="email" error={errors.email?.message}>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            {...register("email")}
          />
        </FormField>

        <FormField label="I am a..." htmlFor="role" error={errors.role?.message}>
          <select
            id="role"
            className="h-11 w-full rounded-lg border border-border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            {...register("role")}
          >
            {ROLE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </FormField>

        <FormField label="Password" htmlFor="password" error={errors.password?.message}>
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            placeholder="At least 8 characters"
            {...register("password")}
          />
        </FormField>

        <FormField
          label="Confirm password"
          htmlFor="confirmPassword"
          error={errors.confirmPassword?.message}
        >
          <Input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            placeholder="Re-enter your password"
            {...register("confirmPassword")}
          />
        </FormField>

        <Button type="submit" isLoading={isSubmitting}>
          Create account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-primary hover:underline">
          Log in
        </Link>
      </p>
    </Card>
  );
}
