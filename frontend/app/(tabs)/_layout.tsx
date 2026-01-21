import { Tabs } from "expo-router";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#059669",
        tabBarInactiveTintColor: "#6B7280",
      }}
    >
      <Tabs.Screen
        name="Dashboard"
        options={{
          title: "Dashboard",
          tabBarLabel: "Dashboard",
        }}
      />
      <Tabs.Screen
        name="Stock"
        options={{ title: "Stock", tabBarLabel: "Stock" }}
      />
      <Tabs.Screen
        name="Predictions"
        options={{ title: "Predictions", tabBarLabel: "Predictions" }}
      />
      <Tabs.Screen
        name="Reports"
        options={{ title: "Reports", tabBarLabel: "Reports" }}
      />
      <Tabs.Screen
        name="Settings"
        options={{ title: "Settings", tabBarLabel: "Settings" }}
      />
    </Tabs>
  );
}
