import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  FlatList,
} from "react-native";
import {
  NavigationProp,
  ParamListBase,
  useNavigation,
} from "@react-navigation/native";
import Layout from "../../components/ui/Layout";

type StockStatus = "Stable" | "Low" | "Critical";

interface StockOverview {
  product_id: number;
  product_name: string;
  total_quantity: number;
  status: StockStatus;
  progress: number; // 0..1
  days_to_out_of_stock?: number | null;
  last_sale_at?: string | null;
}

interface ProductRowProps {
  item: StockOverview;
  onPress: () => void;
}

function statusColor(status: StockStatus) {
  switch (status) {
    case "Critical":
      return "#DC2626";
    case "Low":
      return "#F59E0B";
    default:
      return "#059669";
  }
}

function formatLastSale(date?: string | null) {
  if (!date) return "No sales yet";
  const d = new Date(date);
  return `Last sale: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

function ProductRow({ item, onPress }: ProductRowProps) {
  const color = statusColor(item.status);

  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.productCard,
        pressed && { opacity: 0.7 },
      ]}
    >
      <View style={styles.row}>
        <Text style={styles.productName}>{item.product_name}</Text>
        <Text style={{ color, fontWeight: "600" }}>
          ● {item.status}
        </Text>
      </View>

      <Text style={styles.quantity}>{item.total_quantity}</Text>

      <View style={styles.progressBackground}>
        <View
          style={[
            styles.progressBar,
            {
              width: `${Math.round(item.progress * 100)}%`,
              backgroundColor: color,
            },
          ]}
        />
      </View>

      <View style={styles.metaRow}>
        <Text style={styles.meta}>
          {item.days_to_out_of_stock != null
            ? `Days to OOS: ${item.days_to_out_of_stock}d`
            : "Days to OOS: —"}
        </Text>
        <Text style={styles.meta}>
          {formatLastSale(item.last_sale_at)}
        </Text>
      </View>
    </Pressable>
  );
}

export default function Stock() {
  const navigation =
    useNavigation<NavigationProp<ParamListBase>>();

  const [data, setData] = React.useState<StockOverview[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(
    null
  );

  const STORE_ID = 1;

  React.useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/stock/overview/${STORE_ID}`
        );

        if (!res.ok) {
          throw new Error("Failed to load stock");
        }

        const json = await res.json();
        setData(json);
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "Unknown error"
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <Layout>
      <Text style={styles.subtitle}>Live inventory</Text>
      <Text style={styles.title}>Stock overview</Text>

      {loading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" />
        </View>
      )}

      {error && (
        <Text style={styles.error}>{error}</Text>
      )}

      {!loading && !error && data.length === 0 && (
        <Text style={styles.meta}>
          No stock available for this store.
        </Text>
      )}

      <FlatList
        data={data}
        keyExtractor={(item) =>
          item.product_id.toString()
        }
        renderItem={({ item }) => (
          <ProductRow
            item={item}
            onPress={() =>
              navigation.navigate("Order-product", {
                productId: item.product_id,
              })
            }
          />
        )}
        showsVerticalScrollIndicator={false}
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

  center: {
    marginTop: 32,
  },

  error: {
    color: "#DC2626",
    marginVertical: 16,
  },

  productCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },

  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  productName: {
    fontWeight: "600",
    fontSize: 16,
  },

  quantity: {
    fontSize: 20,
    marginVertical: 8,
    fontWeight: "700",
  },

  progressBackground: {
    height: 6,
    backgroundColor: "#E5E7EB",
    borderRadius: 3,
    overflow: "hidden",
  },

  progressBar: {
    height: 6,
    borderRadius: 3,
  },

  metaRow: {
    marginTop: 6,
  },

  meta: {
    fontSize: 12,
    color: "#6B7280",
  },
});
