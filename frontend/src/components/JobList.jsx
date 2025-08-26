import React from "react";
import JobItem from "./JobItem";

const JobList = ({ jobs, setJobs }) => {
  return (
    <div>
      {jobs.map((job) => (
        <JobItem key={job.job_id} job={job} setJobs={setJobs} />
      ))}
    </div>
  );
};

export default JobList;
