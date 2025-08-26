// Processing queue: tabs + live updates via Socket.IO and 5s polling
import React, { useEffect, useMemo, useState } from "react";
import { Tabs, Tab, Box } from "@mui/material";
import JobItem from "./JobItem";
import { useJobStatusesPolling } from "../hooks/useJobs";
import { socket } from "../lib/socket";

export default function StatusDashboard({ jobIds, onJobsUpdate }) {
  const [jobs, setJobs] = useState([]);
  const [tab, setTab] = useState(0);

  // React Query polling every 5s
  const { data: polledStatuses } = useJobStatusesPolling(jobIds);

  useEffect(() => {
    if (!polledStatuses) return;
    setJobs((prev) => {
      const map = new Map(prev.map((j) => [j.job_id, j]));
      polledStatuses.forEach((s) => {
        const existing = map.get(s.job_id) || {};
        map.set(s.job_id, { ...existing, ...s });
      });
      const next = Array.from(map.values());
      onJobsUpdate?.(next);
      return next;
    });
  }, [polledStatuses]);

  // Socket.IO live updates
  useEffect(() => {
    const handler = (data) => {
      if (!jobIds?.includes(data.job_id)) return;
      setJobs((prev) => {
        const idx = prev.findIndex((j) => j.job_id === data.job_id);
        if (idx !== -1) {
          const updated = [...prev];
          updated[idx] = { ...updated[idx], ...data };
          onJobsUpdate?.(updated);
          return updated;
        }
        const next = [...prev, data];
        onJobsUpdate?.(next);
        return next;
      });
    };
    socket.on("job_update", handler);
    return () => socket.off("job_update", handler);
  }, [jobIds]);

  const shownJobs = useMemo(() => {
    if (tab === 1) return jobs.filter((j) => j.status === "In-Progress" || j.status === "Validating");
    if (tab === 2) return jobs.filter((j) => j.status === "Completed");
    if (tab === 3) return jobs.filter((j) => j.status === "Failed");
    return jobs;
  }, [tab, jobs]);

  return (
    <Box sx={{ width: "100%" }}>
      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 2 }} variant="fullWidth">
        <Tab label="All" />
        <Tab label="Active" />
        <Tab label="Completed" />
        <Tab label="Failed" />
      </Tabs>
      <Box>
        {shownJobs.map((job) => (
          <JobItem
            key={job.job_id}
            job={job}
            onDelete={(id) =>
              setJobs((prev) => {
                const next = prev.filter((j) => j.job_id !== id);
                onJobsUpdate?.(next);
                return next;
              })
            }
          />
        ))}
      </Box>
    </Box>
  );
}
