import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View, ActivityIndicator } from "react-native";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import Layout from "../../components/ui/Layout";

dayjs.extend(relativeTime);

const API_BASE_URL = "http://127.0.0.1:8000";
const STORE_ID = 1;

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
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(
      `${API_BASE_URL}/analytics/predictions?store_id=${STORE_ID}`
    )
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load predictions");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Layout>
        <View style={styles.center}>
          <ActivityIndicator size="large" />
        </View>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout>
        <View style={styles.center}>
          <Text style={styles.errorText}>
            {error ?? "Something went wrong"}
          </Text>
        </View>
      </Layout>
    );
  }

  return (
    <Layout>
      <Text style={styles.subtitle}>
        Updated {dayjs(data.last_updated).fromNow()}
      </Text>

      <Text style={styles.title}>Predictive overview</Text>

      {/* Info cards */}
      <View style={styles.infoGrid}>
        <InfoCard
          title="Forecast accuracy"
          value={`${Math.round(data.forecast_accuracy * 100)}%`}
        />
        <InfoCard
          title="Next restock needed"
          value={
            data.next_restock_in_days
              ? `in ${data.next_restock_in_days}d.`
              : "—"
          }
        />
      </View>

      {/* Chart placeholder */}
      <View style={styles.chartCard}>
        <View style={styles.chartPlaceholder} />
      </View>

      <Text style={styles.sectionTitle}>Automatic predictions</Text>

      {/* Predictions list */}
      <View style={styles.listCard}>
        {data.predictions.map((p: any) => {
          const color =
            p.predicted_stock_change_pct <= -20
              ? "#DC2626"
              : p.predicted_stock_change_pct < 0
              ? "#F59E0B"
              : "#059669";

          return (
            <PredictionRow
              key={p.product_id}
              product={p.product_name}
              value={`${p.predicted_stock_change_pct}% stock`}
              note={
                p.days_until_restock
                  ? `Restock in ${p.days_until_restock} days.`
                  : "No restock planned."
              }
              color={color}
            />
          );
        })}
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    color: "#DC2626",
    fontSize: 16,
  },

  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
  },
  subtitle: {
    color: "#6B7280",
    marginBottom: 4,
  },

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
