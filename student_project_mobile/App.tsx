// App.tsx
import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { AuthProvider, useAuth } from "./context/AuthContext";

// Screens
import LoginScreen from "./screens/LoginScreen";
import SignupScreen from "./screens/SignupScreen";
import AdminDashboard from "./screens/AdminDashboard";
import LecturerDashboard from "./screens/LecturerDashboard";
import StudentDashboard from "./screens/StudentDashboard";

// Define all available screens and their params
export type RootStackParamList = {
  Login: undefined;
  Signup: undefined;
  AdminDashboard: undefined;
  LecturerDashboard: undefined;
  StudentDashboard: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

// Handles conditional navigation based on user state
function AppNavigator() {
  const { user } = useAuth();

  // When no user is logged in → show auth screens
  if (!user) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Signup" component={SignupScreen} />
      </Stack.Navigator>
    );
  }

  // When user is logged in → show their dashboard
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user.role === "admin" && (
        <Stack.Screen name="AdminDashboard" component={AdminDashboard} />
      )}
      {user.role === "lecturer" && (
        <Stack.Screen
          name="LecturerDashboard"
          component={LecturerDashboard}
        />
      )}
      {user.role === "student" && (
        <Stack.Screen name="StudentDashboard" component={StudentDashboard} />
      )}

      {/* fallback screen to avoid empty stack */}
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
}

// Wrap app with AuthProvider & Navigation
export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}
