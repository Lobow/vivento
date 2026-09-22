import { apiClient } from "./client";

export async function listParticipants(eventId) {
  const { data } = await apiClient.get(`/events/${eventId}/participants`);
  return data;
}

export async function registerParticipant(eventId, payload) {
  const { data } = await apiClient.post(`/events/${eventId}/participants`, payload);
  return data;
}

export async function removeParticipant(eventId, participantId) {
  await apiClient.delete(`/events/${eventId}/participants/${participantId}`);
}
