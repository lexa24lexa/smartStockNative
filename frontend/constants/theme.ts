// constants/theme.ts
// import { StyleSheet } from "react-native";

export const Colors = {
  primary: "#059669",
  secondary: "#2563EB",
  warning: "#F59E0B",
  danger: "#DC2626",
  textPrimary: "#111827",
  textSecondary: "#6B7280",
  bgCard: "#fff",
  bgPage: "#F3F4F6",
  border: "#E5E7EB",
  success: "#10B981",
};

export const Radius = {
  card: 12,
  button: 10,
  small: 4,
};

export const Spacing = {
  xs: 4,
  s: 8,
  m: 16,
  l: 24,
};

export const Font = {
  title: { fontSize: 22, fontWeight: "bold" as const, color: Colors.textPrimary },
  subtitle: { fontSize: 16, color: Colors.textSecondary },
  label: { fontWeight: "600" as const, color: Colors.textPrimary },
  button: { fontWeight: "600" as const, color: Colors.primary, textAlign: "center" as const },
  meta: { fontSize: 12, color: Colors.textSecondary },
};

