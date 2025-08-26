import React from "react";
import StatusDashboard from "./StatusDashboard";
import { Typography, Box } from "@mui/material";

const ProcessingQueue = ({ jobs, jobIds, onJobsUpdate }) => {
  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Processing Queue
      </Typography>
      <StatusDashboard jobIds={jobIds} onJobsUpdate={onJobsUpdate} />
    </Box>
  );
};

export default ProcessingQueue;


