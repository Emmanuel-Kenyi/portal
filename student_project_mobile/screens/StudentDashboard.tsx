import React, { useEffect, useState } from "react";
import { View, Text, FlatList, ScrollView } from "react-native";
import { useAuth } from "../context/AuthContext";
import { apiGet } from "../utils/api";

interface Club { id: number; name: string; description: string; member_count: number; }
interface Event { id: number; title: string; club_name: string; date: string; location: string; }
interface Poll { id: number; question: string; club_name: string; total_votes: number; }
interface Post { id: number; title: string; club_name: string; author_name: string; }

export default function StudentDashboard() {
  const { user } = useAuth();
  const [clubs, setClubs] = useState<Club[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [polls, setPolls] = useState<Poll[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    if (!user) return;

    apiGet("clubs/", user.token).then(data => data && setClubs(data));
    apiGet("events/", user.token).then(data => data && setEvents(data));
    apiGet("polls/", user.token).then(data => data && setPolls(data));
    apiGet("posts/", user.token).then(data => data && setPosts(data));
  }, [user]);

  return (
    <ScrollView style={{ padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 10 }}>Your Clubs</Text>
      <FlatList
        data={clubs}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={{ padding: 10, borderWidth: 1, marginBottom: 5 }}>
            <Text style={{ fontWeight: "bold" }}>{item.name}</Text>
            <Text>{item.description}</Text>
            <Text>Members: {item.member_count}</Text>
          </View>
        )}
      />

      <Text style={{ fontSize: 24, fontWeight: "bold", marginVertical: 10 }}>Upcoming Events</Text>
      {events.map(e => (
        <View key={e.id} style={{ padding: 10, borderWidth: 1, marginBottom: 5 }}>
          <Text style={{ fontWeight: "bold" }}>{e.title}</Text>
          <Text>Club: {e.club_name}</Text>
          <Text>Date: {e.date}</Text>
          <Text>Location: {e.location}</Text>
        </View>
      ))}

      <Text style={{ fontSize: 24, fontWeight: "bold", marginVertical: 10 }}>Polls</Text>
      {polls.map(p => (
        <View key={p.id} style={{ padding: 10, borderWidth: 1, marginBottom: 5 }}>
          <Text style={{ fontWeight: "bold" }}>{p.question}</Text>
          <Text>Club: {p.club_name}</Text>
          <Text>Total Votes: {p.total_votes}</Text>
        </View>
      ))}

      <Text style={{ fontSize: 24, fontWeight: "bold", marginVertical: 10 }}>Posts</Text>
      {posts.map(post => (
        <View key={post.id} style={{ padding: 10, borderWidth: 1, marginBottom: 5 }}>
          <Text style={{ fontWeight: "bold" }}>{post.title}</Text>
          <Text>Club: {post.club_name}</Text>
          <Text>Author: {post.author_name}</Text>
        </View>
      ))}
    </ScrollView>
  );
}
