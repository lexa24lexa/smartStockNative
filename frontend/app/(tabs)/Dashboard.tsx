import React, { useEffect, useMemo, useState } from "react";
import { StyleSheet, Text, View, ScrollView, Dimensions } from "react-native";
import Svg, { Path, Line, Circle, Text as SvgText } from "react-native-svg";
import Layout from "../../components/ui/Layout";

type CategoryStock = { category: string; total_stock: number };
type ReplenishmentItem = {
  product_id: number;
  product_name: string;
  current_stock: number;
  quantity: number | null;
};

function StatCard({ value, label, color }: { value: string; label: string; color: string }) {
  return (
    <View style={[styles.card, { backgroundColor: color }]}>
      <Text style={styles.cardValue}>{value}</Text>
      <Text style={styles.cardLabel}>{label}</Text>
    </View>
  );
}

function ProgressBar({ value, maxValue }: { value: number; maxValue: number }) {
  const percentage = Math.min((value / maxValue) * 100, 100);
  let bgColor = "#059669";
  if (percentage < 50) bgColor = "#DC2626";
  else if (percentage < 80) bgColor = "#F59E0B";

  return (
    <View style={styles.progressBarBackground}>
      <View style={[styles.progressBarFill, { width: `${percentage}%`, backgroundColor: bgColor }]} />
    </View>
  );
}

