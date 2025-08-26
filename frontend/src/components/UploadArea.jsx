// Upload panel: drag-and-drop PDFs, then trigger upload + process
import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Paper, Typography, Button, Stack, Switch, FormControlLabel, Chip } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { uploadFile, processFile } from "../api/api";

const UploadArea = ({ setJobs, onError }) => {
  const [autoRoute, setAutoRoute] = useState(true);
  const [dataValidation, setDataValidation] = useState(true);

  // Single mutation that chains: upload → process
  const processMutation = useMutation({
    mutationFn: async ({ file }) => {
      const uploadRes = await uploadFile(file);
      const { file_id } = uploadRes.data;
      return processFile(file_id);
    },
    onSuccess: (res, variables) => {
      setJobs((prev) => [
        ...prev,
        { job_id: res.data.job_id, filename: variables.file.name },
      ]);
    },
    onError: (err) => onError?.(err?.response?.data?.detail || err.message),
  });

  // react-dropzone callback for dropped/selected files
  const onDrop = async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      try {
        await processMutation.mutateAsync({ file });
      } catch (_) {
        // handled by onError
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { "application/pdf": [".pdf"] } });

  return (
    <Stack spacing={5} sx={{ width: "100%" }}>
      {/* Drag-and-drop surface */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 7,
          textAlign: "center",
          border: "2px dashed",
          borderColor: isDragActive ? "primary.main" : "divider",
          bgcolor: isDragActive ? "action.hover" : "background.paper",
          cursor: "pointer",
          width: "100%",
        }}
      >
        <input {...getInputProps()} />
        <Typography variant="h6">Drop documents here</Typography>
        <Typography variant="body2" color="text.secondary">
          or click to browse files (PDF only)
        </Typography>
        <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 2 }}>
          <Chip size="small" label="PDF" />
          <Chip size="small" label="Max 50MB" />
        </Stack>
        <Button sx={{ mt: 2 }} variant="contained" disabled={processMutation.isPending}>
          {processMutation.isPending ? "Uploading..." : "Browse Files"}
        </Button>
      </Paper>

      {/* Optional toggles for future routing/validation controls */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Processing Configuration
        </Typography>
        <FormControlLabel
          control={<Switch checked={autoRoute} onChange={(e) => setAutoRoute(e.target.checked)} />}
          label="Smart Auto-Route"
        />
        <FormControlLabel
          control={<Switch checked={dataValidation} onChange={(e) => setDataValidation(e.target.checked)} />}
          label="Data Validation"
        />
      </Paper>
    </Stack>
  );
};

export default UploadArea;
