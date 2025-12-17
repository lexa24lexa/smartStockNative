import { NavigationProp, ParamListBase, useNavigation } from "@react-navigation/native";
import React from "react";
import { Platform, StyleSheet, Text, TouchableOpacity, View } from "react-native";

interface HeaderProps {
  onRefresh?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onRefresh }) => {
  const navigation = useNavigation<NavigationProp<ParamListBase>>();

  const handleRefresh = () => {
    if (Platform.OS === "web") {
      // Reset the current route to trigger a re-render without full page reload
      const state = navigation.getState();
      const currentRoute = state.routes[state.index]?.name;

      if (currentRoute) {
        navigation.reset({
          index: 0,
          routes: [{ name: currentRoute }],
        });
      }
    } else if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>SmartStock</Text>
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
