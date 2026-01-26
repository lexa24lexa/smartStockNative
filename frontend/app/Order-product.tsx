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

type FifoBatch = {
  batch_id: number;
  batch_code: string;
  quantity: number;
  expiration_date: string | null;
};

export default function OrderProduct() {
  const route = useRoute<RouteProp<RouteParams, "OrderProduct">>();
  const navigation = useNavigation();

  const { product, quantity, productId } = route.params;

  const [value, setValue] = useState<number>(Number(quantity) || 0);
  const [overrideQuantity, setOverrideQuantity] = useState<string>(String(Number(quantity) || 0));
  const [modalVisible, setModalVisible] = useState(false);
  const [reason, setReason] = useState("");
  const [priority, setPriority] = useState<"High" | "Medium" | "Low">("High");
  const [notes, setNotes] = useState("");

  const [currentUser, setCurrentUser] = useState<{ user_id: number; role_id: number } | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const [fifoBatch, setFifoBatch] = useState<FifoBatch | null>(null);
  const [selectedBatchId, setSelectedBatchId] = useState<number | null>(null);

  const [orderConfirmation, setOrderConfirmation] = useState<any | null>(null);

  const STORE_ID = 1;

  // --- Fetch current session user ---
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/session/user");
        if (!res.ok) {
          const fallbackRes = await fetch("http://127.0.0.1:8000/session/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: 2 }),
          });
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
        setFifoBatch({ batch_id: data.batch_id, batch_code: data.batch_code, quantity: data.quantity, expiration_date: data.expiration_date });
        setSelectedBatchId(data.batch_id);

        setValue(data.quantity);
        setOverrideQuantity(String(data.quantity));
      } catch (err) {
        console.error(err);
        Alert.alert("Error", "Could not fetch oldest batch for this product");
      }
    };
    fetchFifoBatch();
  }, [productId]);

  // --- Override modal setup ---
  const openOverrideModal = () => {
    if (currentUser?.role_id !== 2) return;
    setOverrideQuantity(String(value || 0));
    setReason("");
    setPriority("High");
    setNotes("");
    setModalVisible(true);
  };

  // --- Submit override ---
  const submitOverride = async () => {
    if (!selectedBatchId || !fifoBatch) {
      Alert.alert("Error", "No batch selected");
      return;
    }

    try {
      const qty = Number(overrideQuantity) || 0;

      if (qty > fifoBatch.quantity && currentUser?.role_id !== 2) {
        Alert.alert("FIFO Violation", "Employees cannot override oldest batch quantity.");
        return;
      }

      if (qty > fifoBatch.quantity && currentUser?.role_id === 2) {
        Alert.alert("FIFO Alert", "⚠ Quantity exceeds oldest batch. Manager override applied.");
      }

      const res = await fetch(
        `http://127.0.0.1:8000/replenishment-frequency/${productId}/${STORE_ID}/replenish`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            batch_id: selectedBatchId,
            quantity: qty,
            user_id: currentUser?.user_id,
            expiration_date: fifoBatch.expiration_date,
            replenishment_date: new Date().toISOString().split("T")[0],
          }),
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to place order");
      }

      const data = await res.json();

      setOrderConfirmation({
        product_name: product,
        batch_id: fifoBatch.batch_id,
        batch_code: fifoBatch.batch_code,
        quantity_ordered: qty,
        expiration_date: fifoBatch.expiration_date,
        priority,
        replenishment_frequency: data.replenishment_frequency,
        last_replenishment_date: data.last_replenishment_date,
        notes,
        reason,
      });

      setValue(qty);
      setModalVisible(false);
      Alert.alert("Success", "Override order placed successfully!");
    } catch (err: any) {
      console.error(err);
      Alert.alert("Error", err.message);
    }
  };

  // --- Place order ---
  const placeOrder = async () => {
    if (!selectedBatchId || !fifoBatch) {
      Alert.alert("Error", "No batch selected");
      return;
    }

    const isFifoViolation = value > fifoBatch.quantity;

    if (isFifoViolation && currentUser?.role_id !== 2) {
      Alert.alert(
        "FIFO Violation",
        "Quantity exceeds oldest batch! Employees cannot override FIFO."
      );
      return;
    }

    if (isFifoViolation && currentUser?.role_id === 2) {
      Alert.alert(
        "FIFO Alert",
        "⚠ Quantity exceeds oldest batch. You may override using the button if needed."
      );
    }

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/replenishment-frequency/${productId}/${STORE_ID}/replenish`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            batch_id: selectedBatchId,
            quantity: value,
            user_id: currentUser?.user_id ?? 1,
            expiration_date: fifoBatch.expiration_date,
            replenishment_date: new Date().toISOString().split("T")[0],
          }),
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to place order");
      }

      const data = await res.json();

      setOrderConfirmation({
        product_name: product,
        batch_id: fifoBatch.batch_id,
        batch_code: fifoBatch.batch_code,
        quantity_ordered: value,
        expiration_date: fifoBatch.expiration_date,
        priority: "High",
        replenishment_frequency: data.replenishment_frequency,
        last_replenishment_date: data.last_replenishment_date,
      });

      Alert.alert("Success", "Order placed successfully");

    } catch (err: any) {
      console.error(err);
      Alert.alert("Error", err.message);
    }
  };

  const showFifoAlert = fifoBatch ? value > fifoBatch.quantity : false;

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
          <TouchableOpacity style={styles.circle} onPress={() => setValue((v) => Math.max(0, (v || 0) - 1))}>
            <Text>-</Text>
          </TouchableOpacity>

          <Text style={styles.quantity}>{value ?? 0}</Text>

          <TouchableOpacity style={styles.circle} onPress={() => setValue((v) => (v || 0) + 1)}>
            <Text>+</Text>
          </TouchableOpacity>
        </View>

        {showFifoAlert && (
          <Text style={styles.redAlert}>⚠ FIFO violation! Quantity exceeds oldest batch.</Text>
        )}

        {!loadingUser && currentUser?.role_id === 2 && (
          <TouchableOpacity style={styles.overrideButton} onPress={openOverrideModal}>
            <Text style={{ color: "#fff", fontWeight: "600" }}>Override Suggestion</Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity style={styles.primaryButton} onPress={placeOrder}>
        <Text style={styles.primaryText}>Place order</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.dangerButton} onPress={() => navigation.goBack()}>
        <Text style={styles.primaryText}>Cancel order</Text>
      </TouchableOpacity>

      {orderConfirmation && (
        <View style={[styles.card, { backgroundColor: "#D1FAE5" }]}>
          <Text style={{ fontWeight: "bold", fontSize: 18 }}>{orderConfirmation.product_name}</Text>
          <Text>Batch: {orderConfirmation.batch_code}</Text>
          <Text>Quantity ordered: {orderConfirmation.quantity_ordered}</Text>
          <Text>Replenishment priority: {orderConfirmation.priority}</Text>
          <Text>Last replenishment: {orderConfirmation.last_replenishment_date ?? "—"}</Text>
          <Text>Replenishment frequency: every {orderConfirmation.replenishment_frequency} day(s)</Text>
          <Text>Expiration date: {orderConfirmation.expiration_date ?? "—"}</Text>
        </View>
      )}

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
            <TextInput style={styles.input} value={reason} onChangeText={setReason} placeholder="Reason" />
            <Picker selectedValue={priority} onValueChange={(val) => setPriority(val)} style={styles.picker}>
              <Picker.Item label="High" value="High" />
              <Picker.Item label="Medium" value="Medium" />
              <Picker.Item label="Low" value="Low" />
            </Picker>
            <TextInput style={styles.input} value={notes} onChangeText={setNotes} placeholder="Notes" />

            <View style={styles.modalButtons}>
              <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.modalButton}>
                <Text>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={submitOverride} style={[styles.modalButton, { backgroundColor: "#059669" }]}>
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
  overrideButton: { marginTop: 12, backgroundColor: "#F59E0B", padding: 12, borderRadius: 8, alignItems: "center" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center" },
  modalContent: { width: "90%", backgroundColor: "#fff", padding: 16, borderRadius: 12 },
  modalTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 12 },
  input: { borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 8, padding: 8, marginBottom: 12 },
  picker: { height: 50, marginBottom: 12 },
  modalButtons: { flexDirection: "row", justifyContent: "space-between" },
  modalButton: { flex: 1, padding: 12, alignItems: "center", marginHorizontal: 4, borderRadius: 8, backgroundColor: "#E5E7EB" },
  redAlert: { color: "#DC2626", marginTop: 8, fontWeight: "bold" },
});
