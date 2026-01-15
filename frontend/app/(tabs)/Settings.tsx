import React, { useState } from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, TextInput } from "react-native";
import Layout from "../../components/ui/Layout";

function SettingRow({
  label,
  value,
  onPress,
  helpText,
}: {
  label: string;
  value: string;
  onPress?: () => void;
  helpText?: string;
}) {
  return (
    <TouchableOpacity style={styles.settingRow} onPress={onPress} disabled={!onPress}>
      <View style={styles.settingContent}>
        <View style={styles.labelContainer}>
          <Text style={styles.settingLabel}>{label}</Text>
          {helpText && (
            <TouchableOpacity style={styles.helpIcon}>
              <Text style={styles.helpIconText}>ℹ️</Text>
            </TouchableOpacity>
          )}
        </View>
        {helpText && <Text style={styles.helpText}>{helpText}</Text>}
      </View>
      <Text style={styles.settingValue}>{value}</Text>
    </TouchableOpacity>
  );
}

function CategorySettingCard({
  category,
  minStock,
  facing,
  onUpdateMinStock,
  onUpdateFacing,
}: {
  category: string;
  minStock: number;
  facing: number;
  onUpdateMinStock: (value: number) => void;
  onUpdateFacing: (value: number) => void;
}) {
  const [editingMin, setEditingMin] = useState(false);
  const [editingFacing, setEditingFacing] = useState(false);
  const [minValue, setMinValue] = useState(minStock.toString());
  const [facingValue, setFacingValue] = useState(facing.toString());

  return (
    <View style={styles.categoryCard}>
      <Text style={styles.categoryName}>{category}</Text>
      
      <View style={styles.categorySettings}>
        <View style={styles.categorySetting}>
          <Text style={styles.categoryLabel}>Min. Stock</Text>
          {editingMin ? (
            <View style={styles.editRow}>
              <TextInput
                style={styles.smallInput}
                value={minValue}
                onChangeText={setMinValue}
                keyboardType="numeric"
              />
              <TouchableOpacity
                onPress={() => {
                  onUpdateMinStock(parseInt(minValue) || minStock);
                  setEditingMin(false);
                }}
                style={styles.miniSaveBtn}
              >
                <Text style={styles.miniSaveBtnText}>✓</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity onPress={() => setEditingMin(true)}>
              <Text style={styles.categoryValue}>{minStock} ✏️</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.categorySetting}>
          <Text style={styles.categoryLabel}>Facing</Text>
          {editingFacing ? (
            <View style={styles.editRow}>
              <TextInput
                style={styles.smallInput}
                value={facingValue}
                onChangeText={setFacingValue}
                keyboardType="numeric"
              />
              <TouchableOpacity
                onPress={() => {
                  onUpdateFacing(parseInt(facingValue) || facing);
                  setEditingFacing(false);
                }}
                style={styles.miniSaveBtn}
              >
                <Text style={styles.miniSaveBtnText}>✓</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity onPress={() => setEditingFacing(true)}>
              <Text style={styles.categoryValue}>{facing} ✏️</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

export default function Settings() {
  const [replenishmentFreq, setReplenishmentFreq] = useState(2);
  const [categories, setCategories] = useState([
    { id: 1, name: "Beverages", minStock: 50, facing: 3 },
    { id: 2, name: "Dairy", minStock: 30, facing: 2 },
    { id: 3, name: "Bakery", minStock: 20, facing: 4 },
  ]);

  const handleFrequencyChange = (freq: number) => {
    setReplenishmentFreq(freq);
  };

  const updateCategoryMinStock = (id: number, value: number) => {
    setCategories(prev =>
      prev.map(cat => (cat.id === id ? { ...cat, minStock: value } : cat))
    );
  };

  const updateCategoryFacing = (id: number, value: number) => {
    setCategories(prev =>
      prev.map(cat => (cat.id === id ? { ...cat, facing: value } : cat))
    );
  };

  return (
    <Layout>
      <Text style={styles.title}>Settings</Text>
      <Text style={styles.subtitle}>Configure inventory parameters</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Replenishment Frequency</Text>
        <Text style={styles.sectionDesc}>
          How often should replenishment be calculated?
        </Text>
        
        <View style={styles.frequencyButtons}>
          {[1, 2, 3].map(freq => (
            <TouchableOpacity
              key={freq}
              style={[
                styles.freqBtn,
                replenishmentFreq === freq && styles.freqBtnActive,
              ]}
              onPress={() => handleFrequencyChange(freq)}
            >
              <Text
                style={[
                  styles.freqBtnText,
                  replenishmentFreq === freq && styles.freqBtnTextActive,
                ]}
              >
                {freq} {freq === 1 ? "day" : "days"}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>General Settings</Text>
        <SettingRow
          label="Default Language"
          value="English"
          onPress={() => {}}
        />
        <SettingRow
          label="Time Zone"
          value="Europe/Paris"
          onPress={() => {}}
        />
        <SettingRow
          label="Currency"
          value="EUR (€)"
          onPress={() => {}}
        />
      </View>

      <Text style={styles.sectionTitle}>Category Configuration</Text>
      <Text style={styles.sectionDesc}>
        Set minimum stock levels and facing per category
      </Text>
      
      <ScrollView style={styles.categoriesContainer}>
        {categories.map(cat => (
          <CategorySettingCard
            key={cat.id}
            category={cat.name}
            minStock={cat.minStock}
            facing={cat.facing}
            onUpdateMinStock={(value) => updateCategoryMinStock(cat.id, value)}
            onUpdateFacing={(value) => updateCategoryFacing(cat.id, value)}
          />
        ))}
      </ScrollView>

      <TouchableOpacity style={styles.saveAllBtn}>
        <Text style={styles.saveAllBtnText}>Save All Settings</Text>
      </TouchableOpacity>
    </Layout>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "bold" },
  subtitle: { color: "#6B7280", marginBottom: 16 },

  section: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8,
  },
  sectionDesc: {
    color: "#6B7280",
    fontSize: 13,
    marginBottom: 12,
  },

  frequencyButtons: {
    flexDirection: "row",
    gap: 8,
  },
  freqBtn: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#D1D5DB",
    alignItems: "center",
  },
  freqBtnActive: {
    backgroundColor: "#059669",
    borderColor: "#059669",
  },
  freqBtnText: {
    color: "#6B7280",
    fontWeight: "500",
  },
  freqBtnTextActive: {
    color: "#fff",
  },

  settingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#F3F4F6",
  },
  settingContent: {
    flex: 1,
  },
  labelContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: "500",
  },
  helpIcon: {
    width: 18,
    height: 18,
  },
  helpIconText: {
    fontSize: 12,
  },
  helpText: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
  },
  settingValue: {
    color: "#2563EB",
    fontSize: 14,
  },

  categoriesContainer: {
    maxHeight: 300,
  },

  categoryCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  categoryName: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 12,
  },
  categorySettings: {
    flexDirection: "row",
    gap: 16,
  },
  categorySetting: {
    flex: 1,
  },
  categoryLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 4,
  },
  categoryValue: {
    fontSize: 16,
    fontWeight: "500",
    color: "#2563EB",
  },
  editRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  smallInput: {
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 6,
    padding: 4,
    width: 60,
    textAlign: "center",
  },
  miniSaveBtn: {
    backgroundColor: "#059669",
    borderRadius: 6,
    padding: 4,
    width: 24,
    alignItems: "center",
  },
  miniSaveBtnText: {
    color: "#fff",
    fontSize: 14,
  },

  saveAllBtn: {
    backgroundColor: "#059669",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 16,
  },
  saveAllBtnText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});