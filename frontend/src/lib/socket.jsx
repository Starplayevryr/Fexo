import { io } from "socket.io-client";

const SOCKET_URL = "http://127.0.0.1:8000"; // same as your FastAPI backend

// Create socket instance
export const socket = io(SOCKET_URL, {
  transports: ["websocket"],
  autoConnect: true,
});
