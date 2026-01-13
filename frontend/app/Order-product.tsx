import { RouteProp, useNavigation, useRoute } from "@react-navigation/native";
import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import Layout from "../components/ui/Layout";

type RouteParams = {
  OrderProduct: {
    product: string;
    quantity: number;
  };
};

export default function OrderProduct() {
  const route = useRoute<RouteProp<RouteParams, "OrderProduct">>();
  const navigation = useNavigation(); // <--- para voltar

  const { product, quantity } = route.params;
  const [value, setValue] = useState(quantity);

  return (
    <Layout>
      {/* Back button */}
      <TouchableOpacity
        style={styles.backButton}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.backText}>← Back</Text>
      </TouchableOpacity>

      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Order {product}</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Quantity</Text>

        <View style={styles.quantityRow}>
          <TouchableOpacity
            style={styles.circle}
            onPress={() => setValue((v) => Math.max(0, v - 1))}
          >
            <Text>-</Text>
          </TouchableOpacity>

          <Text style={styles.quantity}>{value}</Text>

          <TouchableOpacity
            style={styles.circle}
            onPress={() => setValue((v) => v + 1)}
          >
            <Text>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Supplier</Text>
        <Text>name</Text>
        <Text style={styles.meta}>
          Estimated delivery date: 28-11-2025
        </Text>
      </View>

      <TouchableOpacity style={styles.primaryButton}>
        <Text style={styles.primaryText}>Place order</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.dangerButton}
        onPress={() => navigation.goBack()} // <--- cancelar volta para Stock
      >
        <Text style={styles.primaryText}>Cancel order</Text>
      </TouchableOpacity>
    </Layout>
  );
}

const styles = StyleSheet.create({
  backButton: {
    marginBottom: 12,
  },
  backText: {
    fontSize: 16,
    color: "#059669",
  },

  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
  },
  subtitle: {
    color: "#6B7280",
  },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  label: {
    fontWeight: "600",
    marginBottom: 8,
  },

  quantityRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  quantity: {
    fontSize: 18,
  },

  circle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "#E5E7EB",
    alignItems: "center",
    justifyContent: "center",
  },

  primaryButton: {
    backgroundColor: "#059669",
    padding: 16,
    borderRadius: 10,
    marginBottom: 12,
  },
  dangerButton: {
    backgroundColor: "#DC2626",
    padding: 16,
    borderRadius: 10,
  },
  primaryText: {
    color: "#fff",
    textAlign: "center",
    fontWeight: "600",
  },

  meta: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 6,
  },
});
