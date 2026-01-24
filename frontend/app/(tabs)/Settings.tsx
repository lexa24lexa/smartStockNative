import React, { useState } from "react";
import { StyleSheet, Switch, Text, View } from "react-native";
import Layout from "../../components/ui/Layout";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

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
      <Text style={Font.label}>{label}</Text>
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
      <Text style={Font.title}>Settings</Text>

      <View style={styles.card}>
        <Text style={Font.subtitle}>Notification Preferences</Text>

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
        <Text style={Font.subtitle}>Legal & Support</Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>Help & Support</Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>Privacy Policy</Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>Terms & Conditions</Text>
      </View>

      <View style={styles.clearCard}>
        <Text style={[Font.label, { color: Colors.danger }]}>Clear Cache</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.bgCard,
    padding: Spacing.m,
    borderRadius: Radius.card,
    marginBottom: Spacing.m,
  },
  toggleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: Spacing.s,
  },
  clearCard: {
    backgroundColor: Colors.bgPage,
    padding: Spacing.m,
    borderRadius: Radius.card,
    alignItems: "center",
    marginTop: Spacing.m,
  },
});
