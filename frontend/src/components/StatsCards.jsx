// KPI summary cards at the top of the dashboard
import React from "react";
import { Grid, Paper, Typography, Stack, Avatar } from "@mui/material";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import VerifiedIcon from "@mui/icons-material/Verified";
import PercentIcon from "@mui/icons-material/Percent";

const Card = ({ title, value, subtitle, icon, color }) => (
  <Paper
    sx={{
      p: 3,
      minHeight: 150,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      borderRadius: 3,
      transition: "all 0.3s ease",
      "&:hover": {
        transform: "translateY(-6px)",
        boxShadow: 6,
      },
    }}
    variant="outlined"
  >
    <Stack spacing={0.5}>
      <Typography variant="caption" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="h5" fontWeight="bold">
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="caption" color="success.main">
          {subtitle}
        </Typography>
      )}
    </Stack>
    <Avatar
      sx={{
        bgcolor: `${color}.light`,
        color: `${color}.dark`,
        width: 56,
        height: 56,
      }}
    >
      {icon}
    </Avatar>
  </Paper>
);

const StatsCards = ({ totals }) => {
  return (
    <Grid
      container
      spacing={4}
      sx={{
        width: "100%",
        maxWidth: "100%", // makes the cards spread wider
        px: { xs: 2, md: 6 }, // less empty side space
        mx: "auto",
      }}
    >
      <Grid item xs={12} sm={6} md={3}>
        <Card
          title="Total Processed"
          value={totals?.totalProcessed ?? "—"}
          subtitle="+18% from last week"
          icon={<DoneAllIcon fontSize="medium" />}
          color="success"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card
          title="In Progress"
          value={totals?.inProgress ?? "—"}
          icon={<PendingActionsIcon fontSize="medium" />}
          color="warning"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card
          title="Validating"
          value={totals?.validating ?? "—"}
          icon={<VerifiedIcon fontSize="medium" />}
          color="info"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card
          title="Success Rate"
          value={totals?.successRate ?? "—"}
          subtitle="+2.6% improvement"
          icon={<PercentIcon fontSize="medium" />}
          color="primary"
        />
      </Grid>
    </Grid>
  );
};

export default StatsCards;
