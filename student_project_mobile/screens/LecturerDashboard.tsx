import React, { useEffect, useState } from "react";
import { View, Text, FlatList, ScrollView, TouchableOpacity, Alert, ActivityIndicator, StyleSheet } from "react-native";
import { useAuth } from "../context/AuthContext";
import { apiGet } from "../utils/api";

interface Club { id: number; name: string; description: string; member_count: number; }
interface Event { id: number; title: string; club_name: string; date: string; location: string; }
interface Poll { id: number; question: string; club_name: string; total_votes: number; }
interface Post { id: number; title: string; club_name: string; author_name: string; }

export default function LecturerDashboard() {
  const { user } = useAuth();
  const [clubs, setClubs] = useState<Club[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [polls, setPolls] = useState<Poll[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState({
    total_clubs: 0,
    total_students: 0,
    active_polls_count: 0,
    upcoming_events_count: 0,
  });

  useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const [clubsData, eventsData, pollsData, postsData, totalStudentsData] = await Promise.all([
          apiGet("clubs/", user.token),
          apiGet("events/", user.token),
          apiGet("polls/", user.token),
          apiGet("posts/", user.token),
          apiGet("students/count/", user.token),
        ]);

        setClubs(clubsData || []);
        setEvents(eventsData || []);
        setPolls(pollsData || []);
        setPosts(postsData || []);

        setStats({
          total_clubs: clubsData?.length || 0,
          total_students: totalStudentsData?.count || 0,
          active_polls_count: pollsData?.length || 0,
          upcoming_events_count: eventsData?.length || 0,
        });
      } catch (error) {
        console.error("Error fetching lecturer dashboard data:", error);
        Alert.alert("Error", "Unable to fetch dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (!user || loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#4e73df" />
        <Text style={{ marginTop: 10 }}>
          {user ? "Fetching dashboard data..." : "Loading user data..."}
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ padding: 16 }}>
      <Text style={styles.welcome}>👋 Welcome, {user.name || user.username}</Text>
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.total_clubs}</Text>
          <Text>Total Clubs</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.total_students}</Text>
          <Text>Total Students</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.upcoming_events_count}</Text>
          <Text>Upcoming Events</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.active_polls_count}</Text>
          <Text>Active Polls</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Managed Clubs</Text>
      <FlatList
        data={clubs}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.itemCard}>
            <Text style={styles.itemTitle}>{item.name}</Text>
            <Text>{item.description}</Text>
            <Text>Members: {item.member_count}</Text>
          </View>
        )}
      />

      <Text style={styles.sectionTitle}>Upcoming Events</Text>
      {events.map((e) => (
        <View key={e.id} style={styles.itemCard}>
          <Text style={styles.itemTitle}>{e.title}</Text>
          <Text>Club: {e.club_name}</Text>
          <Text>Date: {e.date}</Text>
          <Text>Location: {e.location}</Text>
        </View>
      ))}

      <Text style={styles.sectionTitle}>Active Polls</Text>
      {polls.map((p) => (
        <View key={p.id} style={styles.itemCard}>
          <Text style={styles.itemTitle}>{p.question}</Text>
          <Text>Club: {p.club_name}</Text>
          <Text>Total Votes: {p.total_votes}</Text>
        </View>
      ))}

      <Text style={styles.sectionTitle}>Recent Posts</Text>
      {posts.map((post) => (
        <View key={post.id} style={styles.itemCard}>
          <Text style={styles.itemTitle}>{post.title}</Text>
          <Text>Club: {post.club_name}</Text>
          <Text>Author: {post.author_name}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  welcome: { fontSize: 24, fontWeight: "bold", marginBottom: 16 },
  statsRow: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between", marginBottom: 20 },
  statCard: { width: "48%", padding: 16, borderRadius: 12, backgroundColor: "#f1f3f6", alignItems: "center", marginBottom: 10 },
  statNumber: { fontSize: 22, fontWeight: "bold", marginBottom: 4 },
  sectionTitle: { fontSize: 20, fontWeight: "bold", marginVertical: 10 },
  itemCard: { padding: 12, borderWidth: 1, borderColor: "#ddd", borderRadius: 10, marginBottom: 8 },
  itemTitle: { fontWeight: "bold", marginBottom: 4 },
});
