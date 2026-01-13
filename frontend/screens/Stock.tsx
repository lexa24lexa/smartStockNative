import {
  NavigationProp,
  ParamListBase,
  useNavigation,
} from "@react-navigation/native";
import React from "react";
import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import Layout from "../components/ui/Layout";

interface ProductRowProps {
  name: string;
  quantity: number;
  status: string;
  color: string;
  onPress: () => void;
}

function ProductRow({
  name,
  quantity,
  status,
  color,
  onPress,
}: ProductRowProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.productCard,
        pressed && { opacity: 0.7 },
      ]}
    >
      <View style={styles.row}>
        <Text style={styles.productName}>{name}</Text>
        <Text style={{ color }}>{status}</Text>
      </View>

      <Text style={styles.quantity}>{quantity}</Text>

      <View style={styles.progressBackground}>
        <View
          style={[styles.progressBar, { backgroundColor: color }]}
        />
      </View>

      <Text style={styles.meta}>Last purchase: 10:45</Text>
    </Pressable>
  );
}

export default function Stock() {
  const navigation =
    useNavigation<NavigationProp<ParamListBase>>();

  return (
    <Layout>
      <Text style={styles.subtitle}>Updated 10min ago</Text>
      <Text style={styles.title}>Stock overview</Text>

      <View style={styles.statusCard}>
        <Text style={styles.statusTitle}>Stock status</Text>
        <Text style={styles.stable}>● Stable</Text>
        <Text style={styles.meta}>
          Days to Out-of-Stock: 2d
        </Text>
      </View>

      <ProductRow
        name="Product A"
        quantity={120}
        status="Stable"
        color="#059669"
        onPress={() =>
          navigation.navigate("OrderProduct", {
            product: "Product A",
            quantity: 120,
          })
        }
      />

      <ProductRow
        name="Product B"
        quantity={50}
        status="Critical"
        color="#DC2626"
        onPress={() =>
          navigation.navigate("OrderProduct", {
            product: "Product B",
            quantity: 50,
          })
        }
      />

      <ProductRow
        name="Product C"
        quantity={70}
        status="Low"
        color="#F59E0B"
        onPress={() =>
          navigation.navigate("OrderProduct", {
            product: "Product C",
            quantity: 70,
          })
        }
      />
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
  },
  subtitle: {
    color: "#6B7280",
  },

  statusCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginVertical: 16,
  },
  statusTitle: {
    fontWeight: "600",
    marginBottom: 8,
  },
  stable: {
    color: "#059669",
    fontWeight: "600",
  },

  productCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    cursor: "pointer",
  },

  row: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  productName: {
    fontWeight: "600",
  },
  quantity: {
    fontSize: 18,
    marginVertical: 8,
  },

  progressBackground: {
    height: 6,
    backgroundColor: "#E5E7EB",
    borderRadius: 3,
  },
  progressBar: {
    width: "50%",
    height: 6,
    borderRadius: 3,
  },

  meta: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 6,
  },
});
