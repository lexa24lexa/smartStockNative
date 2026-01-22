import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";

function ReportCard({
  title,
  description,
  type,
  lastGenerated,
  onDownload,
}: {
  title: string;
  description: string;
  type: "daily" | "monthly";
  lastGenerated: string;
  onDownload: () => void;
}) {
  return (
    <View style={styles.reportCard}>
      <View style={styles.reportHeader}>
        <View>
          <Text style={styles.reportTitle}>{title}</Text>
          <Text style={styles.reportDesc}>{description}</Text>
        </View>
        <View style={[styles.typeBadge, type === "daily" ? styles.dailyBadge : styles.monthlyBadge]}>
          <Text style={styles.badgeText}>{type.toUpperCase()}</Text>
        </View>
      </View>
      
      <Text style={styles.lastGenerated}>Last generated: {lastGenerated}</Text>
      
      <View style={styles.reportActions}>
        <TouchableOpacity style={styles.downloadBtn} onPress={onDownload}>
          <Text style={styles.downloadBtnText}>📥 Download PDF</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.downloadBtn} onPress={onDownload}>
          <Text style={styles.downloadBtnText}>📊 Download Excel</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function TraceabilityLog({
  action,
  product,
  quantity,
  timestamp,
  user,
}: {
  action: string;
  product: string;
  quantity: number;
  timestamp: string;
  user: string;
}) {
  return (
    <View style={styles.logEntry}>
      <View style={styles.logIcon}>
        <Text>📦</Text>
      </View>
      <View style={styles.logContent}>
        <Text style={styles.logAction}>{action}</Text>
        <Text style={styles.logProduct}>{product} - {quantity} units</Text>
        <Text style={styles.logMeta}>{user} • {timestamp}</Text>
      </View>
    </View>
  );
}

export default function Reports() {
  const [emailEnabled, setEmailEnabled] = useState(true);

  const reports = [
    {
      id: 1,
      title: "Daily Sales & Stock Report",
      description: "Complete overview of daily operations",
      type: "daily" as const,
      lastGenerated: "Today at 8:00 AM",
    },
    {
      id: 2,
      title: "Monthly Performance Report",
      description: "Detailed monthly analytics and trends",
      type: "monthly" as const,
      lastGenerated: "Jan 1, 2026",
    },
  ];

  const traceability = [
    { id: 1, action: "Replenishment", product: "Coca Cola 500ml", quantity: 48, timestamp: "2h ago", user: "System" },
    { id: 2, action: "Manual Override", product: "Croissant", quantity: 30, timestamp: "5h ago", user: "John Doe" },
    { id: 3, action: "Stock Adjustment", product: "Pain au chocolat", quantity: -5, timestamp: "Yesterday", user: "Jane Smith" },
  ];

  return (
    <Layout>
      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Reports</Text>

      <View style={styles.filters}>
        <View style={styles.filterCard}>
          <Text style={styles.filterLabel}>Select report type</Text>
          <Text style={styles.filterValue}>Graphic ▾</Text>
        </View>

        <View style={styles.filterCard}>
          <Text style={styles.filterLabel}>Data range</Text>
          <Text style={styles.filterValue}>20-01-2025</Text>
          <Text style={styles.filterValue}>20-02-2025</Text>
        </View>
      </View>

      <View style={styles.chartCard}>
        <View style={styles.chartPlaceholder} />

        <View style={styles.tooltip}>
          <Text style={styles.tooltipTitle}>Detailed Breakdown -</Text>
          <Text style={styles.tooltipSubtitle}>August 2023</Text>

          <View style={styles.tooltipRow}>
            <Text>● Product A</Text>
            <Text>150 units</Text>
          </View>
          <View style={styles.tooltipRow}>
            <Text>● Product B</Text>
            <Text>50 units</Text>
          </View>
          <View style={styles.tooltipRow}>
            <Text>● Product C</Text>
            <Text>75 units</Text>
          </View>
        </View>
      </View>

      <View style={styles.table}>
        <Text style={styles.tableHeader}>Date     Product     Sales Qty</Text>
        <Text style={styles.tableRow}>—        —           —</Text>
        <Text style={styles.tableRow}>—        —           —</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280", marginBottom: 4 },

  filters: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  filterCard: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 12,
  },
  filterLabel: {
    color: "#6B7280",
    fontSize: 12,
  },
  filterValue: {
    marginTop: 4,
    fontWeight: "600",
  },

  chartCard: {
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  chartPlaceholder: {
    height: 160,
    backgroundColor: "#E5E7EB",
    borderRadius: 8,
  },

  tooltip: {
    position: "absolute",
    left: 20,
    bottom: 20,
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 10,
    elevation: 3,
  },
  tooltipTitle: {
    fontWeight: "600",
  },
  tooltipSubtitle: {
    marginBottom: 8,
  },
  tooltipRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },

  table: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
  },
  tableHeader: {
    fontWeight: "600",
    marginBottom: 8,
  },
  tableRow: {
    color: "#6B7280",
  },
});
