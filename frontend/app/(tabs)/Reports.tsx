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

  // Fetch report data
  const fetchReport = async () => {
    setLoading(true);
    try {
      let url = `http://127.0.0.1:8000/reports/monthly?store_id=${storeId}&year=${year}&month=${month}&format=json`;
      if (reportType === "daily") {
        url = `http://127.0.0.1:8000/reports/daily?store_id=${storeId}&report_date=${day}&format=json`;
      }
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

  // Export report
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

  useEffect(() => { fetchReport(); }, [year, month, day, reportType]);

  const daysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();

  if (loading) return <Layout><ActivityIndicator size="large" color={Colors.primary} /></Layout>;
  if (!report) return <Layout><Text style={[Font.meta, { textAlign: "center", marginTop: Spacing.l }]}>No report data</Text></Layout>;

  const topProducts = report.top_products ?? [];
  const chartData = {
    labels: topProducts.map(p => p.name),
    datasets: [{ data: topProducts.map(p => p.qty_sold), color: () => Colors.primary, strokeWidth: 2 }],
    legend: ["Qty Sold"],
  };

  return (
    <Layout>
      <Text style={Font.title}>Reports</Text>

      {/* Filters */}
      <View style={{ marginBottom: Spacing.l }}>
        <Text style={[Font.label, { marginBottom: Spacing.s }]}>Year</Text>
        <Picker selectedValue={year} onValueChange={setYear} style={{ height: 50, width: "100%", marginBottom: Spacing.s }}>
          {Array.from({ length: 5 }, (_, i) => today.getFullYear() - i).map(y => <Picker.Item key={y} label={`${y}`} value={y} />)}
        </Picker>

        <Text style={[Font.label, { marginBottom: Spacing.s }]}>Month</Text>
        <Picker selectedValue={month} onValueChange={setMonth} style={{ height: 50, width: "100%", marginBottom: Spacing.s }}>
          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => <Picker.Item key={m} label={`${m}`} value={m} />)}
        </Picker>

        {reportType === "daily" && (
          <>
            <Text style={[Font.label, { marginBottom: Spacing.s }]}>Day</Text>
            <Picker selectedValue={day} onValueChange={setDay} style={{ height: 50, width: "100%", marginBottom: Spacing.s }}>
              {Array.from({ length: daysInMonth(year, month) }, (_, i) => {
                const value = `${year}-${month.toString().padStart(2, "0")}-${(i + 1).toString().padStart(2, "0")}`;
                return <Picker.Item key={value} label={`${i + 1}`} value={value} />;
              })}
            </Picker>
          </>
        )}

        {/* Report type buttons */}
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
        {/* Header */}
        <View style={{ flexDirection: "row", marginBottom: Spacing.s }}>
          <Text style={[Font.label, { flex: 2 }]}>Product</Text>
          <Text style={[Font.label, { flex: 1, textAlign: "center" }]}>Qty Sold</Text>
          <Text style={[Font.label, { flex: 1, textAlign: "right" }]}>Revenue</Text>
        </View>

        {/* Rows */}
        {topProducts.length > 0 ? (
          topProducts.map((p) => (
            <View key={p.product_id} style={{ flexDirection: "row", marginBottom: Spacing.s }}>
              <Text style={[Font.meta, { flex: 2 }]}>{p.name}</Text>
              <Text style={[Font.meta, { flex: 1, textAlign: "center" }]}>{p.qty_sold}</Text>
              <Text style={[Font.meta, { flex: 1, textAlign: "right" }]}>{p.revenue?.toFixed(2) ?? "0.00"}</Text>
            </View>
          ))
        ) : (
          <Text style={[Font.meta, { marginBottom: Spacing.s }]}>No product sales data available</Text>
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
