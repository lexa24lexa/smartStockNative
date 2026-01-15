import React, { useState } from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, Switch } from "react-native";
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
      <Text style={styles.title}>Reports & History</Text>
      <Text style={styles.subtitle}>Export reports and view traceability</Text>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>📧 Email Delivery</Text>
          <Switch
            value={emailEnabled}
            onValueChange={setEmailEnabled}
            trackColor={{ false: "#D1D5DB", true: "#059669" }}
            thumbColor="#fff"
          />
        </View>
        {emailEnabled && (
          <Text style={styles.emailInfo}>
            Reports will be sent daily at 8:00 AM to admin@company.com
          </Text>
        )}
      </View>

      <Text style={styles.sectionTitle}>Available Reports</Text>
      <ScrollView style={styles.reportsContainer}>
        {reports.map(report => (
          <ReportCard
            key={report.id}
            title={report.title}
            description={report.description}
            type={report.type}
            lastGenerated={report.lastGenerated}
            onDownload={() => console.log(`Download ${report.title}`)}
          />
        ))}
      </ScrollView>

      <Text style={styles.sectionTitle}>Replenishment Traceability</Text>
      <ScrollView style={styles.traceabilityContainer}>
        {traceability.map(log => (
          <TraceabilityLog
            key={log.id}
            action={log.action}
            product={log.product}
            quantity={log.quantity}
            timestamp={log.timestamp}
            user={log.user}
          />
        ))}
      </ScrollView>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold" },
  subtitle: { color: "#6B7280", marginBottom: 16 },

  section: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 12,
  },
  emailInfo: {
    marginTop: 8,
    color: "#6B7280",
    fontSize: 13,
  },

  reportsContainer: {
    maxHeight: 280,
    marginBottom: 16,
  },

  reportCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  reportHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  reportTitle: {
    fontSize: 16,
    fontWeight: "600",
  },
  reportDesc: {
    color: "#6B7280",
    fontSize: 13,
    marginTop: 2,
  },
  typeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    height: 24,
  },
  dailyBadge: {
    backgroundColor: "#DBEAFE",
  },
  monthlyBadge: {
    backgroundColor: "#FEF3C7",
  },
  badgeText: {
    fontSize: 11,
    fontWeight: "600",
  },
  lastGenerated: {
    color: "#6B7280",
    fontSize: 12,
    marginBottom: 12,
  },
  reportActions: {
    flexDirection: "row",
    gap: 8,
  },
  downloadBtn: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  downloadBtnText: {
    fontSize: 13,
    fontWeight: "500",
  },

  traceabilityContainer: {
    maxHeight: 240,
  },

  logEntry: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
  },
  logIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#F3F4F6",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  logContent: {
    flex: 1,
  },
  logAction: {
    fontWeight: "600",
    fontSize: 14,
  },
  logProduct: {
    color: "#6B7280",
    fontSize: 13,
    marginTop: 2,
  },
  logMeta: {
    color: "#9CA3AF",
    fontSize: 11,
    marginTop: 4,
  },
});