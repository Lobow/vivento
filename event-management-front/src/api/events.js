import { apiClient } from "./client";

export async function listEvents({ status, date } = {}) {
  const params = {};
  if (status) params.status = status;
  if (date) params.date = date;
  const { data } = await apiClient.get("/events", { params });
  return data;
}

export async function getEvent(eventId) {
  const { data } = await apiClient.get(`/events/${eventId}`);
  return data;
}

export async function getEventImage(eventId) {
    const { data } = await apiClient.get(`/events/${eventId}/image`,{ responseType: "blob" });
    return data;
}
export async function createEvent(payload) {
    const formData = new FormData();
    
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });

  const { data } = await apiClient.post("/events", formData);
  return data;
}

export async function updateEvent(eventId, payload) {
    const formData = new FormData();
    
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });
  const { data } = await apiClient.put(`/events/${eventId}`, formData);
  return data;
}

export async function deleteEvent(eventId) {
  await apiClient.delete(`/events/${eventId}`);
}
