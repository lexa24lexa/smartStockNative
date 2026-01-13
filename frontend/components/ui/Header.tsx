import { router } from "expo-router";
import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

interface HeaderProps {
  onRefresh?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onRefresh }) => {
  const handleRefresh = () => {
    if (onRefresh) onRefresh();
  };

  return (
    <View style={styles.container}>
      {/* Aqui: clicar em Meroski leva para a Dashboard */}
      <TouchableOpacity onPress={() => router.push("/Dashboard")}>
        <Text style={styles.title}>Meroski</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={handleRefresh} style={styles.button}>
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
    padding: 16,
    backgroundColor: "#fff",
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  title: { fontSize: 20, fontWeight: "bold" },
  button: { padding: 8, borderRadius: 6 },
  icon: { fontSize: 20 },
});

export default Header;
