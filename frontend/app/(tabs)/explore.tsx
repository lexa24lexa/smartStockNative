import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import Layout from "../../components/ui/Layout";

export default function Explore() {
  return (
    <Layout>
      <View style={styles.content}>
        <Text>Explore Screen</Text>
      </View>
    </Layout>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
