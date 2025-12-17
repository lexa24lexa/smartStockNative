import React, { ReactNode } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import Header from "./Header";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <View style={styles.container}>
      <Header />
      <ScrollView style={styles.main}>{children}</ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  main: { flex: 1, padding: 16, backgroundColor: "#f3f4f6" },
});
