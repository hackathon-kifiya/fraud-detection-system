import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Paper,
  IconButton,
  Tooltip,
} from "@mui/material";
import { ContentCopy as CopyIcon } from "@mui/icons-material";
import { userAPI } from "../services/api";

const LoginPage = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleCopyCredentials = (email, password) => {
    setFormData({
      email: email,
      password: password,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await userAPI.login(formData);
      const { token, user } = response.data;

      localStorage.setItem("authToken", token);
      localStorage.setItem("user", JSON.stringify(user));

      onLogin(user);
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        bgcolor: "#f5f5f5",
      }}
    >
      {/* Left Side - Logo and Branding */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "#023737",
          color: "white",
          p: 4,
        }}
      >
        <Box sx={{ textAlign: "center", maxWidth: 500 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mb: 3,
            }}
          >
            <img
              src='/logo.svg'
              alt='MAX Logo'
              style={{ width: 144, height: 144, marginRight: 12 }}
            />
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 3,
                  mb: 1.5,
                }}
              >
                <Typography
                  variant='h5'
                  sx={{
                    fontWeight: "bold",
                    color: "white",
                    lineHeight: 1,
                    fontSize: "3.5rem",
                  }}
                >
                  MAX
                </Typography>
                <Typography
                  variant='body2'
                  sx={{
                    color: "#bdbdbd",
                    fontWeight: "medium",
                    fontSize: "1.2rem",
                  }}
                >
                  v0.1.0
                </Typography>
              </Box>
              <Typography
                variant='body2'
                sx={{
                  color: "#bdbdbd",
                  fontSize: "1.7rem",
                  lineHeight: 1,
                  fontWeight: "normal",
                }}
              >
                Fraud Detection System
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Right Side - Login Form */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 4,
        }}
      >
        <Paper elevation={3} sx={{ width: "100%", maxWidth: 400 }}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: "center", mb: 3 }}>
                <Typography variant='h4' component='h1' gutterBottom>
                  Welcome Back
                </Typography>
                <Typography variant='body1' color='text.secondary'>
                  Sign in to your account
                </Typography>
              </Box>

              {error && (
                <Alert severity='error' sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label='Email'
                  name='email'
                  type='email'
                  value={formData.email}
                  onChange={handleChange}
                  margin='normal'
                  required
                  autoComplete='email'
                />
                <TextField
                  fullWidth
                  label='Password'
                  name='password'
                  type='password'
                  value={formData.password}
                  onChange={handleChange}
                  margin='normal'
                  required
                  autoComplete='current-password'
                />
                <Button
                  type='submit'
                  fullWidth
                  variant='contained'
                  sx={{
                    mt: 3,
                    mb: 2,
                    bgcolor: "#ff9800",
                    "&:hover": { bgcolor: "#f57c00" },
                  }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Sign In"}
                </Button>
              </form>

              <Box sx={{ textAlign: "center", mt: 2 }}>
                <Typography
                  variant='body2'
                  color='text.secondary'
                  sx={{ mb: 1 }}
                >
                  Demo credentials:
                </Typography>

                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1,
                    mb: 0.5,
                  }}
                >
                  <Typography variant='body2' color='text.secondary'>
                    admin@fraud-detection.com / admin123
                  </Typography>
                  <Tooltip title='Use these credentials'>
                    <IconButton
                      size='small'
                      onClick={() =>
                        handleCopyCredentials(
                          "admin@fraud-detection.com",
                          "admin123"
                        )
                      }
                      sx={{ p: 0.5 }}
                    >
                      <CopyIcon sx={{ fontSize: "1rem" }} />
                    </IconButton>
                  </Tooltip>
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1,
                    mb: 0.5,
                  }}
                >
                  <Typography variant='body2' color='text.secondary'>
                    analyst@fraud-detection.com / analyst123
                  </Typography>
                  <Tooltip title='Use these credentials'>
                    <IconButton
                      size='small'
                      onClick={() =>
                        handleCopyCredentials(
                          "analyst@fraud-detection.com",
                          "analyst123"
                        )
                      }
                      sx={{ p: 0.5 }}
                    >
                      <CopyIcon sx={{ fontSize: "1rem" }} />
                    </IconButton>
                  </Tooltip>
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1,
                  }}
                >
                  <Typography variant='body2' color='text.secondary'>
                    viewer@fraud-detection.com / viewer123
                  </Typography>
                  <Tooltip title='Use these credentials'>
                    <IconButton
                      size='small'
                      onClick={() =>
                        handleCopyCredentials(
                          "viewer@fraud-detection.com",
                          "viewer123"
                        )
                      }
                      sx={{ p: 0.5 }}
                    >
                      <CopyIcon sx={{ fontSize: "1rem" }} />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Box>
    </Box>
  );
};

export default LoginPage;
