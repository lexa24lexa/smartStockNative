import React, { useState } from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, TextInput } from "react-native";
import Layout from "../../components/ui/Layout";

function PredictionCard({
  productName,
  currentStock,
  predictedStockout,
  suggestedQuantity,
  onOverride,
}: {
  productName: string;
  currentStock: number;
  predictedStockout: string;
  suggestedQuantity: number;
  onOverride: (newQty: number) => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [overrideValue, setOverrideValue] = useState(suggestedQuantity.toString());

  const handleSave = () => {
    onOverride(parseInt(overrideValue) || suggestedQuantity);
    setIsEditing(false);
  };

  return (
    <View style={styles.predictionCard}>
      <View style={styles.cardHeader}>
        <Text style={styles.productName}>{productName}</Text>
        <Text style={styles.stockoutBadge}>⚠️ {predictedStockout}</Text>
      </View>
      
      <View style={styles.cardBody}>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Current Stock:</Text>
          <Text style={styles.value}>{currentStock} units</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.label}>Suggested Replenishment:</Text>
          {isEditing ? (
            <View style={styles.editContainer}>
              <TextInput
                style={styles.input}
                value={overrideValue}
                onChangeText={setOverrideValue}
                keyboardType="numeric"
              />
              <TouchableOpacity onPress={handleSave} style={styles.saveBtn}>
                <Text style={styles.saveBtnText}>✓</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity onPress={() => setIsEditing(true)}>
              <Text style={[styles.value, styles.editable]}>{suggestedQuantity} units ✏️</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

export default function Predictions() {
  const [predictions, setPredictions] = useState([
    { id: 1, productName: "Coca Cola 500ml", currentStock: 12, predictedStockout: "In 2 days", suggestedQuantity: 48 },
    { id: 2, productName: "Croissant", currentStock: 5, predictedStockout: "Tomorrow", suggestedQuantity: 30 },
    { id: 3, productName: "Pain au chocolat", currentStock: 8, predictedStockout: "In 3 days", suggestedQuantity: 24 },
  ]);

  const handleOverride = (id: number, newQty: number) => {
    setPredictions(prev =>
      prev.map(p => (p.id === id ? { ...p, suggestedQuantity: newQty } : p))
    );
  };

  return (
    <Layout>
      <Text style={styles.title}>Predictions & Replenishment</Text>
      <Text style={styles.subtitle}>Automated daily replenishment suggestions</Text>

      <View style={styles.statsRow}>
        <View style={[styles.statBox, { backgroundColor: "#DC2626" }]}>
          <Text style={styles.statValue}>8</Text>
          <Text style={styles.statLabel}>Stockouts predicted</Text>
        </View>
        <View style={[styles.statBox, { backgroundColor: "#2563EB" }]}>
          <Text style={styles.statValue}>120</Text>
          <Text style={styles.statLabel}>Items to restock</Text>
        </View>
      </View>

      <ScrollView style={styles.listContainer}>
        {predictions.map(pred => (
          <PredictionCard
            key={pred.id}
            productName={pred.productName}
            currentStock={pred.currentStock}
            predictedStockout={pred.predictedStockout}
            suggestedQuantity={pred.suggestedQuantity}
            onOverride={(newQty) => handleOverride(pred.id, newQty)}
          />
        ))}
      </ScrollView>

      <TouchableOpacity style={styles.generateBtn}>
        <Text style={styles.generateBtnText}>Generate Replenishment List</Text>
      </TouchableOpacity>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold" },
  subtitle: { color: "#6B7280", marginBottom: 16 },

  statsRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  statBox: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#fff",
  },
  statLabel: {
    color: "#fff",
    marginTop: 4,
    fontSize: 12,
  },

  listContainer: {
    flex: 1,
  },

  predictionCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: "#DC2626",
  },

  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  productName: {
    fontSize: 16,
    fontWeight: "600",
  },
  stockoutBadge: {
    fontSize: 12,
    color: "#DC2626",
    fontWeight: "500",
  },

  cardBody: {
    gap: 8,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  label: {
    color: "#6B7280",
    fontSize: 14,
  },
  value: {
    fontSize: 14,
    fontWeight: "500",
  },
  editable: {
    color: "#2563EB",
  },

  editContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 6,
    padding: 6,
    width: 80,
    textAlign: "center",
  },
  saveBtn: {
    backgroundColor: "#059669",
    borderRadius: 6,
    padding: 6,
    width: 32,
    alignItems: "center",
  },
  saveBtnText: {
    color: "#fff",
    fontSize: 16,
  },

  generateBtn: {
    backgroundColor: "#059669",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 16,
  },
  generateBtnText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});