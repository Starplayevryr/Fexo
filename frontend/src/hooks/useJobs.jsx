import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { socket } from "../lib/socket";
import { getJobStatus } from "../api/api";

export const useJobStatusSocket = (jobId) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    // Listen for status updates for this job
    socket.emit("subscribe", { job_id: jobId });

    socket.on("job_update", (data) => {
      if (data.job_id === jobId) {
        setStatus(data);
        setLoading(false);
      }
    });

    socket.on("connect_error", (err) => {
      setError(err.message);
      setLoading(false);
    });

    return () => {
      // Cleanup on unmount
      socket.emit("unsubscribe", { job_id: jobId });
      socket.off("job_update");
      socket.off("connect_error");
    };
  }, [jobId]);

  return { status, loading, error };
};

// Poll multiple job IDs every 5s using React Query
export const useJobStatusesPolling = (jobIds) => {
  return useQuery({
    queryKey: ["job-statuses", jobIds],
    queryFn: async () => {
      if (!jobIds || jobIds.length === 0) return [];
      const results = await Promise.all(
        jobIds.map(async (id) => {
          try {
            const res = await getJobStatus(id);
            return res.data; // { job_id, status, result? }
          } catch (e) {
            return { job_id: id, status: "Unknown" };
          }
        })
      );
      return results;
    },
    refetchInterval: 5000,
    enabled: Boolean(jobIds && jobIds.length > 0),
    staleTime: 1000,
  });
};
