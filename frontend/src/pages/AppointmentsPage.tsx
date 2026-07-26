import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { CalendarPlus, CalendarX2 } from "lucide-react";

import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { EmptyState } from "@/components/common/EmptyState";
import { FormField } from "@/components/common/FormField";
import { FullPageSpinner } from "@/components/common/Spinner";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { bookAppointment, cancelAppointment, listMyAppointments } from "@/services/appointmentService";
import { getApiErrorMessage } from "@/utils/apiError";
import { appointmentSchema, type AppointmentFormValues } from "@/utils/validation";
import type { AppointmentStatus } from "@/types/appointment";

const STATUS_VARIANT: Record<AppointmentStatus, BadgeVariant> = {
  scheduled: "info",
  completed: "success",
  cancelled: "destructive",
};

export function AppointmentsPage() {
  const queryClient = useQueryClient();
  const [pendingCancelId, setPendingCancelId] = useState<string | null>(null);

  const { data: appointments, isLoading } = useQuery({
    queryKey: ["appointments"],
    queryFn: listMyAppointments,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AppointmentFormValues>({ resolver: zodResolver(appointmentSchema) });

  const bookMutation = useMutation({
    mutationFn: (values: AppointmentFormValues) =>
      bookAppointment({
        doctor_name: values.doctor_name,
        department: values.department,
        scheduled_at: new Date(values.scheduled_at).toISOString(),
        reason: values.reason,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      toast.success("Appointment booked successfully.");
      reset();
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not book this appointment."));
    },
  });

  const cancelMutation = useMutation({
    mutationFn: cancelAppointment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      toast.success("Appointment cancelled.");
      setPendingCancelId(null);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not cancel this appointment."));
      setPendingCancelId(null);
    },
  });

  return (
    <div className="container flex flex-col gap-6 py-10">
      <div>
        <h1 className="text-2xl font-bold">Appointments</h1>
        <p className="text-sm text-muted-foreground">Book, view, and manage your appointments.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card variant="glass" className="flex flex-col gap-4 lg:col-span-1">
          <div className="flex items-center gap-2">
            <CalendarPlus className="h-5 w-5 text-primary" aria-hidden="true" />
            <h2 className="text-base font-semibold">Book an appointment</h2>
          </div>

          <form
            className="flex flex-col gap-4"
            onSubmit={handleSubmit((values) => bookMutation.mutate(values))}
            noValidate
          >
            <FormField label="Doctor name" htmlFor="doctor_name" error={errors.doctor_name?.message}>
              <Input id="doctor_name" placeholder="Dr. Jane Smith" {...register("doctor_name")} />
            </FormField>

            <FormField label="Department (optional)" htmlFor="department" error={errors.department?.message}>
              <Input id="department" placeholder="Oncology" {...register("department")} />
            </FormField>

            <FormField label="Date & time" htmlFor="scheduled_at" error={errors.scheduled_at?.message}>
              <Input id="scheduled_at" type="datetime-local" {...register("scheduled_at")} />
            </FormField>

            <FormField label="Reason (optional)" htmlFor="reason" error={errors.reason?.message}>
              <Textarea id="reason" placeholder="Follow-up consultation" {...register("reason")} />
            </FormField>

            <Button
              type="submit"
              className="h-11 w-auto self-end px-8"
              isLoading={isSubmitting || bookMutation.isPending}
            >
              Book appointment
            </Button>
          </form>
        </Card>

        <div className="flex flex-col gap-4 lg:col-span-2">
          {isLoading ? (
            <FullPageSpinner label="Loading appointments..." />
          ) : !appointments || appointments.length === 0 ? (
            <EmptyState
              icon={CalendarX2}
              title="No appointments yet"
              description="Book your first appointment using the form."
            />
          ) : (
            appointments
              .slice()
              .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime())
              .map((appointment) => (
                <Card
                  key={appointment.id}
                  variant="glass"
                  className="flex flex-col gap-2 p-5 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="font-semibold">{appointment.doctor_name}</p>
                    {appointment.department && (
                      <p className="text-sm text-muted-foreground">{appointment.department}</p>
                    )}
                    <p className="text-sm text-muted-foreground">
                      {new Date(appointment.scheduled_at).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </p>
                    {appointment.reason && (
                      <p className="mt-1 text-sm text-muted-foreground">{appointment.reason}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={STATUS_VARIANT[appointment.status]}>{appointment.status}</Badge>
                    {appointment.status === "scheduled" && (
                      <Button
                        variant="outline"
                        className="h-9 w-auto px-4"
                        onClick={() => setPendingCancelId(appointment.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </Card>
              ))
          )}
        </div>
      </div>

      <ConfirmDialog
        open={pendingCancelId !== null}
        title="Cancel this appointment?"
        description="You can always book a new appointment later."
        confirmLabel="Cancel appointment"
        isLoading={cancelMutation.isPending}
        onConfirm={() => pendingCancelId && cancelMutation.mutate(pendingCancelId)}
        onCancel={() => setPendingCancelId(null)}
      />
    </div>
  );
}
