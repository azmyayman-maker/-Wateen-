import { defaultTheme } from "react-admin";
import { ThemeOptions } from "@mui/material/styles";

export const theme: ThemeOptions = {
    ...defaultTheme,
    direction: "rtl",
    palette: {
        mode: 'dark',
        primary: {
            main: "#dd7bbb", // Based on GlowingEffect gradient
        },
        secondary: {
            main: "#d79f1e",
        },
        background: {
            default: "#0f172a", // slate-900
            paper: "rgba(15, 23, 42, 0.7)", // Transparent slate
        },
        text: {
            primary: "#f8fafc",
            secondary: "#94a3b8",
        },
    },
    typography: {
        fontFamily: "'Plus Jakarta Sans', sans-serif, 'Cairo', Arial",
    },
    components: {
        ...defaultTheme.components,
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    backgroundColor: "#0f172a",
                    backgroundImage: "radial-gradient(ellipse at top, #1e293b, transparent), radial-gradient(ellipse at bottom, #0f172a, transparent)",
                    backgroundAttachment: "fixed",
                }
            }
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    background: "rgba(30, 41, 59, 0.5)", // slate-800 semi-transparent
                    backdropFilter: "blur(16px)",
                    borderRadius: "16px",
                    boxShadow: "0 4px 30px rgba(0, 0, 0, 0.1)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    transition: "all 300ms ease",
                }
            }
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    background: "rgba(30, 41, 59, 0.6)",
                    backdropFilter: "blur(16px)",
                    borderRadius: "16px",
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                }
            }
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: "8px",
                    textTransform: "none",
                    fontWeight: 600,
                    boxShadow: "none",
                }
            }
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: "rgba(15, 23, 42, 0.5)",
                    backdropFilter: "blur(16px)",
                    color: "#f8fafc",
                    borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                    boxShadow: "none",
                }
            }
        },
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    backgroundColor: "rgba(15, 23, 42, 0.8)",
                    backdropFilter: "blur(20px)",
                    borderLeft: "1px solid rgba(255, 255, 255, 0.05)",
                }
            }
        }
    }
};
