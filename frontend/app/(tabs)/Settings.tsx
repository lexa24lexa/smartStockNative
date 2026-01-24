import React, { useState, useEffect } from "react";
import { StyleSheet, Switch, Text, View } from "react-native";
import { Picker } from "@react-native-picker/picker";
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

  // User selector
  const [userId, setUserId] = useState<number | undefined>(undefined);

  // Fetch current user from backend
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/session/user");
        if (!res.ok) return;
        const data = await res.json();
        setUserId(data.user_id);
      } catch (err) {
        console.error("Error fetching current user:", err);
      }
    };
    fetchCurrentUser();
  }, []);

  // Save selected user to backend
  const saveCurrentUser = async (id: number) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/session/user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: id }),
      });
      if (!res.ok) throw new Error("Failed to save user");
    } catch (err) {
      console.error("Error saving current user:", err);
    }
  };

  return (
    <Layout>
      <Text style={Font.title}>Settings</Text>

      {/* User / Role Selector */}
      <View style={styles.card}>
        <Text style={Font.subtitle}>Current User</Text>
          <Picker
            selectedValue={userId}
            onValueChange={(value: number) => {
              setUserId(value);
              saveCurrentUser(value);
            }}
            style={{ color: Colors.primary }}
          >
            <Picker.Item label="John Employee" value={1} />
            <Picker.Item label="Anna Manager" value={2} />
          </Picker>
        <Text style={[Font.label, { marginTop: Spacing.s }]}>
          Selected User ID: {userId ?? "loading..."}
        </Text>
      </View>

      {/* Notification Preferences */}
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

      {/* Legal & Support */}
      <View style={styles.card}>
        <Text style={Font.subtitle}>Legal & Support</Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>
          Help & Support
        </Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>
          Privacy Policy
        </Text>
        <Text style={[Font.label, { paddingVertical: Spacing.s, color: Colors.primary }]}>
          Terms & Conditions
        </Text>
      </View>

      {/* Clear Cache */}
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
