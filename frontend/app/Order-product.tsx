import { RouteProp, useNavigation, useRoute } from "@react-navigation/native"; 
import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Modal,
  TextInput,
  Alert,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import Layout from "../components/ui/Layout";

type RouteParams = {
  OrderProduct: {
    product: string;
    productId: number;
    quantity: number;
  };
};

export default function OrderProduct() {
  const route = useRoute<RouteProp<RouteParams, "OrderProduct">>();
  const navigation = useNavigation();

  const { product, quantity, productId } = route.params;

  // --- State initialization ---
  const [value, setValue] = useState<number>(Number(quantity) || 0);
  const [overrideQuantity, setOverrideQuantity] = useState<string>(String(Number(quantity) || 0));
  const [modalVisible, setModalVisible] = useState(false);
  const [reason, setReason] = useState("");
  const [priority, setPriority] = useState<"High" | "Medium" | "Low">("High");
  const [notes, setNotes] = useState("");

  const [currentUser, setCurrentUser] = useState<{ user_id: number; role_id: number } | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const [fifoBatch, setFifoBatch] = useState<{ batch_id: number; quantity: number } | null>(null);
  const STORE_ID = 1;

  // --- Fetch current session user ---
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/session/user");
        if (!res.ok) {
          // fallback: set default manager if no session user
          await fetch("http://127.0.0.1:8000/session/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: 2 }), // default manager ID
          });
          const fallbackRes = await fetch("http://127.0.0.1:8000/session/user");
          const fallbackData = await fallbackRes.json();
          setCurrentUser({ user_id: fallbackData.user_id, role_id: fallbackData.role_id });
        } else {
          const data = await res.json();
          setCurrentUser({ user_id: data.user_id, role_id: data.role_id });
        }
      } catch (err) {
        console.error("Error fetching current user:", err);
      } finally {
        setLoadingUser(false);
      }
    };
    fetchCurrentUser();
  }, []);

  // --- Fetch FIFO batch for this product ---
  useEffect(() => {
    const fetchFifoBatch = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/replenishment/${STORE_ID}/${productId}`);
        if (!res.ok) throw new Error("Failed to fetch FIFO batch");

        const data = await res.json();
        setFifoBatch({ batch_id: data.batch_id, quantity: data.available_quantity });

        // set default quantity to FIFO batch
        setValue(data.available_quantity);
        setOverrideQuantity(String(data.available_quantity));
      } catch (err) {
        console.error(err);
        Alert.alert("Error", "Could not fetch oldest batch for this product");
      }
    };
    fetchFifoBatch();
  }, [productId]);

  // --- Override modal setup ---
  const openOverrideModal = () => {
    if (currentUser?.role_id !== 2) return; // only managers
    setOverrideQuantity(String(value || 0));
    setReason("");
    setPriority("High");
    setNotes("");
    setModalVisible(true);
  };

  const submitOverride = async () => {
    try {
      const qty = Number(overrideQuantity) || 0;
      const response = await fetch(
        `http://127.0.0.1:8000/replenishment-lists/1/2026-01-24/items/${productId}/override`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            user_id: String(currentUser?.user_id ?? 1),
          },
          body: JSON.stringify({ quantity: qty, reason, priority, notes }),
        }
      );
      if (!response.ok) throw new Error("Failed to override");

      setValue(qty);
      setModalVisible(false);
      Alert.alert("Success", "Override applied!");
    } catch (err) {
      console.error(err);
      Alert.alert("Error", "Failed to override item");
    }
  };

  // --- Place order using FIFO batch ---
  const placeOrder = async () => {
    if (!fifoBatch) {
      Alert.alert("Error", "No batch available for this product");
      return;
    }
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/replenishment-frequency/${productId}/${STORE_ID}/replenish`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            user_id: String(currentUser?.user_id ?? 1),
          },
          body: JSON.stringify({ batch_id: fifoBatch.batch_id, quantity: value, user_id: currentUser?.user_id ?? 1 }),
        }
      );
      if (!res.ok) throw new Error("Failed to place order");

      Alert.alert("Success", `Order placed for batch ${fifoBatch.batch_id}`);
      navigation.goBack();
    } catch (err) {
      console.error(err);
      Alert.alert("Error", "Failed to place order");
    }
  };

  return (
    <Layout>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backText}>← Back</Text>
      </TouchableOpacity>

      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Order {product}</Text>

      {fifoBatch && (
        <View style={[styles.card, { backgroundColor: "#E0F2FE" }]}>
          <Text style={styles.label}>FIFO Batch Info</Text>
          <Text>Batch ID: {fifoBatch.batch_id}</Text>
          <Text>Available Quantity: {fifoBatch.quantity}</Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.label}>Quantity</Text>
        <View style={styles.quantityRow}>
          <TouchableOpacity
            style={styles.circle}
            onPress={() => setValue((v) => Math.max(0, (v || 0) - 1))}
          >
            <Text>-</Text>
          </TouchableOpacity>

          <Text style={styles.quantity}>{value ?? 0}</Text>

          <TouchableOpacity
            style={styles.circle}
            onPress={() => setValue((v) => (v || 0) + 1)}
          >
            <Text>+</Text>
          </TouchableOpacity>
        </View>

        {/* SHOW BUTTON ONLY FOR MANAGERS */}
        {!loadingUser && currentUser?.role_id === 2 && (
          <TouchableOpacity style={styles.overrideButton} onPress={openOverrideModal}>
            <Text style={{ color: "#fff", fontWeight: "600" }}>Override Suggestion</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Supplier</Text>
        <Text>name</Text>
        <Text style={styles.meta}>Estimated delivery date: 28-11-2025</Text>
      </View>

      <TouchableOpacity style={styles.primaryButton} onPress={placeOrder}>
        <Text style={styles.primaryText}>Place order</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.dangerButton} onPress={() => navigation.goBack()}>
        <Text style={styles.primaryText}>Cancel order</Text>
      </TouchableOpacity>

      <Modal visible={modalVisible} transparent={true} animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Override {product}</Text>

            <TextInput
              style={styles.input}
              value={overrideQuantity}
              onChangeText={setOverrideQuantity}
              keyboardType="numeric"
              placeholder="Quantity"
            />
            <TextInput
              style={styles.input}
              value={reason}
              onChangeText={setReason}
              placeholder="Reason"
            />
            <Picker
              selectedValue={priority}
              onValueChange={(val) => setPriority(val)}
              style={styles.picker}
            >
              <Picker.Item label="High" value="High" />
              <Picker.Item label="Medium" value="Medium" />
              <Picker.Item label="Low" value="Low" />
            </Picker>
            <TextInput
              style={styles.input}
              value={notes}
              onChangeText={setNotes}
              placeholder="Notes"
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.modalButton}>
                <Text>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={submitOverride}
                style={[styles.modalButton, { backgroundColor: "#059669" }]}
              >
                <Text style={{ color: "#fff" }}>Submit</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </Layout>
  );
}

const styles = StyleSheet.create({
  backButton: { marginBottom: 12 },
  backText: { fontSize: 16, color: "#059669" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 16 },
  subtitle: { color: "#6B7280" },
  card: { backgroundColor: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 },
  label: { fontWeight: "600", marginBottom: 8 },
  quantityRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  quantity: { fontSize: 18 },
  circle: { width: 36, height: 36, borderRadius: 18, backgroundColor: "#E5E7EB", alignItems: "center", justifyContent: "center" },
  primaryButton: { backgroundColor: "#059669", padding: 16, borderRadius: 10, marginBottom: 12 },
  dangerButton: { backgroundColor: "#DC2626", padding: 16, borderRadius: 10 },
  primaryText: { color: "#fff", textAlign: "center", fontWeight: "600" },
  meta: { fontSize: 12, color: "#6B7280", marginTop: 6 },
  overrideButton: { marginTop: 12, backgroundColor: "#F59E0B", padding: 12, borderRadius: 8, alignItems: "center" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center" },
  modalContent: { width: "90%", backgroundColor: "#fff", padding: 16, borderRadius: 12 },
  modalTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 12 },
  input: { borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 8, padding: 8, marginBottom: 12 },
  picker: { height: 50, marginBottom: 12 },
  modalButtons: { flexDirection: "row", justifyContent: "space-between" },
  modalButton: { flex: 1, padding: 12, alignItems: "center", marginHorizontal: 4, borderRadius: 8, backgroundColor: "#E5E7EB" },
});
