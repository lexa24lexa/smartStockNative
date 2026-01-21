import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";

export default function Reports() {
  return (
    <Layout>
      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Reports</Text>

      <View style={styles.filters}>
        <View style={styles.filterCard}>
          <Text style={styles.filterLabel}>Select report type</Text>
          <Text style={styles.filterValue}>Graphic ▾</Text>
        </View>

        <View style={styles.filterCard}>
          <Text style={styles.filterLabel}>Data range</Text>
          <Text style={styles.filterValue}>20-01-2025</Text>
          <Text style={styles.filterValue}>20-02-2025</Text>
        </View>
      </View>

      <View style={styles.chartCard}>
        <View style={styles.chartPlaceholder} />

        <View style={styles.tooltip}>
          <Text style={styles.tooltipTitle}>Detailed Breakdown -</Text>
          <Text style={styles.tooltipSubtitle}>August 2023</Text>

          <View style={styles.tooltipRow}>
            <Text>● Product A</Text>
            <Text>150 units</Text>
          </View>
          <View style={styles.tooltipRow}>
            <Text>● Product B</Text>
            <Text>50 units</Text>
          </View>
          <View style={styles.tooltipRow}>
            <Text>● Product C</Text>
            <Text>75 units</Text>
          </View>
        </View>
      </View>

      <View style={styles.table}>
        <Text style={styles.tableHeader}>Date     Product     Sales Qty</Text>
        <Text style={styles.tableRow}>—        —           —</Text>
        <Text style={styles.tableRow}>—        —           —</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280", marginBottom: 4 },

  filters: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  filterCard: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 12,
  },
  filterLabel: {
    color: "#6B7280",
    fontSize: 12,
  },
  filterValue: {
    marginTop: 4,
    fontWeight: "600",
  },

  chartCard: {
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  chartPlaceholder: {
    height: 160,
    backgroundColor: "#E5E7EB",
    borderRadius: 8,
  },

  tooltip: {
    position: "absolute",
    left: 20,
    bottom: 20,
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 10,
    elevation: 3,
  },
  tooltipTitle: {
    fontWeight: "600",
  },
  tooltipSubtitle: {
    marginBottom: 8,
  },
  tooltipRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },

  table: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
  },
  tableHeader: {
    fontWeight: "600",
    marginBottom: 8,
  },
  tableRow: {
    color: "#6B7280",
  },
});
