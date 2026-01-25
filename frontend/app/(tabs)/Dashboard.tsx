import React, { useEffect, useMemo, useState } from "react";
import { StyleSheet, Text, View, ScrollView, Dimensions } from "react-native";
import Svg, { Path, Line, Circle, Text as SvgText } from "react-native-svg";
import Layout from "../../components/ui/Layout";
import { Colors, Radius, Spacing, Font } from "../../constants/theme";

// Types
type CategoryStock = { category: string; total_stock: number };
type ReplenishmentItem = { product_id: number; product_name: string; current_stock: number; quantity: number | null };

// Stat card
function StatCard({ value, label, color }: { value: string; label: string; color: string }) {
  return (
    <View style={[styles.card, { backgroundColor: color }]}>
      <Text style={[Font.title, { color: "#fff" }]}>{value}</Text>
      <Text style={[Font.subtitle, { color: "#fff" }]}>{label}</Text>
    </View>
  );
}

// Progress bar
function ProgressBar({ value, maxValue }: { value: number; maxValue: number }) {
  const percentage = Math.min((value / maxValue) * 100, 100);
  let bgColor = Colors.primary;
  if (percentage < 50) bgColor = Colors.danger;
  else if (percentage < 80) bgColor = Colors.warning;

  return (
    <View style={styles.progressBarBackground}>
      <View style={[styles.progressBarFill, { width: `${percentage}%`, backgroundColor: bgColor }]} />
    </View>
  );
}

// Main dashboard
export default function Dashboard() {
  const [categories, setCategories] = useState<CategoryStock[]>([]);
  const [replenishments, setReplenishments] = useState<ReplenishmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const storeId = 1;

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

  useEffect(() => { fetchData(); }, []);
  useEffect(() => { const interval = setInterval(fetchData, 30 * 60 * 1000); return () => clearInterval(interval); }, []);
  const [tick, setTick] = useState(0);
  useEffect(() => { const interval = setInterval(() => setTick(prev => prev + 1), 60000); return () => clearInterval(interval); }, []);

  const getUpdatedText = () => {
    if (!lastUpdated) return "Loading…";
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (diff < 60) return "Updated just now";
    if (diff < 3600) return `Updated ${Math.floor(diff / 60)} min ago`;
    return `Updated ${Math.floor(diff / 3600)} h ago`;
  };

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

  // Chart setup
  const chartWidth = Dimensions.get("window").width - Spacing.m * 2;
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
      <ScrollView contentContainerStyle={{ padding: Spacing.m, backgroundColor: Colors.bgPage }}>
        <Text style={Font.title}>Dashboard</Text>
        <Text style={Font.subtitle}>{loading ? "Loading…" : getUpdatedText()}</Text>

        {/* Stats */}
        <View style={styles.grid}>
          <StatCard value={`${stats.availability}%`} label="Stock availability" color={Colors.primary} />
          <StatCard value={`${stats.outOfStock}`} label="Out of stock categories" color={Colors.danger} />
          <StatCard value={`${stats.predictedRestocks}`} label="Predicted restocks" color={Colors.secondary} />
          <StatCard value={`${stats.activeCategories}`} label="Active categories" color={Colors.secondary} />
        </View>

        {/* Stock vs Sales chart */}
        <View style={styles.section}>
          <Text style={[Font.label, { marginBottom: 12 }]}>Stock vs Sales Trend</Text>
          <Svg width="100%" height={chartHeight}>
            {yAxisValues.map((v, i) => {
              const y = yScale(v);
              return (
                <React.Fragment key={i}>
                  <Line x1={padding} y1={y} x2={chartWidth - padding} y2={y} stroke={Colors.border} strokeWidth={1} />
                  <SvgText x={padding - 6} y={y + 4} fontSize={10} fill={Colors.textSecondary} textAnchor="end">{v}</SvgText>
                </React.Fragment>
              );
            })}
            <Path d={lineStock} stroke={Colors.primary} strokeWidth={2} fill="none" />
            <Path d={lineSales} stroke={Colors.secondary} strokeWidth={2} fill="none" />
            {stockValues.map((v, i) => <Circle key={`s${i}`} cx={xScale(i)} cy={yScale(v)} r={4} fill={Colors.primary} />)}
            {salesValues.map((v, i) => <Circle key={`sa${i}`} cx={xScale(i)} cy={yScale(v)} r={4} fill={Colors.secondary} />)}
            {labels.map((l, i) => <SvgText key={i} x={xScale(i)} y={chartHeight - padding + 14} fontSize={10} fill={Colors.textSecondary} textAnchor="middle">{l}</SvgText>)}
          </Svg>
          <View style={styles.legend}>
            <View style={styles.legendItem}><View style={[styles.legendColorBox, { backgroundColor: Colors.primary }]} /><Text style={Font.subtitle}>Stock</Text></View>
            <View style={styles.legendItem}><View style={[styles.legendColorBox, { backgroundColor: Colors.secondary }]} /><Text style={Font.subtitle}>Sales</Text></View>
          </View>
        </View>

        {/* Low stock */}
        <View style={styles.section}>
          <Text style={[Font.label, { marginBottom: 12 }]}>Low Stock Products (&lt;50)</Text>
          {lowStockItems.length === 0 ? <Text style={Font.subtitle}>All products have sufficient stock.</Text> :
            lowStockItems.map(item => {
              const maxStock = item.quantity || 100;
              return (
                <View key={item.product_id} style={styles.lowStockRow}>
                  <Text style={[Font.label, { marginBottom: 4 }]}>{item.product_name}</Text>
                  <Text style={{ ...Font.label, fontWeight: "bold" as const, color: Colors.danger, marginBottom: 4 }}>{item.current_stock}</Text>
                  <ProgressBar value={item.current_stock} maxValue={maxStock} />
                </View>
              );
            })}
        </View>
      </ScrollView>
    </Layout>
  );
}

const styles = StyleSheet.create({
  grid: { flexDirection: "row", flexWrap: "wrap", gap: Spacing.s },
  card: { width: "48%", padding: Spacing.m, borderRadius: Radius.card },
  section: { marginTop: Spacing.l, backgroundColor: Colors.bgCard, padding: Spacing.m, borderRadius: Radius.card },
  progressBarBackground: { height: 8, backgroundColor: Colors.border, borderRadius: Radius.small },
  progressBarFill: { height: "100%", borderRadius: Radius.small },
  legend: { flexDirection: "row", marginTop: 8, gap: 16 },
  legendItem: { flexDirection: "row", alignItems: "center" },
  legendColorBox: { width: 12, height: 12, borderRadius: 2 },
  lowStockRow: { marginBottom: 12 },
});
