// Main dashboard layout: header, KPIs, upload panel, and queue
import React, { useMemo, useState } from "react";
import { Box, Grid, Snackbar, Alert } from "@mui/material";
import UploadArea from "../components/UploadArea";
import ProcessingQueue from "../components/ProcessingQueue";
import StatsCards from "../components/StatsCards";

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  const jobIds = useMemo(() => jobs.map((j) => j.job_id), [jobs]);

  return (
    <Box sx={{ mt: 3, mb: 6, px: { xs: 10, md: 4 } }}>
      {/* Top Statistics */}
      <StatsCards
        totals={{
          totalProcessed: jobs.filter((j) => j.status === "Completed").length,
          inProgress: jobs.filter((j) => j.status === "In-Progress").length,
          validating: jobs.filter((j) => j.status === "Validating").length,
          successRate:
            jobs.filter((j) => j.status === "Completed").length +
            jobs.filter((j) => j.status === "Failed").length
              ? `${(
                  (jobs.filter((j) => j.status === "Completed").length /
                    (jobs.filter((j) => j.status === "Completed").length +
                      jobs.filter((j) => j.status === "Failed").length)) *
                  100
                ).toFixed(1)}%`
              : "0%",
        }}
      />

      {/* Main Content */}
      <Grid container spacing={5} sx={{ mt: 3 }}>
        {/* Upload Section */}
        <Grid item xs={14} md={5}>
          <UploadArea setJobs={setJobs} onError={setError} />
        </Grid>

        {/* Processing Queue */}
        <Grid item xs={12} md={8}>
          <ProcessingQueue jobs={jobs} jobIds={jobIds} onJobsUpdate={setJobs} />
        </Grid>
      </Grid>

      {/* Global Error Snackbar */}
      <Snackbar
        open={Boolean(error)}
        autoHideDuration={4000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ width: "100%" }}
        >
          {String(error)}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Dashboard;
