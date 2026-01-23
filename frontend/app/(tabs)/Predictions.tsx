import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View, ActivityIndicator, Dimensions, ScrollView } from "react-native";
import { BarChart } from "react-native-chart-kit";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import Layout from "../../components/ui/Layout";

dayjs.extend(relativeTime);

const API_BASE_URL = "http://127.0.0.1:8000";
const STORE_ID = 1;

export default function Predictions() {
  const [data, setData] = useState<any>(null);
  const [stockSales, setStockSales] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const predictionsRes = await fetch(`${API_BASE_URL}/analytics/predictions?store_id=${STORE_ID}`);
        if (!predictionsRes.ok) throw new Error("Failed to fetch predictions");
        const predictionsData = await predictionsRes.json();

        const stockSalesRes = await fetch(`${API_BASE_URL}/analytics/stock-vs-sales`);
        if (!stockSalesRes.ok) throw new Error("Failed to fetch stock vs sales");
        const stockSalesData = await stockSalesRes.json();

        setData(predictionsData);
        setStockSales(stockSalesData);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <Layout><View style={styles.center}><ActivityIndicator size="large" /></View></Layout>;
  if (error || !data) return <Layout><View style={styles.center}><Text style={styles.errorText}>{error ?? "Something went wrong"}</Text></View></Layout>;

  const categories = stockSales.map(c => c.category);
  const stockValues = stockSales.map(c => c.stock);
  const salesValues = stockSales.map(c => c.sales);

  const chartData = {
    labels: categories,
    datasets: [
      { data: stockValues, color: () => "#059669" },
      { data: salesValues, color: () => "#F59E0B" },
    ],
  };

  const screenWidth = Dimensions.get("window").width - 32;

  return (
    <Layout>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.subtitle}>Updated {dayjs(data.last_updated).fromNow()}</Text>
        <Text style={styles.title}>Stock vs Sales Trend</Text>

        <View style={styles.chartCard}>
          <BarChart
            data={chartData}
            width={screenWidth}
            height={220}
            fromZero
            yAxisLabel=""
            yAxisSuffix=""
            chartConfig={{
              backgroundColor: "#fff",
              backgroundGradientFrom: "#fff",
              backgroundGradientTo: "#fff",
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
              barPercentage: 0.4,
            }}
            verticalLabelRotation={30}
            withInnerLines
            showBarTops
          />
          <View style={styles.legendRow}>
            <View style={styles.legendItem}><View style={[styles.dot, { backgroundColor: "#059669" }]} /><Text>Stock</Text></View>
            <View style={styles.legendItem}><View style={[styles.dot, { backgroundColor: "#F59E0B" }]} /><Text>Sales</Text></View>
          </View>
        </View>

        {/* Predictions list */}
        <Text style={styles.sectionTitle}>Automatic predictions</Text>
        <View style={styles.listCard}>
          {data.predictions.map((p: any) => {
            const color = p.predicted_stock_change_pct <= -20 ? "#DC2626" : p.predicted_stock_change_pct < 0 ? "#F59E0B" : "#059669";
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

function PredictionRow({ product, value, note, color }: { product: string; value: string; note: string; color: string }) {
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

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  errorText: { color: "#DC2626", fontSize: 16 },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280", marginBottom: 8 },
  chartCard: { backgroundColor: "#fff", padding: 12, borderRadius: 12, marginBottom: 20 },
  legendRow: { flexDirection: "row", justifyContent: "flex-start", marginTop: 8, gap: 16 },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  sectionTitle: { fontWeight: "600", marginBottom: 12 },
  listCard: { backgroundColor: "#fff", borderRadius: 12, padding: 16, gap: 16 },
  predictionRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  rowLeft: { flexDirection: "row", alignItems: "center", gap: 8 },
  product: { fontWeight: "600" },
  percent: { fontWeight: "600" },
  meta: { fontSize: 12, color: "#6B7280" },
});
