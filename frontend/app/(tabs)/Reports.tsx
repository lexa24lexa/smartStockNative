import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View, ActivityIndicator, Dimensions, TouchableOpacity, Platform } from "react-native";
import { Picker } from "@react-native-picker/picker";
import { LineChart } from "react-native-chart-kit";
import Layout from "../../components/ui/Layout";
import * as FileSystem from "expo-file-system";
import * as Sharing from "expo-sharing";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

// Types
type TopProduct = { product_id: number; name: string; qty_sold: number; revenue: number };
type Category = { category_id: number; category_name: string };
type Report = { sale_count: number; total_items_sold: number; total_revenue: number; top_products?: TopProduct[] };

export default function Reports() {
  const storeId = 1;
  const today = new Date();

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  const [year, setYear] = useState<number>(today.getFullYear());
  const [month, setMonth] = useState<number>(today.getMonth() + 1);
  const [day, setDay] = useState<string>(today.toISOString().slice(0, 10));
  const [reportType, setReportType] = useState<"monthly" | "daily">("monthly");

  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);

  // Fetch categories for filter
  const fetchCategories = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/categories`);
      const data = await res.json();
      setCategories(data);
    } catch (err) {
      console.error("Failed to fetch categories", err);
    }
  };

  // Fetch report data with filters
  const fetchReport = async () => {
    setLoading(true);
    try {
      let url = `http://127.0.0.1:8000/reports/${reportType}?store_id=${storeId}&format=json`;

      if (reportType === "monthly") url += `&year=${year}&month=${month}`;
      else url += `&report_date=${day}`;

      if (selectedCategory) url += `&category_id=${selectedCategory}`;
      if (selectedProduct) url += `&product_id=${selectedProduct}`;

      const res = await fetch(url);
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error(err);
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  // Export report (PDF or Excel)
  const exportReport = async (format: "pdf" | "excel") => {
    try {
      const fileExt = format === "pdf" ? "pdf" : "xlsx";
      const url = `http://127.0.0.1:8000/stock/${storeId}/daily-report?report_date=${day}&format=${format}`;

      if (Platform.OS === "web") {
        window.open(url, "_blank");
        return;
      }

      const dir = (FileSystem as any).cacheDirectory || (FileSystem as any).documentDirectory;
      const localUri = `${dir}report-${day}.${fileExt}`;

      const downloadResumable = FileSystem.createDownloadResumable(url, localUri);
      const { uri } = await downloadResumable.downloadAsync();

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(uri);
      } else {
        alert("Sharing not available. File downloaded to: " + uri);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to export report: " + err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCategories(); }, []);
  useEffect(() => { fetchReport(); }, [year, month, day, reportType, selectedCategory, selectedProduct]);

  useEffect(() => {
    if (!loading && report === null) {
      alert("No report data available for the selected period.");
    }
  }, [loading, report]);

  const daysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();

  if (loading) return <Layout><ActivityIndicator size="large" color={Colors.primary} /></Layout>;

  const topProducts = report?.top_products ?? [];
  const chartData = {
    labels: topProducts.map(p => p.name),
    datasets: [{ data: topProducts.map(p => p.qty_sold), color: () => Colors.primary, strokeWidth: 2 }],
    legend: ["Qty Sold"],
  };

  return (
    <Layout>
      <Text style={Font.title}>Reports</Text>

      {/* Filters */}
      <View style={{ marginBottom: Spacing.s }}>
        <Text style={Font.label}>Year</Text>
        <Picker selectedValue={year} onValueChange={setYear} style={{ height: 40 }}>
          {Array.from({ length: 5 }, (_, i) => today.getFullYear() - i).map(y => <Picker.Item key={y} label={`${y}`} value={y} />)}
        </Picker>

        <Text style={Font.label}>Month</Text>
        <Picker selectedValue={month} onValueChange={setMonth} style={{ height: 40 }}>
          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => <Picker.Item key={m} label={`${m}`} value={m} />)}
        </Picker>

        {reportType === "daily" && (
          <>
            <Text style={Font.label}>Day</Text>
            <Picker selectedValue={day} onValueChange={setDay} style={{ height: 40 }}>
              {Array.from({ length: daysInMonth(year, month) }, (_, i) => {
                const value = `${year}-${month.toString().padStart(2,"0")}-${(i+1).toString().padStart(2,"0")}`;
                return <Picker.Item key={value} label={`${i+1}`} value={value} />;
              })}
            </Picker>
          </>
        )}

        <Text style={Font.label}>Category</Text>
        <Picker selectedValue={selectedCategory ?? 0} onValueChange={(val) => setSelectedCategory(val === 0 ? null : val)} style={{ height: 40 }}>
          <Picker.Item label="All" value={0} />
          {categories.map(cat => <Picker.Item key={cat.category_id} label={cat.category_name} value={cat.category_id} />)}
        </Picker>

        {topProducts.length > 0 && (
          <>
            <Text style={Font.label}>Product</Text>
            <Picker selectedValue={selectedProduct ?? 0} onValueChange={(val) => setSelectedProduct(val === 0 ? null : val)} style={{ height: 40 }}>
              <Picker.Item label="All" value={0} />
              {topProducts.map(p => <Picker.Item key={p.product_id} label={p.name} value={p.product_id} />)}
            </Picker>
          </>
        )}
      </View>

      {/* Monthly/Daily toggle */}
      <View style={{ flexDirection: "row", marginVertical: Spacing.s }}>
        <TouchableOpacity style={[styles.button, reportType === "monthly" && styles.activeButton]} onPress={() => setReportType("monthly")}>
          <Text style={[Font.label, reportType === "monthly" && { color: Colors.bgCard, fontWeight: "600" }]}>Monthly</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, reportType === "daily" && styles.activeButton]} onPress={() => setReportType("daily")}>
          <Text style={[Font.label, reportType === "daily" && { color: Colors.bgCard, fontWeight: "600" }]}>Daily</Text>
        </TouchableOpacity>
      </View>

      {/* Export buttons */}
      <View style={{ flexDirection: "row", justifyContent: "space-around", marginTop: Spacing.m }}>
        <TouchableOpacity style={styles.exportButton} onPress={() => exportReport("pdf")}>
          <Text style={[Font.label, { color: Colors.bgCard, textAlign: "center" }]}>Export PDF</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.exportButton} onPress={() => exportReport("excel")}>
          <Text style={[Font.label, { color: Colors.bgCard, textAlign: "center" }]}>Export Excel</Text>
        </TouchableOpacity>
      </View>

      {/* Chart */}
      {topProducts.length > 0 ? (
        <>
          <Text style={Font.subtitle}>Top Products Sold</Text>
          <LineChart
            data={chartData}
            width={Dimensions.get("window").width - Spacing.m * 2}
            height={220}
            yAxisLabel=""
            chartConfig={{
              backgroundColor: Colors.bgCard,
              backgroundGradientFrom: Colors.bgCard,
              backgroundGradientTo: Colors.bgCard,
              decimalPlaces: 0,
              color: () => Colors.primary,
              labelColor: () => Colors.textSecondary,
              style: { borderRadius: Radius.card },
            }}
            style={{ borderRadius: Radius.card, marginVertical: Spacing.m }}
          />
        </>
      ) : (
        <Text style={[Font.meta, { marginVertical: Spacing.m }]}>No product sales data available</Text>
      )}

      {/* Table */}
      <View style={{ backgroundColor: Colors.bgCard, padding: Spacing.m, borderRadius: Radius.card }}>
        <View style={{ flexDirection: "row", paddingVertical: Spacing.s }}>
          <Text style={[Font.label, { flex: 3 }]}>Product</Text>
          <Text style={[Font.label, { flex: 1, textAlign: "center" }]}>Qty Sold</Text>
          <Text style={[Font.label, { flex: 1, textAlign: "center" }]}>Revenue</Text>
        </View>
        <View style={{ height: 1, backgroundColor: Colors.border, marginVertical: Spacing.s }} />
        {topProducts.length > 0 ? (
          topProducts.map((p) => (
            <View key={p.product_id} style={{ flexDirection: "row", paddingVertical: Spacing.s }}>
              <Text style={[Font.meta, { flex: 3 }]}>{p.name}</Text>
              <Text style={[Font.meta, { flex: 1, textAlign: "center" }]}>{p.qty_sold}</Text>
              <Text style={[Font.meta, { flex: 1, textAlign: "center" }]}>{p.revenue?.toFixed(2) ?? "0.00"}</Text>
            </View>
          ))
        ) : (
          <Text style={[Font.meta, { marginTop: Spacing.s }]}>No product sales data available</Text>
        )}
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  button: { flex: 1, padding: Spacing.s, backgroundColor: Colors.border, borderRadius: Radius.small, alignItems: "center", marginHorizontal: Spacing.s },
  activeButton: { backgroundColor: Colors.primary },
  exportButton: { backgroundColor: Colors.primary, padding: Spacing.s, borderRadius: Radius.small, flex: 1, marginHorizontal: Spacing.s },
});
