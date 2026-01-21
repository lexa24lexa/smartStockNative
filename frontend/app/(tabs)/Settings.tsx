import React, { useState } from "react";
import { StyleSheet, Switch, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";

function ToggleRow({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: () => void;
}) {
  return (
    <View style={styles.toggleRow}>
      <Text>{label}</Text>
      <Switch value={value} onValueChange={onChange} />
    </View>
  );
}

export default function Settings() {
  const [master, setMaster] = useState(true);
  const [report, setReport] = useState(true);
  const [below, setBelow] = useState(true);
  const [reaching, setReaching] = useState(true);

  return (
    <Layout>
      <Text style={styles.title}>Settings</Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Notification Preferences</Text>

        <ToggleRow
          label="Master Notifications"
          value={master}
          onChange={() => setMaster(!master)}
        />
        <ToggleRow
          label="Report Generated"
          value={report}
          onChange={() => setReport(!report)}
        />
        <ToggleRow
          label="Stock Below Minimum"
          value={below}
          onChange={() => setBelow(!below)}
        />
        <ToggleRow
          label="Stock Reaching Minimum"
          value={reaching}
          onChange={() => setReaching(!reaching)}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Legal & Support</Text>
        <Text style={styles.link}>Help & Support</Text>
        <Text style={styles.link}>Privacy Policy</Text>
        <Text style={styles.link}>Terms & Conditions</Text>
      </View>

      <View style={styles.clearCard}>
        <Text style={styles.clearText}>Clear Cache</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
  },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  cardTitle: {
    fontWeight: "600",
    marginBottom: 12,
  },

  toggleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: 6,
  },

  link: {
    paddingVertical: 8,
  },

  clearCard: {
    backgroundColor: "#F3F4F6",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  clearText: {
    fontWeight: "600",
  },
});
