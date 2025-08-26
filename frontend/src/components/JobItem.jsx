// Single job row: status chip, progress, and actions (view, download, delete)
import React, { useState } from "react";
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import VisibilityIcon from "@mui/icons-material/Visibility";
import DeleteIcon from "@mui/icons-material/Delete";
import { getJobStatus, downloadJobResultJson } from "../api/api";

const statusColors = {
  "In-Progress": "warning",
  Validating: "info",
  Completed: "success",
  Failed: "error",
};

const JobItem = ({ job, onDelete }) => {
  const [open, setOpen] = useState(false);
  const [result, setResult] = useState(job.result || null);
  const [loading, setLoading] = useState(false);

  const handleView = async () => {
    setOpen(true);
    try {
      setLoading(true);
      const res = await getJobStatus(job.job_id);
      setResult(res.data?.result || null);
    } finally {
      setLoading(false);
    }
  };

  const isDone = job.status === "Completed" || job.status === "Failed";

  return (
    <Box
      sx={{
        p: 2,
        mb: 2,
        borderRadius: 3,
        bgcolor: "background.paper",
        boxShadow: 1,
      }}
    >
      {/* Top Row: Filename + Status */}
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        mb={1}
      >
        <Typography variant="subtitle1" fontWeight={600}>
          {job.filename || `Job ${job.job_id?.slice(0, 6)}`}
        </Typography>
        <Chip
          label={job.status}
          color={statusColors[job.status] || "default"}
          size="small"
          sx={{ fontWeight: 600 }}
        />
      </Stack>

      {/* Progress Bar */}
      {!isDone && (
        <LinearProgress
          variant="indeterminate"
          color="primary"
          sx={{ borderRadius: 1, height: 6, mb: 1 }}
        />
      )}

      {/* Metadata Row */}
      <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
        <Typography variant="caption" color="text.secondary">
          Job ID: {job.job_id}
        </Typography>
        {isDone && (
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" startIcon={<VisibilityIcon />} onClick={handleView}>
              View Output
            </Button>
            <Tooltip title="Download JSON result">
              <IconButton
                size="small"
                color="primary"
                onClick={async () => {
                  const blob = await downloadJobResultJson(job.job_id);
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `${job.filename || job.job_id}_result.json`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                }}
              >
                <DownloadIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete job from list">
              <IconButton size="small" color="error" onClick={() => onDelete?.(job.job_id)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        )}
      </Stack>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Output Preview</DialogTitle>
        <DialogContent dividers>
          {loading && <Typography variant="body2">Loading...</Typography>}
          {!loading && !result && (
            <Typography variant="body2" color="text.secondary">No result available.</Typography>
          )}
          {!loading && result && (
            <Box>
              <Typography variant="subtitle2">Summary</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Pages: {result.pages} • Tables: {result.table_count}
              </Typography>
              {Array.isArray(result.tables) && result.tables.length > 0 && (
                <Box>
                  {result.tables.map((t, idx) => (
                    <Box key={idx} sx={{ mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {result.table_titles?.[idx] || `Table ${idx + 1}`}
                      </Typography>
                      <Box component="pre" sx={{ p: 1, bgcolor: "grey.50", borderRadius: 1, whiteSpace: "pre-wrap", fontSize: 12 }}>
                        {(t.content || []).join("\n")}
                      </Box>
                    </Box>
            ))}
          </Box>
        )}
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default JobItem;
