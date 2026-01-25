import { router } from "expo-router";
import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Colors, Font, Spacing, Radius } from "../../constants/theme";

interface HeaderProps {
  onRefresh?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onRefresh }) => {
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      console.log("No refresh function provided");
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={() => router.push("/Dashboard")}>
        <Text style={styles.title}>Meroski</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={handleRefresh} style={styles.button} activeOpacity={0.7}>
        <Text style={styles.icon}>⟳</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: Spacing.m,
    backgroundColor: Colors.bgCard,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  title: { fontSize: 20, fontWeight: "bold", color: Colors.textPrimary },
  button: { padding: Spacing.s, borderRadius: Radius.small },
  icon: { fontSize: 20, color: Colors.primary },
});

export default Header;