export default function Dashboard() {
  const [categories, setCategories] = useState<CategoryStock[]>([]);
  const [replenishments, setReplenishments] = useState<ReplenishmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const storeId = 1;

  // --- Fetch data ---
  const fetchData = async () => {
    setLoading(true);
    try {
      const catRes = await fetch("http://127.0.0.1:8000/analytics/stock-by-category");
      const catData: CategoryStock[] = await catRes.json();
      const lowRes = await fetch(`http://127.0.0.1:8000/analytics/low-stock?store_id=${storeId}`);
      const lowData: ReplenishmentItem[] = await lowRes.json();
      setCategories(catData);
      setReplenishments(lowData);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // --- Initial fetch ---
  useEffect(() => {
    fetchData();
  }, []);

  // --- Auto refresh every 30 minutes ---
  useEffect(() => {
    const interval = setInterval(fetchData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // --- Timer for "last updated" label ---
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setTick(prev => prev + 1), 60000);
    return () => clearInterval(interval);
  }, []);

  const getUpdatedText = () => {
    if (!lastUpdated) return "Loading…";
    // use tick to trigger re-render every minute
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (diff < 60) return "Updated just now";
    if (diff < 3600) return `Updated ${Math.floor(diff / 60)} min ago`;
    return `Updated ${Math.floor(diff / 3600)} h ago`;
  };

  // --- Stats ---
  const stats = useMemo(() => {
    const total = categories.length;
    const outOfStock = categories.filter(c => c.total_stock === 0).length;
    return {
      availability: total ? Math.round(((total - outOfStock) / total) * 100) : 0,
      outOfStock,
      predictedRestocks: replenishments.length,
      activeCategories: total,
    };
  }, [categories, replenishments]);

  const lowStockItems = useMemo(() => replenishments.filter(i => i.current_stock < 50), [replenishments]);

  // --- Chart ---
  const chartWidth = Dimensions.get("window").width - 32;
  const chartHeight = 220;
  const padding = 40;
  const stockValues = categories.map(c => c.total_stock);
  const salesValues = categories.map(() => Math.floor(Math.random() * 200));
  const labels = categories.map(c => c.category);
  const maxValue = Math.max(...stockValues, ...salesValues, 1);
  const chartInnerWidth = chartWidth - 2 * padding;
  const xScale = (i: number) => (categories.length === 1 ? padding + chartInnerWidth / 2 : padding + (i / (categories.length - 1)) * chartInnerWidth);
  const yScale = (v: number) => padding + (1 - v / maxValue) * (chartHeight - 2 * padding);
  const createPath = (values: number[]) => values.map((v, i) => `${i === 0 ? "M" : "L"}${xScale(i)},${yScale(v)}`).join(" ");
  const lineStock = createPath(stockValues);
  const lineSales = createPath(salesValues);
  const yAxisValues = [0, 0.25, 0.5, 0.75, 1].map(f => Math.round(maxValue * f));

  return (
    <Layout onRefresh={fetchData}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.title}>Dashboard</Text>
        <Text style={styles.subtitle}>{loading ? "Loading…" : getUpdatedText()}</Text>

        <View style={styles.grid}>
          <StatCard value={`${stats.availability}%`} label="Stock availability" color="#059669" />
          <StatCard value={`${stats.outOfStock}`} label="Out of stock categories" color="#DC2626" />
          <StatCard value={`${stats.predictedRestocks}`} label="Predicted restocks" color="#2563EB" />
          <StatCard value={`${stats.activeCategories}`} label="Active categories" color="#1E40AF" />
        </View>

        {/* Stock vs Sales Chart */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Stock vs Sales Trend</Text>
          <Svg width="100%" height={chartHeight}>
            {yAxisValues.map((v, i) => {
              const y = yScale(v);
              return (
                <React.Fragment key={i}>
                  <Line x1={padding} y1={y} x2={chartWidth - padding} y2={y} stroke="#E5E7EB" strokeWidth={1} />
                  <SvgText x={padding - 6} y={y + 4} fontSize={10} fill="#6B7280" textAnchor="end">
                    {v}
                  </SvgText>
                </React.Fragment>
              );
            })}
            <Path d={lineStock} stroke="#059669" strokeWidth={2} fill="none" />
            <Path d={lineSales} stroke="#2563EB" strokeWidth={2} fill="none" />
            {stockValues.map((v, i) => <Circle key={`s${i}`} cx={xScale(i)} cy={yScale(v)} r={4} fill="#059669" />)}
            {salesValues.map((v, i) => <Circle key={`sa${i}`} cx={xScale(i)} cy={yScale(v)} r={4} fill="#2563EB" />)}
            {labels.map((l, i) => (
              <SvgText key={i} x={xScale(i)} y={chartHeight - padding + 14} fontSize={10} fill="#6B7280" textAnchor="middle">
                {l}
              </SvgText>
            ))}
          </Svg>

          <View style={styles.legend}>
            <View style={styles.legendItem}>
              <View style={[styles.legendColorBox, { backgroundColor: "#059669" }]} />
              <Text style={styles.legendLabel}>Stock</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColorBox, { backgroundColor: "#2563EB" }]} />
              <Text style={styles.legendLabel}>Sales</Text>
            </View>
          </View>
        </View>

        {/* Low Stock */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Low Stock Products (&lt;50)</Text>
          {lowStockItems.length === 0 ? (
            <Text style={styles.chartText}>All products have sufficient stock.</Text>
          ) : (
            lowStockItems.map(item => {
              const maxStock = item.quantity || 100;
              return (
                <View key={item.product_id} style={styles.lowStockRow}>
                  <Text style={styles.lowStockName}>{item.product_name}</Text>
                  <Text style={styles.lowStockQty}>{item.current_stock}</Text>
                  <ProgressBar value={item.current_stock} maxValue={maxStock} />
                </View>
              );
            })
          )}
        </View>
      </ScrollView>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold" },
  subtitle: { color: "#6B7280", marginBottom: 16 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  card: { width: "48%", padding: 16, borderRadius: 12 },
  cardValue: { fontSize: 22, fontWeight: "bold", color: "#fff" },
  cardLabel: { color: "#fff", marginTop: 4 },
  section: { marginTop: 24, backgroundColor: "#fff", padding: 16, borderRadius: 12 },
  sectionTitle: { fontWeight: "600", marginBottom: 12 },
  chartText: { color: "#6B7280" },
  lowStockRow: { marginBottom: 12 },
  lowStockName: { fontWeight: "500", marginBottom: 4 },
  lowStockQty: { fontWeight: "bold", color: "#DC2626", marginBottom: 4 },
  progressBarBackground: { height: 8, backgroundColor: "#E5E7EB", borderRadius: 4 },
  progressBarFill: { height: "100%", borderRadius: 4 },
  legend: { flexDirection: "row", marginTop: 8, gap: 16 },
  legendItem: { flexDirection: "row", alignItems: "center" },
  legendColorBox: { width: 12, height: 12, borderRadius: 2 },
  legendLabel: { marginLeft: 4, fontSize: 12 },
});
