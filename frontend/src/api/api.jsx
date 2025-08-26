// API client utilities for the frontend → backend communication
// Keeps all REST calls centralized for easy maintenance/refactoring
import axios from "axios";

// Base URL for FastAPI backend
const API_BASE = "http://127.0.0.1:8000"; // backend URL

// Upload a PDF file to the server
export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// Request backend to start processing a previously uploaded file
export const processFile = (file_id) => {
  return axios.post(`${API_BASE}/process`, { file_id });
};

// Fetch the current status (and result if available) for a job
export const getJobStatus = (job_id) => {
  return axios.get(`${API_BASE}/status/${job_id}`);
};

// Build a JSON blob from the latest job result. Caller triggers browser download.
export const downloadJobResultJson = async (job_id) => {
  const res = await getJobStatus(job_id);
  const result = res.data?.result || {};
  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
  return blob;
};
