import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  FlatList,
  Modal,
  ScrollView,
} from "react-native";
import { NavigationProp, ParamListBase, useNavigation } from "@react-navigation/native";
import Layout from "../../components/ui/Layout";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

type StockStatus = "Stable" | "Low" | "Critical";
type PriorityLevel = "High" | "Medium" | "Low";

interface StockOverview {
  product_id: number;
  product_name: string;
  total_quantity: number;
  status: StockStatus;
  progress: number;
  days_to_out_of_stock?: number | null;
  last_sale_at?: string | null;
  average_daily_sales?: number | null;
  replenishment_frequency?: number | null;
  next_replenishment_date?: string | null;
  quantity?: number | null;
  facing?: number | null;
}

interface ProductRowProps {
  item: StockOverview;
  onPress: () => void;
  onViewHistory: () => void;
}

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

function calculatePriority(item: StockOverview): PriorityLevel {
  if (item.status === "Critical") return "High";
  if (item.status === "Low") return "Medium";
  return "Low";
}

function formatLastSale(date?: string | null) {
  if (!date) return "No sales yet";
  const d = new Date(date);
  return `Last sale: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function ProductRow({ item, onPress, onViewHistory }: ProductRowProps) {
  const color = statusColor(item.status);
  const formatDate = (date?: string | null) => (date ? new Date(date).toLocaleDateString() : "—");
  const priority = calculatePriority(item);

  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.productCard, pressed && { opacity: 0.7 }]}
    >
      <View style={styles.row}>
        <Text style={Font.label}>{item.product_name}</Text>
        <Text style={{ color, fontWeight: "600" }}>● {item.status}</Text>
      </View>

      <Text style={[Font.title, { marginVertical: 8 }]}>{item.total_quantity}</Text>

      <View style={styles.progressBackground}>
        <View
          style={[
            styles.progressBar,
            { width: `${Math.round(item.progress * 100)}%`, backgroundColor: color },
          ]}
        />
      </View>

      <View style={styles.metaRow}>
        <Text style={Font.meta}>Days to OOS: {item.days_to_out_of_stock ?? "—"}</Text>
        <Text style={Font.meta}>{formatLastSale(item.last_sale_at)}</Text>
        <Text style={Font.meta}>Avg daily sales: {item.average_daily_sales?.toFixed(2) ?? "0.00"}</Text>
        <Text style={Font.meta}>
          Frequency: every {item.replenishment_frequency ?? "—"} day
          {item.replenishment_frequency && item.replenishment_frequency > 1 ? "s" : ""}
        </Text>
        <Text style={Font.meta}>Next replenishment: {formatDate(item.next_replenishment_date)}</Text>
        <Text style={Font.meta}>Suggested qty: {item.quantity ?? 0}</Text>
        <Text style={Font.meta}>Shelf facing: {item.facing ?? 0}</Text>
        <Text style={[Font.meta, { fontWeight: "700" }]}>Replenishment priority: {priority}</Text>

        {/* NEW: View History Button */}
        <Pressable
          onPress={onViewHistory}
          style={({ pressed }) => [
            styles.historyButton,
            pressed && { opacity: 0.7 },
          ]}
        >
          <Text style={styles.historyButtonText}>View Replenishment History</Text>
        </Pressable>
      </View>
    </Pressable>
  );
}

interface ReplenishmentHistoryItem {
  date: string;
  batch: string;
  expiration: string;
  quantity: number;
  user: string;
}

export default function Stock() {
  const navigation = useNavigation<NavigationProp<ParamListBase>>();
  const [data, setData] = React.useState<StockOverview[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [modalVisible, setModalVisible] = React.useState(false);
  const [history, setHistory] = React.useState<ReplenishmentHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = React.useState(false);
  const STORE_ID = 1;

  React.useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/stock/overview/${STORE_ID}`);
        if (!res.ok) throw new Error("Failed to load stock");
        const json = await res.json();

        const mapped: StockOverview[] = json.map((p: any) => ({
          ...p,
          average_daily_sales: p.average_daily_sales ?? 0,
          replenishment_frequency: p.replenishment_frequency ?? null,
          next_replenishment_date: p.next_replenishment_date ?? null,
          quantity: p.quantity ?? null,
          facing: p.facing ?? null,
        }));

        const sorted = mapped.sort((a, b) => {
          const priorityMap = { High: 3, Medium: 2, Low: 1 };
          return priorityMap[calculatePriority(b)] - priorityMap[calculatePriority(a)];
        });
        setData(sorted);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const viewHistory = async (productId: number) => {
    setModalVisible(true);
    setHistoryLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/replenishment-logs/${STORE_ID}/${productId}`);
      if (!res.ok) throw new Error("Failed to load history");
      const json = await res.json();

      const mapped: ReplenishmentHistoryItem[] = json.map((h: any) => ({
        date: h.timestamp,
        batch: `Batch ${h.batch_id}`,
        expiration: h.expiration_date,
        quantity: h.quantity,
        user: `User ${h.user_id}`,
      }));

      setHistory(mapped);
    } catch (e) {
      console.error(e);
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <Layout>
      <Text style={Font.subtitle}>Live inventory</Text>
      <Text style={Font.title}>Stock overview</Text>

      {loading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      )}

      {error && <Text style={[Font.meta, { color: Colors.danger }]}>{error}</Text>}

      {!loading && !error && data.length === 0 && (
        <Text style={Font.meta}>No stock available for this store.</Text>
      )}

      <FlatList
        data={data}
        keyExtractor={(item) => item.product_id.toString()}
        renderItem={({ item }) => (
          <ProductRow
            item={item}
            onPress={() => navigation.navigate("Order-product", { productId: item.product_id })}
            onViewHistory={() => viewHistory(item.product_id)}
          />
        )}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: Spacing.l }}
      />

      {/* NEW: Replenishment History Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <Layout>
          <Text style={[Font.title, { marginBottom: Spacing.m }]}>
            Replenishment History
          </Text>
          {historyLoading ? (
            <ActivityIndicator size="large" color={Colors.primary} />
          ) : history.length === 0 ? (
            <Text style={Font.meta}>No replenishment history found.</Text>
          ) : (
            <ScrollView>
              {history.map((h, idx) => (
                <View key={idx} style={styles.historyRow}>
                  <Text style={Font.label}>Date: {new Date(h.date).toLocaleString()}</Text>
                  <Text style={Font.meta}>Batch: {h.batch}</Text>
                  <Text style={Font.meta}>Expiration: {h.expiration}</Text>
                  <Text style={Font.meta}>Quantity: {h.quantity}</Text>
                  <Text style={Font.meta}>User: {h.user}</Text>
                </View>
              ))}
            </ScrollView>
          )}
          <Pressable
            onPress={() => setModalVisible(false)}
            style={styles.closeButton}
          >
            <Text style={styles.closeButtonText}>Close</Text>
          </Pressable>
        </Layout>
      </Modal>
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
  progressBackground: { height: 6, backgroundColor: Colors.border, borderRadius: 3, overflow: "hidden" },
  progressBar: { height: 6, borderRadius: 3 },
  metaRow: { marginTop: 6 },
  historyButton: {
    marginTop: Spacing.s,
    backgroundColor: Colors.secondary,
    paddingVertical: Spacing.s,
    borderRadius: Radius.small,
    alignItems: "center",
  },
  historyButtonText: {
    color: "#fff",
    fontWeight: "600",
  },
  historyRow: {
    backgroundColor: Colors.bgCard,
    padding: Spacing.m,
    borderRadius: Radius.card,
    marginBottom: Spacing.s,
  },
  closeButton: {
    marginTop: Spacing.m,
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.s,
    borderRadius: Radius.small,
    alignItems: "center",
  },
  closeButtonText: { color: "#fff", fontWeight: "700" },
});
