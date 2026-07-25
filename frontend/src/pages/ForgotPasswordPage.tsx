import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";

import { AlertBanner } from "@/components/common/AlertBanner";
import { FormField } from "@/components/common/FormField";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/utils/validation";

/**
 * UI-only forgot-password flow. There is no `/auth/forgot-password`
 * backend endpoint yet (out of scope for this milestone) — submitting
 * this form only confirms the request was captured client-side.
 */
export function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({ resolver: zodResolver(forgotPasswordSchema) });

  async function onSubmit(_values: ForgotPasswordFormValues) {
    // Placeholder until a backend password-reset endpoint exists.
    await new Promise((resolve) => setTimeout(resolve, 400));
    setSubmitted(true);
  }

  return (
    <Card>
      <h1 className="mb-1 text-2xl font-bold">Reset your password</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Enter your account email and we'll send you a link to reset your password.
      </p>

      {submitted ? (
        <AlertBanner
          variant="success"
          message="If an account exists for that email, a reset link is on its way."
        />
      ) : (
        <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <FormField label="Email" htmlFor="email" error={errors.email?.message}>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              {...register("email")}
            />
          </FormField>

          <Button type="submit" isLoading={isSubmitting}>
            Send reset link
          </Button>
        </form>
      )}

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Remembered your password?{" "}
        <Link to="/login" className="font-medium text-primary hover:underline">
          Log in
        </Link>
      </p>
    </Card>
  );
}
