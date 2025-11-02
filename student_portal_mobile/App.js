import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from './src/screens/LoginScreen';
import AdminDashboardScreen from './src/screens/AdminDashboardScreen';
import LecturerDashboardScreen from './src/screens/LecturerDashboardScreen';
import StudentDashboardScreen from './src/screens/StudentDashboardScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="AdminDashboard" component={AdminDashboardScreen} />
        <Stack.Screen name="LecturerDashboard" component={LecturerDashboardScreen} />
        <Stack.Screen name="StudentDashboard" component={StudentDashboardScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
