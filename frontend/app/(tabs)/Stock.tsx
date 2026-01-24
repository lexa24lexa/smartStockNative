import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { NavigationProp, ParamListBase, useNavigation } from "@react-navigation/native";
import Layout from "../../components/ui/Layout";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

// Stock status type
type StockStatus = "Stable" | "Low" | "Critical";

// Interface for each product in stock overview
interface StockOverview {
  product_id: number;
  product_name: string;
  total_quantity: number;
  status: StockStatus;
  progress: number;
  days_to_out_of_stock?: number | null;
  last_sale_at?: string | null;
  average_daily_sales?: number | null;
}

// Props for individual product row
interface ProductRowProps {
  item: StockOverview;
  onPress: () => void;
}

// Map status to color
function statusColor(status: StockStatus) {
  switch (status) {
    case "Critical":
      return Colors.danger;
    case "Low":
      return Colors.warning;
    default:
      return Colors.primary;
  }
}

// Format last sale date
function formatLastSale(date?: string | null) {
  if (!date) return "No sales yet";
  const d = new Date(date);
  return `Last sale: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

// Render single product row
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
      {/* Product name and status */}
      <View style={styles.row}>
        <Text style={Font.label}>{item.product_name}</Text>
        <Text style={{ color, fontWeight: "600" as const }}>● {item.status}</Text>
      </View>

      {/* Total quantity */}
      <Text style={[Font.title, { marginVertical: 8 }]}>{item.total_quantity}</Text>

      {/* Stock progress bar */}
      <View style={styles.progressBackground}>
        <View
          style={[
            styles.progressBar,
            { width: `${Math.round(item.progress * 100)}%`, backgroundColor: color },
          ]}
        />
      </View>

      {/* Meta info: days to out-of-stock & last sale */}
      <View style={styles.metaRow}>
        <Text style={Font.meta}>
          {item.days_to_out_of_stock != null
            ? `Days to OOS: ${item.days_to_out_of_stock}d`
            : "Days to OOS: —"}
        </Text>
        <Text style={Font.meta}>{formatLastSale(item.last_sale_at)}</Text>
        {item.average_daily_sales != null && (
          <Text style={Font.meta}>Avg daily sales: {item.average_daily_sales.toFixed(2)}</Text>
        )}
      </View>
    </Pressable>
  );
}

// Main Stock overview screen
export default function Stock() {
  const navigation = useNavigation<NavigationProp<ParamListBase>>();

  // State
  const [data, setData] = React.useState<StockOverview[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const STORE_ID = 1;

  // Load stock data on mount
  React.useEffect(() => {
  const load = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/stock/overview/${STORE_ID}`);
      if (!res.ok) throw new Error("Failed to load stock");
      const json = await res.json();

      const mapped: StockOverview[] = json.map((p: any) => ({
        ...p,
        average_daily_sales: p.average_daily_sales ?? 0,
      }));

      setData(mapped);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

    load();
  }, []);

  return (
    <Layout>
      {/* Page header */}
      <Text style={Font.subtitle}>Live inventory</Text>
      <Text style={Font.title}>Stock overview</Text>

      {/* Loading indicator */}
      {loading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      )}

      {/* Error message */}
      {error && <Text style={[Font.meta, { color: Colors.danger }]}>{error}</Text>}

      {/* Empty state */}
      {!loading && !error && data.length === 0 && (
        <Text style={Font.meta}>No stock available for this store.</Text>
      )}

      {/* Stock list */}
      <FlatList
        data={data}
        keyExtractor={(item) => item.product_id.toString()}
        renderItem={({ item }) => (
          <ProductRow
            item={item}
            onPress={() =>
              navigation.navigate("Order-product", { productId: item.product_id })
            }
          />
        )}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: Spacing.l }}
      />
    </Layout>
  );
}

const styles = StyleSheet.create({
  center: { marginTop: 32 },

  productCard: {
    backgroundColor: Colors.bgCard,
    padding: Spacing.m,
    borderRadius: Radius.card,
    marginBottom: Spacing.m,
  },

  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },

  progressBackground: {
    height: 6,
    backgroundColor: Colors.border,
    borderRadius: 3,
    overflow: "hidden",
  },

  progressBar: { height: 6, borderRadius: 3 },

  metaRow: { marginTop: 6 },
});
