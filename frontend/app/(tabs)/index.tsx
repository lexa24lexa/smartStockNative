import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import React from "react";
import Dashboard from "../../screens/Dashboard";
import Predictions from "../../screens/Predictions";
import Reports from "../../screens/Reports";
import Settings from "../../screens/Settings";
import Stock from "../../screens/Stock";

export type TabParamList = {
  Dashboard: undefined;
  Stock: undefined;
  Predictions: undefined;
  Reports: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<TabParamList>();

export default function TabNavigator() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Dashboard" component={Dashboard} />
      <Tab.Screen name="Stock" component={Stock} />
      <Tab.Screen name="Predictions" component={Predictions} />
      <Tab.Screen name="Reports" component={Reports} />
      <Tab.Screen name="Settings" component={Settings} />
    </Tab.Navigator>
  );
}
