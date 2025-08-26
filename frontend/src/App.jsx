import React from "react";
import { CssBaseline, Box } from "@mui/material";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <Box sx={{ width: "100%", minHeight: "100vh" }}>
      <CssBaseline />
      <Navbar />
      <Dashboard />
    </Box>
  );
}

export default App;
