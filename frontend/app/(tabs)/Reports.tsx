import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View, ActivityIndicator, Dimensions, TouchableOpacity } from "react-native";
import { Picker } from "@react-native-picker/picker";
import { LineChart } from "react-native-chart-kit";
import Layout from "../../components/ui/Layout";

type TopProduct = {
  product_id: number;
  name: string;
  qty_sold: number;
  revenue: number;
};

type Report = {
  sale_count: number;
  total_items_sold: number;
  total_revenue: number;
  top_products?: TopProduct[];
};

export default function Reports() {
  const storeId = 1; // Replace with dynamic store if needed
  const today = new Date();

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  const [year, setYear] = useState<number>(today.getFullYear());
  const [month, setMonth] = useState<number>(today.getMonth() + 1);
  const [day, setDay] = useState<string>(today.toISOString().slice(0, 10));
  const [reportType, setReportType] = useState<"monthly" | "daily">("monthly");

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

  useEffect(() => {
    fetchReport();
  }, [year, month, day, reportType]);

  const daysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();

  if (loading) return <Layout><ActivityIndicator size="large" color="#000" /></Layout>;
  if (!report) return <Layout><Text style={{ textAlign: "center", marginTop: 20 }}>No report data</Text></Layout>;

  const topProducts = report.top_products ?? [];
  const chartData = {
    labels: topProducts.map(p => p.name),
    datasets: [{ data: topProducts.map(p => p.qty_sold), color: () => "#4F46E5", strokeWidth: 2 }],
    legend: ["Qty Sold"],
  };

  return (
    <Layout>
      <Text style={styles.title}>Reports</Text>

      {/* Filters */}
      <View style={styles.filters}>

        <Text style={styles.filterLabel}>Year</Text>
        <Picker selectedValue={year} onValueChange={setYear} style={styles.picker}>
          {Array.from({ length: 5 }, (_, i) => today.getFullYear() - i).map(y => (
            <Picker.Item key={y} label={`${y}`} value={y} />
          ))}
        </Picker>

        <Text style={styles.filterLabel}>Month</Text>
        <Picker selectedValue={month} onValueChange={setMonth} style={styles.picker}>
          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
            <Picker.Item key={m} label={`${m}`} value={m} />
          ))}
        </Picker>

        {reportType === "daily" && (
          <>
            <Text style={styles.filterLabel}>Day</Text>
            <Picker selectedValue={day} onValueChange={setDay} style={styles.picker}>
              {Array.from({ length: daysInMonth(year, month) }, (_, i) => {
                const value = `${year}-${month.toString().padStart(2, "0")}-${(i + 1).toString().padStart(2, "0")}`;
                return <Picker.Item key={value} label={`${i + 1}`} value={value} />;
              })}
            </Picker>
          </>
        )}

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, reportType === "monthly" && styles.activeButton]}
            onPress={() => setReportType("monthly")}
          >
            <Text style={[styles.buttonText, reportType === "monthly" && styles.activeButtonText]}>Monthly</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, reportType === "daily" && styles.activeButton]}
            onPress={() => setReportType("daily")}
          >
            <Text style={[styles.buttonText, reportType === "daily" && styles.activeButtonText]}>Daily</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Chart */}
      {topProducts.length > 0 ? (
        <>
          <Text style={styles.subtitle}>Top Products Sold</Text>
          <LineChart
            data={chartData}
            width={Dimensions.get("window").width - 32}
            height={220}
            yAxisLabel=""
            chartConfig={{
              backgroundColor: "#fff",
              backgroundGradientFrom: "#fff",
              backgroundGradientTo: "#fff",
              decimalPlaces: 0,
              color: () => "#4F46E5",
              labelColor: () => "#374151",
              style: { borderRadius: 16 },
            }}
            style={{ borderRadius: 16, marginVertical: 16 }}
          />
        </>
      ) : (
        <Text style={{ marginVertical: 16 }}>No product sales data available</Text>
      )}

      {/* Table */}
      <View style={styles.table}>
        <Text style={styles.tableHeader}>Product     Qty Sold     Revenue</Text>
        {topProducts.length > 0 ? (
          topProducts.map(p => (
            <Text key={p.product_id} style={styles.tableRow}>
              {p.name}     {p.qty_sold}     {p.revenue?.toFixed(2) ?? "0.00"}
            </Text>
          ))
        ) : (
          <Text style={styles.tableRow}>No product sales data available</Text>
        )}
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280", fontWeight: "600", marginBottom: 8 },
  filters: { marginBottom: 16 },
  filterLabel: { fontWeight: "600", marginBottom: 4, color: "#374151" },
  picker: { height: 50, width: "100%", marginBottom: 8 },
  table: { backgroundColor: "#fff", padding: 16, borderRadius: 12 },
  tableHeader: { fontWeight: "600", marginBottom: 8 },
  tableRow: { color: "#6B7280", marginBottom: 4 },
  buttonRow: { flexDirection: "row", marginVertical: 8 },
  button: { flex: 1, padding: 8, backgroundColor: "#E5E7EB", borderRadius: 8, alignItems: "center", marginHorizontal: 4 },
  activeButton: { backgroundColor: "#4F46E5" },
  buttonText: { color: "#000", fontWeight: "600" },
  activeButtonText: { color: "#fff" },
});
