import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Layout from "../components/ui/Layout";

function StatCard({
  value,
  label,
  color,
}: {
  value: string;
  label: string;
  color: string;
}) {
  return (
    <View style={[styles.card, { backgroundColor: color }]}>
      <Text style={styles.cardValue}>{value}</Text>
      <Text style={styles.cardLabel}>{label}</Text>
    </View>
  );
}

export default function Dashboard() {
  return (
    <Layout>
      <Text style={styles.title}>Dashboard</Text>
      <Text style={styles.subtitle}>Updated 5min ago</Text>

      <View style={styles.grid}>
        <StatCard value="92%" label="Stock availability" color="#059669" />
        <StatCard value="34" label="Out of stock" color="#DC2626" />
        <StatCard value="120" label="Predicted Restocks" color="#2563EB" />
        <StatCard value="15" label="Stores connected" color="#1E40AF" />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Stock vs Sales Trend</Text>
        <View style={styles.chartPlaceholder}>
          <Text style={styles.chartText}>Chart placeholder</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Stores with Low Stock</Text>

        <View style={styles.storeRow}>
          <Text>⚠️ Traugutta</Text>
          <View style={styles.redBar} />
        </View>

        <View style={styles.storeRow}>
          <Text>⚠️ Grunwaldzki</Text>
          <View style={styles.greenBar} />
        </View>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold" },
  subtitle: { color: "#6B7280", marginBottom: 16 },

  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },

  card: {
    width: "48%",
    padding: 16,
    borderRadius: 12,
  },
  cardValue: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#fff",
  },
  cardLabel: {
    color: "#fff",
    marginTop: 4,
  },

  section: {
    marginTop: 24,
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontWeight: "600",
    marginBottom: 12,
  },

  chartPlaceholder: {
    height: 160,
    backgroundColor: "#E5E7EB",
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
  },
  chartText: { color: "#6B7280" },

  storeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: 8,
  },
  redBar: {
    width: 80,
    height: 6,
    backgroundColor: "#DC2626",
    borderRadius: 3,
  },
  greenBar: {
    width: 80,
    height: 6,
    backgroundColor: "#059669",
    borderRadius: 3,
  },
});
