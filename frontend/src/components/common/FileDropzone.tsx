import { useCallback, useRef, useState, type DragEvent } from "react";
import { FileCheck2, UploadCloud } from "lucide-react";

import { cn } from "@/utils/cn";

const ACCEPTED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"];
const MAX_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB

interface FileDropzoneProps {
  file: File | null;
  onFileSelected: (file: File | null) => void;
  error?: string;
}

function isAcceptedFile(file: File): boolean {
  const lowerName = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
}

/** Drag-and-drop + click-to-browse file picker for report uploads (PDF/JPG/JPEG/PNG, max 20MB). */
export function FileDropzone({ file, onFileSelected, error }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const validateAndSet = useCallback(
    (candidate: File | null) => {
      if (!candidate) {
        onFileSelected(null);
        return;
      }
      if (!isAcceptedFile(candidate)) {
        setLocalError("Only PDF, JPG, JPEG, or PNG files are supported.");
        return;
      }
      if (candidate.size > MAX_SIZE_BYTES) {
        setLocalError("File exceeds the maximum upload size of 20 MB.");
        return;
      }
      setLocalError(null);
      onFileSelected(candidate);
    },
    [onFileSelected],
  );

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const dropped = event.dataTransfer.files?.[0] ?? null;
    validateAndSet(dropped);
  }

  const displayError = error ?? localError ?? undefined;

  return (
    <div className="flex flex-col gap-2">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 text-center transition-colors",
          isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50",
          displayError && "border-destructive",
        )}
      >
        {file ? (
          <>
            <FileCheck2 className="h-8 w-8 text-secondary" aria-hidden="true" />
            <p className="text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </>
        ) : (
          <>
            <UploadCloud className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
            <p className="text-sm font-medium">Drag & drop your report here, or click to browse</p>
            <p className="text-xs text-muted-foreground">PDF, JPG, JPEG, or PNG — max 20 MB</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          className="hidden"
          onChange={(event) => validateAndSet(event.target.files?.[0] ?? null)}
        />
      </div>
      {displayError && <p className="text-xs text-destructive">{displayError}</p>}
    </div>
  );
}
