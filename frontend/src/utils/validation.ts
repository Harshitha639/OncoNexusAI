import { z } from "zod";

/**
 * Shared Zod schemas for auth forms, kept in one place so validation
 * rules stay consistent with the backend's Pydantic contracts.
 */

export const loginSchema = z.object({
  email: z.string().min(1, "Email is required.").email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    full_name: z.string().trim().min(2, "Full name must be at least 2 characters."),
    email: z.string().min(1, "Email is required.").email("Enter a valid email address."),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .regex(/[A-Za-z]/, "Password must contain at least one letter.")
      .regex(/\d/, "Password must contain at least one number."),
    confirmPassword: z.string().min(1, "Please confirm your password."),
    role: z.enum(["patient", "doctor", "caregiver", "admin"]),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export type RegisterFormValues = z.infer<typeof registerSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().min(1, "Email is required.").email("Enter a valid email address."),
});

export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

const emptyToUndefined = (value: unknown) =>
  value === "" ? undefined : value;

export const patientProfileSchema = z.object({
  date_of_birth: z.preprocess(
    emptyToUndefined,
    z.string().optional(),
  ),

  gender: z.preprocess(
    emptyToUndefined,
    z.enum(["male", "female", "other", "prefer_not_to_say"]).optional(),
  ),

  phone_number: z.preprocess(
    emptyToUndefined,
    z.string().max(32).optional(),
  ),

  blood_group: z.preprocess(
    emptyToUndefined,
    z.enum([
      "A+",
      "A-",
      "B+",
      "B-",
      "AB+",
      "AB-",
      "O+",
      "O-",
      "unknown",
    ]).optional(),
  ),

  height_cm: z.preprocess(
    emptyToUndefined,
    z.coerce
      .number()
      .gt(0, "Height must be greater than 0.")
      .max(300, "Height must not exceed 300 cm.")
      .optional(),
  ),

  weight_kg: z.preprocess(
    emptyToUndefined,
    z.coerce
      .number()
      .gt(0, "Weight must be greater than 0.")
      .max(500, "Weight must not exceed 500 kg.")
      .optional(),
  ),

  address: z.preprocess(
    emptyToUndefined,
    z.string().max(2000).optional(),
  ),

  emergency_contact_name: z.preprocess(
    emptyToUndefined,
    z.string().max(255).optional(),
  ),

  emergency_contact_phone: z.preprocess(
    emptyToUndefined,
    z.string().max(32).optional(),
  ),

  emergency_contact_relationship: z.preprocess(
    emptyToUndefined,
    z.string().max(100).optional(),
  ),
});

export type PatientProfileFormValues = z.infer<
  typeof patientProfileSchema
>;

export const medicalProfileSchema = z.object({
  family_history: z.preprocess(
    emptyToUndefined,
    z.string().max(4000).optional(),
  ),

  allergies: z.preprocess(
    emptyToUndefined,
    z.string().max(2000).optional(),
  ),

  current_medications: z.preprocess(
    emptyToUndefined,
    z.string().max(2000).optional(),
  ),

  smoking_status: z.preprocess(
    emptyToUndefined,
    z.enum(["never", "former", "current"]).optional(),
  ),

  alcohol_consumption: z.preprocess(
    emptyToUndefined,
    z.enum(["never", "occasional", "regular", "frequent"]).optional(),
  ),
});

export type MedicalProfileFormValues = z.infer<
  typeof medicalProfileSchema
>;

export const reportUploadSchema = z.object({
  title: z.string().trim().min(1, "Title is required.").max(255),

  description: z.preprocess(
    emptyToUndefined,
    z.string().max(2000).optional(),
  ),
});

export type ReportUploadFormValues = z.infer<
  typeof reportUploadSchema
>;

export const appointmentSchema = z.object({
  doctor_name: z
    .string()
    .trim()
    .min(1, "Doctor name is required.")
    .max(255),

  department: z.preprocess(
    emptyToUndefined,
    z.string().max(255).optional(),
  ),

  scheduled_at: z
    .string()
    .min(1, "Please choose a date and time."),

  reason: z.preprocess(
    emptyToUndefined,
    z.string().max(2000).optional(),
  ),
});

export type AppointmentFormValues = z.infer<
  typeof appointmentSchema
>;