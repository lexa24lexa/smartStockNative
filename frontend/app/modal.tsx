import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import Layout from "../components/ui/Layout";

export default function ModalScreen() {
  return (
    <Layout>
      <View style={styles.content}>
        <Text>Modal Screen</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
