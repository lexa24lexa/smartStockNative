import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View, ActivityIndicator, Dimensions, ScrollView } from "react-native";
import { BarChart } from "react-native-chart-kit";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import Layout from "../../components/ui/Layout";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

dayjs.extend(relativeTime);

const API_BASE_URL = "http://127.0.0.1:8000";
const STORE_ID = 1;

// Main Predictions screen
export default function Predictions() {
  // State
  const [data, setData] = useState<any>(null); // Prediction data
  const [stockSales, setStockSales] = useState<any[]>([]); // Stock vs sales data
  const [loading, setLoading] = useState(true); // Loading indicator
  const [error, setError] = useState<string | null>(null); // Error state

  // Fetch data on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch predictions
        const predictionsRes = await fetch(`${API_BASE_URL}/analytics/predictions?store_id=${STORE_ID}`);
        if (!predictionsRes.ok) throw new Error("Failed to fetch predictions");
        const predictionsData = await predictionsRes.json();

        // Fetch stock vs sales
        const stockSalesRes = await fetch(`${API_BASE_URL}/analytics/stock-vs-sales`);
        if (!stockSalesRes.ok) throw new Error("Failed to fetch stock vs sales");
        const stockSalesData = await stockSalesRes.json();

        setData(predictionsData); // Save predictions
        setStockSales(stockSalesData); // Save stock vs sales
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error"); // Save error
      } finally {
        setLoading(false); // Stop loading
      }
    };

    fetchData();
  }, []);

  // Loading state
  if (loading) return (
    <Layout>
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    </Layout>
  );

  // Error or no data
  if (error || !data) return (
    <Layout>
      <View style={styles.center}>
        <Text style={[Font.meta, { color: Colors.danger }]}>{error ?? "Something went wrong"}</Text>
      </View>
    </Layout>
  );

  // Prepare chart data
  const categories = stockSales.map(c => c.category);
  const stockValues = stockSales.map(c => c.stock);
  const salesValues = stockSales.map(c => c.sales);

  const chartData = {
    labels: categories,
    datasets: [
      { data: stockValues, color: () => Colors.primary },
      { data: salesValues, color: () => Colors.warning },
    ],
  };

  const screenWidth = Dimensions.get("window").width - Spacing.m * 2;

  return (
    <Layout>
      <ScrollView contentContainerStyle={{ padding: Spacing.m }}>
        {/* Last updated */}
        <Text style={Font.subtitle}>Updated {dayjs(data.last_updated).fromNow()}</Text>
        <Text style={Font.title}>Stock vs Sales Trend</Text>

        {/* Bar chart: Stock vs Sales */}
        <View style={styles.chartCard}>
          <BarChart
            data={chartData}
            width={screenWidth}
            height={220}
            fromZero
            yAxisLabel=""
            yAxisSuffix=""
            chartConfig={{
              backgroundColor: Colors.bgCard,
              backgroundGradientFrom: Colors.bgCard,
              backgroundGradientTo: Colors.bgCard,
              decimalPlaces: 0,
              color: () => Colors.textPrimary,
              labelColor: () => Colors.textSecondary,
              barPercentage: 0.4,
            }}
            verticalLabelRotation={30}
            withInnerLines
            showBarTops
          />
          {/* Chart legend */}
          <View style={styles.legendRow}>
            <View style={styles.legendItem}>
              <View style={[styles.dot, { backgroundColor: Colors.primary }]} />
              <Text style={Font.label}>Stock</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.dot, { backgroundColor: Colors.warning }]} />
              <Text style={Font.label}>Sales</Text>
            </View>
          </View>
        </View>

        {/* Predictions list */}
        <Text style={Font.label}>Automatic predictions</Text>
        <View style={styles.listCard}>
          {data.predictions.map((p: any) => {
            const color = p.predicted_stock_change_pct <= -20
              ? Colors.danger
              : p.predicted_stock_change_pct < 0
              ? Colors.warning
              : Colors.primary;
            return (
              <PredictionRow
                key={p.product_id}
                product={p.product_name}
                value={`${p.predicted_stock_change_pct}% stock`}
                note={p.days_until_restock ? `Restock in ${p.days_until_restock} days.` : "No restock planned."}
                color={color}
              />
            );
          })}
        </View>
      </ScrollView>
    </Layout>
  );
}

// Single prediction row
function PredictionRow({ product, value, note, color }: { product: string; value: string; note: string; color: string }) {
  return (
    <View style={styles.predictionRow}>
      {/* Product info */}
      <View style={styles.rowLeft}>
        <View style={[styles.dot, { backgroundColor: color }]} />
        <Text style={Font.label}>{product}</Text>
      </View>
      {/* Predicted value & note */}
      <View style={{ alignItems: "flex-end" }}>
        <Text style={[Font.label, { color, fontWeight: "600" }]}>{value}</Text>
        <Text style={Font.meta}>{note}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  chartCard: { backgroundColor: Colors.bgCard, padding: Spacing.m, borderRadius: Radius.card, marginBottom: Spacing.l },
  legendRow: { flexDirection: "row", marginTop: Spacing.s, gap: Spacing.m },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  listCard: { backgroundColor: Colors.bgCard, borderRadius: Radius.card, padding: Spacing.m, gap: Spacing.s },
  predictionRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  rowLeft: { flexDirection: "row", alignItems: "center", gap: 8 },
});
