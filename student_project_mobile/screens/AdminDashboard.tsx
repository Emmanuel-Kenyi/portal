import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
} from "react-native";
import { useAuth, User as AuthUser } from "../context/AuthContext";
import { apiGet } from "../utils/api";

// We use intersection type instead of extending
// so username can remain optional without TypeScript errors
type UserWithUsername = AuthUser & { username?: string };

// Define Stats shape
interface Stats {
  total_users: number;
  total_clubs: number;
  total_events: number;
  total_posts: number;
}

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const currentUser = user as UserWithUsername; // cast user to include optional username
  const [stats, setStats] = useState<Stats>({
    total_users: 0,
    total_clubs: 0,
    total_events: 0,
    total_posts: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentUser) return;

    const fetchStats = async () => {
      try {
        setLoading(true);

        const [users, clubs, events, posts] = await Promise.all([
          apiGet("users/count/", currentUser.token),
          apiGet("clubs/count/", currentUser.token),
          apiGet("events/count/", currentUser.token),
          apiGet("posts/count/", currentUser.token),
        ]);

        setStats({
          total_users: users?.count ?? 0,
          total_clubs: clubs?.count ?? 0,
          total_events: events?.count ?? 0,
          total_posts: posts?.count ?? 0,
        });
      } catch (error) {
        console.error("Error fetching stats:", error);
        Alert.alert("Error", "Unable to fetch admin statistics.");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [currentUser]);

  if (!currentUser || loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#4e73df" />
        <Text style={styles.loadingText}>
          {currentUser ? "Fetching dashboard data..." : "Loading user data..."}
        </Text>
      </View>
    );
  }

  const handleGenerateReport = () =>
    Alert.alert("📊 Report", "Generating Clubs Report...");
  const handleDownloadReport = () =>
    Alert.alert("✅ Download", "Downloading Latest Report...");

  const quickActions = [
    { id: 1, title: "Manage Clubs", icon: "🏛", color: "#4e73df" },
    { id: 2, title: "Manage Users", icon: "👥", color: "#1cc88a" },
    { id: 3, title: "Manage Posts", icon: "📝", color: "#f6c23e" },
    { id: 4, title: "Reports", icon: "📊", color: "#36b9cc" },
    { id: 5, title: "Settings", icon: "⚙️", color: "#858796" },
    { id: 6, title: "Moderation", icon: "🗑️", color: "#e74a3b" },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.welcome}>
          👋 Welcome, {currentUser.username ?? "Admin"}
        </Text>
        <Text style={styles.subtitle}>
          Full system management and administrative controls
        </Text>
      </View>

      {/* Stats Section */}
      <View style={styles.statsGrid}>
        <View style={[styles.statCard, { backgroundColor: "#4e73df" }]}>
          <Text style={styles.statNumber}>{stats.total_users}</Text>
          <Text style={styles.statLabel}>Total Users</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: "#1cc88a" }]}>
          <Text style={styles.statNumber}>{stats.total_clubs}</Text>
          <Text style={styles.statLabel}>Total Clubs</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: "#f6c23e" }]}>
          <Text style={styles.statNumber}>{stats.total_events}</Text>
          <Text style={styles.statLabel}>Total Events</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: "#36b9cc" }]}>
          <Text style={styles.statNumber}>{stats.total_posts}</Text>
          <Text style={styles.statLabel}>Total Posts</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <Text style={styles.sectionTitle}>Admin Quick Actions</Text>
      <FlatList
        data={quickActions}
        keyExtractor={(item) => item.id.toString()}
        numColumns={2}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: item.color }]}
            onPress={() => Alert.alert(item.title, `Opening ${item.title}...`)}
          >
            <Text style={styles.actionIcon}>{item.icon}</Text>
            <Text style={styles.actionTitle}>{item.title}</Text>
          </TouchableOpacity>
        )}
        scrollEnabled={false}
      />

      {/* Reports Section */}
      <View style={styles.reportSection}>
        <Text style={styles.sectionTitle}>📊 Reports</Text>
        <TouchableOpacity
          style={[styles.btn, { backgroundColor: "#4e73df" }]}
          onPress={handleGenerateReport}
        >
          <Text style={styles.btnText}>Generate Clubs Report</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btn, { backgroundColor: "#1cc88a" }]}
          onPress={handleDownloadReport}
        >
          <Text style={styles.btnText}>Download Latest Report</Text>
        </TouchableOpacity>
      </View>

      {/* Logout Button */}
      <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
        <Text style={styles.logoutText}>🚪 Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#f8f9fc" },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  loadingText: { marginTop: 10, fontSize: 16, color: "#6c757d" },
  header: { marginBottom: 20 },
  welcome: { fontSize: 24, fontWeight: "bold", color: "#2e2e2e" },
  subtitle: { fontSize: 14, color: "#6c757d", marginTop: 4 },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },
  statCard: {
    width: "47%",
    padding: 20,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: "center",
  },
  statNumber: { fontSize: 28, fontWeight: "bold", color: "#fff" },
  statLabel: { fontSize: 14, color: "#fff" },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginTop: 20,
    marginBottom: 10,
  },
  actionCard: {
    flex: 1,
    margin: 6,
    borderRadius: 12,
    padding: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  actionIcon: { fontSize: 36 },
  actionTitle: { marginTop: 8, color: "#fff", fontWeight: "600" },
  reportSection: { marginTop: 20 },
  btn: { borderRadius: 10, padding: 14, alignItems: "center", marginVertical: 6 },
  btnText: { color: "#fff", fontWeight: "600" },
  logoutBtn: {
    marginTop: 30,
    padding: 14,
    backgroundColor: "#e74a3b",
    borderRadius: 10,
    alignItems: "center",
  },
  logoutText: { color: "#fff", fontWeight: "bold" },
});
