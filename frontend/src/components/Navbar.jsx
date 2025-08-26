import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import { motion } from "framer-motion";

const Navbar = () => {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <motion.div
          initial={{ x: -200, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <Typography variant="h6" component="div">
            Document LLM Dashboard
          </Typography>
        </motion.div>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
