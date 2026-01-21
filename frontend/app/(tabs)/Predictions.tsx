import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";

function InfoCard({ title, value }: { title: string; value: string }) {
  return (
    <View style={styles.infoCard}>
      <Text style={styles.infoTitle}>{title}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function PredictionRow({
  product,
  value,
  note,
  color,
}: {
  product: string;
  value: string;
  note: string;
  color: string;
}) {
  return (
    <View style={styles.predictionRow}>
      <View style={styles.rowLeft}>
        <View style={[styles.dot, { backgroundColor: color }]} />
        <Text style={styles.product}>{product}</Text>
      </View>
      <View style={{ alignItems: "flex-end" }}>
        <Text style={[styles.percent, { color }]}>{value}</Text>
        <Text style={styles.meta}>{note}</Text>
      </View>
    </View>
  );
}

export default function Predictions() {
  return (
    <Layout>
      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Predictive overview</Text>

      <View style={styles.infoGrid}>
        <InfoCard title="Forecast accuracy" value="89%" />
        <InfoCard title="Next restock needed" value="in 2d." />
      </View>

      <View style={styles.chartCard}>
        <View style={styles.chartPlaceholder} />
      </View>

      <Text style={styles.sectionTitle}>Automatic predictions</Text>

      <View style={styles.listCard}>
        <PredictionRow
          product="Product B"
          value="-25% stock"
          note="Restock tomorrow."
          color="#DC2626"
        />
        <PredictionRow
          product="Product C"
          value="+5% stock"
          note="Restock in 2 days."
          color="#F59E0B"
        />
        <PredictionRow
          product="Product D"
          value="+45% stock"
          note="Restock in 3.5 days."
          color="#059669"
        />
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280", marginBottom: 4 },

  infoGrid: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  infoCard: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
  },
  infoTitle: {
    color: "#6B7280",
    fontSize: 13,
  },
  infoValue: {
    fontSize: 20,
    fontWeight: "700",
    marginTop: 6,
  },

  chartCard: {
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 12,
    marginBottom: 20,
  },
  chartPlaceholder: {
    height: 160,
    backgroundColor: "#E5E7EB",
    borderRadius: 8,
  },

  sectionTitle: {
    fontWeight: "600",
    marginBottom: 12,
  },

  listCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    gap: 16,
  },

  predictionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  rowLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  product: {
    fontWeight: "600",
  },
  percent: {
    fontWeight: "600",
  },
  meta: {
    fontSize: 12,
    color: "#6B7280",
  },
});
