// frontend/app/components/ui/Tooltip.tsx

import React, { useState, useEffect } from "react";
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  Modal, 
  ScrollView,
  ActivityIndicator 
} from "react-native";
import { helpService, HelpData } from "../../app/services/helpService";

interface TooltipProps {
  metricKey: string;
  inline?: boolean;
}

export function Tooltip({ metricKey, inline = false }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const [helpData, setHelpData] = useState<HelpData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHelpData();
  }, [metricKey]);

  const loadHelpData = async () => {
    setLoading(true);
    const data = await helpService.getHelp(metricKey);
    setHelpData(data);
    setLoading(false);
  };

  if (loading) {
    return (
      <View style={styles.helpIcon}>
        <ActivityIndicator size="small" color="#6B7280" />
      </View>
    );
  }

  if (!helpData) {
    return null;
  }

  if (inline) {
    // Version inline (pour petits tooltips)
    return (
      <View style={styles.inlineContainer}>
        <TouchableOpacity
          style={styles.inlineIcon}
          onPress={() => setVisible(!visible)}
        >
          <Text style={styles.iconText}>ℹ️</Text>
        </TouchableOpacity>
        
        {visible && (
          <View style={styles.inlineTooltip}>
            <Text style={styles.inlineText}>{helpData.description}</Text>
            {helpData.formula && (
              <Text style={styles.inlineFormula}>
                Formula: {helpData.formula}
              </Text>
            )}
          </View>
        )}
      </View>
    );
  }

  // Version modal (pour tooltips détaillés)
  return (
    <>
      <TouchableOpacity
        style={styles.helpIcon}
        onPress={() => setVisible(true)}
      >
        <Text style={styles.iconText}>ℹ️</Text>
      </TouchableOpacity>

      <Modal
        visible={visible}
        transparent
        animationType="fade"
        onRequestClose={() => setVisible(false)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setVisible(false)}
        >
          <TouchableOpacity 
            activeOpacity={1} 
            style={styles.modalContent}
            onPress={(e) => e.stopPropagation()}
          >
            <ScrollView showsVerticalScrollIndicator={false}>
              <Text style={styles.modalTitle}>{helpData.title}</Text>
              
              <Text style={styles.modalDescription}>
                {helpData.description}
              </Text>

              {helpData.formula && (
                <View style={styles.formulaSection}>
                  <Text style={styles.sectionLabel}>Formula:</Text>
                  <Text style={styles.formulaText}>{helpData.formula}</Text>
                </View>
              )}

              {helpData.example && (
                <View style={styles.exampleSection}>
                  <Text style={styles.sectionLabel}>Example:</Text>
                  <Text style={styles.exampleText}>{helpData.example}</Text>
                </View>
              )}

              {helpData.why && (
                <View style={styles.whySection}>
                  <Text style={styles.sectionLabel}>Why it matters:</Text>
                  <Text style={styles.whyText}>{helpData.why}</Text>
                </View>
              )}

              {helpData.options && (
                <View style={styles.optionsSection}>
                  <Text style={styles.sectionLabel}>Options:</Text>
                  {helpData.options.map((option, index) => (
                    <Text key={index} style={styles.optionText}>
                      • {option}
                    </Text>
                  ))}
                </View>
              )}

              {helpData.threshold && (
                <View style={styles.thresholdSection}>
                  <Text style={styles.sectionLabel}>Threshold:</Text>
                  <Text style={styles.thresholdText}>{helpData.threshold}</Text>
                </View>
              )}

              {helpData.action && (
                <View style={styles.actionSection}>
                  <Text style={styles.sectionLabel}>Recommended Action:</Text>
                  <Text style={styles.actionText}>{helpData.action}</Text>
                </View>
              )}

              {helpData.impact && (
                <View style={styles.impactSection}>
                  <Text style={styles.sectionLabel}>Impact:</Text>
                  <Text style={styles.impactText}>{helpData.impact}</Text>
                </View>
              )}

              {helpData.purpose && (
                <View style={styles.purposeSection}>
                  <Text style={styles.sectionLabel}>Purpose:</Text>
                  <Text style={styles.purposeText}>{helpData.purpose}</Text>
                </View>
              )}
            </ScrollView>

            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setVisible(false)}
            >
              <Text style={styles.closeButtonText}>Got it!</Text>
            </TouchableOpacity>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </>
  );
}

// Composant wrapper pour ajouter facilement un tooltip à un label
export function LabelWithTooltip({
  label,
  metricKey,
  inline = false,
  labelStyle,
}: {
  label: string;
  metricKey: string;
  inline?: boolean;
  labelStyle?: any;
}) {
  return (
    <View style={styles.labelContainer}>
      <Text style={[styles.label, labelStyle]}>{label}</Text>
      <Tooltip metricKey={metricKey} inline={inline} />
    </View>
  );
}

const styles = StyleSheet.create({
  helpIcon: {
    width: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  iconText: {
    fontSize: 16,
  },

  // Inline tooltip styles
  inlineContainer: {
    position: "relative",
  },
  inlineIcon: {
    width: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  inlineTooltip: {
    position: "absolute",
    top: 25,
    right: 0,
    backgroundColor: "#1F2937",
    padding: 12,
    borderRadius: 8,
    width: 220,
    zIndex: 1000,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  inlineText: {
    color: "#fff",
    fontSize: 12,
    lineHeight: 16,
  },
  inlineFormula: {
    color: "#D1D5DB",
    fontSize: 11,
    marginTop: 6,
    fontStyle: "italic",
  },

  // Modal tooltip styles
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 24,
    width: "85%",
    maxWidth: 400,
    maxHeight: "80%",
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 12,
    color: "#1F2937",
  },
  modalDescription: {
    fontSize: 14,
    color: "#4B5563",
    lineHeight: 20,
    marginBottom: 16,
  },

  // Section styles
  formulaSection: {
    backgroundColor: "#F3F4F6",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  exampleSection: {
    backgroundColor: "#EFF6FF",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  whySection: {
    backgroundColor: "#FEF3C7",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  optionsSection: {
    backgroundColor: "#F3F4F6",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  thresholdSection: {
    backgroundColor: "#FEE2E2",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  actionSection: {
    backgroundColor: "#DCFCE7",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  impactSection: {
    backgroundColor: "#E0E7FF",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  purposeSection: {
    backgroundColor: "#F3F4F6",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },

  sectionLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: "#6B7280",
    marginBottom: 4,
  },
  formulaText: {
    fontSize: 13,
    color: "#1F2937",
    fontFamily: "monospace",
  },
  exampleText: {
    fontSize: 13,
    color: "#1E40AF",
  },
  whyText: {
    fontSize: 13,
    color: "#92400E",
  },
  optionText: {
    fontSize: 13,
    color: "#1F2937",
    marginLeft: 8,
    marginVertical: 2,
  },
  thresholdText: {
    fontSize: 13,
    color: "#991B1B",
  },
  actionText: {
    fontSize: 13,
    color: "#166534",
  },
  impactText: {
    fontSize: 13,
    color: "#3730A3",
  },
  purposeText: {
    fontSize: 13,
    color: "#1F2937",
  },

  closeButton: {
    backgroundColor: "#059669",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 16,
  },
  closeButtonText: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "600",
  },

  // Label with tooltip
  labelContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  label: {
    fontSize: 14,
    fontWeight: "500",
    color: "#1F2937",
  },
});