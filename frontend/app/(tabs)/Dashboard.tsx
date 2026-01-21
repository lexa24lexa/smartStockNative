import React, { useEffect, useMemo, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";

type CategoryStock = {
  category: string;
  total_stock: number;
};

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
  const [categories, setCategories] = useState<CategoryStock[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analytics/stock-by-category")
      .then((res) => res.json())
      .then(setCategories)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // 🔢 Derived metrics (frontend logic)
  const stats = useMemo(() => {
    const total = categories.length;
    const withStock = categories.filter((c) => c.total_stock > 0).length;
    const outOfStock = categories.filter((c) => c.total_stock === 0).length;

    const availability =
      total > 0 ? Math.round((withStock / total) * 100) : 0;

    return {
      availability,
      outOfStock,
      predictedRestocks: outOfStock, // proxy honesto
      activeCategories: total,
    };
  }, [categories]);

  return (
    <Layout>
      <Text style={styles.title}>Dashboard</Text>
      <Text style={styles.subtitle}>
        {loading ? "Loading data…" : "Updated just now"}
      </Text>

      {/* Stats */}
      <View style={styles.grid}>
        <StatCard
          value={`${stats.availability}%`}
          label="Stock availability"
          color="#059669"
        />
        <StatCard
          value={`${stats.outOfStock}`}
          label="Out of stock categories"
          color="#DC2626"
        />
        <StatCard
          value={`${stats.predictedRestocks}`}
          label="Predicted restocks"
          color="#2563EB"
        />
        <StatCard
          value={`${stats.activeCategories}`}
          label="Active categories"
          color="#1E40AF"
        />
      </View>

      {/* Chart */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Stock vs Sales by Category
        </Text>

        <View style={styles.chartPlaceholder}>
          <Text style={styles.chartText}>
            Bar chart (categories)
          </Text>
        </View>
      </View>

      {/* Low stock (demo / placeholder) */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Stores with Low Stock</Text>

        <Text style={styles.chartText}>
          Data not available with current backend
        </Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 22,
    fontWeight: "bold",
  },
  subtitle: {
    color: "#6B7280",
    marginBottom: 16,
  },

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
  chartText: {
    color: "#6B7280",
  },
});
