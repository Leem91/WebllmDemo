const API = "http://localhost:8000/api";

async function get(path) {
  const r = await fetch(API + path);
  return r.json();
}

async function post(path, body) {
  const r = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

async function put(path, body) {
  const opts = { method: "PUT" };
  if (body) {
    opts.headers = { "Content-Type": "application/json" };
    opts.body = JSON.stringify(body);
  }
  const r = await fetch(API + path, opts);
  return r.json();
}

async function del(path) {
  await fetch(API + path, { method: "DELETE" });
}

export const api = {
  // Overview & KPI
  getOverview: () => get("/overview"),
  getKpiTrend: (days = 30) => get(`/kpi/trend?days=${days}`),
  getKpiPerformance: () => get("/kpi/performance"),

  // Patrons
  listPatrons: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/patrons?${q}`);
  },
  getPatron: (id) => get(`/patrons/${id}`),
  getPatronTimeline: (id, days = 30) => get(`/patrons/${id}/timeline?days=${days}`),
  getPatronOperations: (id) => get(`/patrons/${id}/operations`),

  // Campaigns & Hosts
  listCampaigns: () => get("/campaigns"),
  listHosts: () => get("/hosts"),
  getHost: (id) => get(`/hosts/${id}`),

  // Tasks
  listTasks: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/tasks?${q}`);
  },
  updateTaskStatus: (id, status) => put(`/tasks/${id}/status?status=${status}`),

  // Simulation Lab
  runSimulation: (body) => post("/simulation/run", body),
  getSimulationHistory: () => get("/simulation/history?limit=10"),

  // Chat (AI Copilot)
  listConversations: () => get("/chat/conversations"),
  createConversation: (title) => post("/chat/conversations", { title }),
  addMessage: (id, role, content) => post(`/chat/conversations/${id}/messages`, { role, content }),
  getMessages: (id) => get(`/chat/conversations/${id}/messages`),
  deleteConversation: (id) => del(`/chat/conversations/${id}`),

  // Comp Transactions
  listComps: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/comps?${q}`);
  },
  issueComp: (body) => post("/comps", body),
  redeemComp: (id) => put(`/comps/${id}/redeem`),
  cancelComp: (id) => put(`/comps/${id}/cancel`),

  // Rooms
  listRooms: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/rooms?${q}`);
  },
  roomAvailability: (checkIn, checkOut) => get(`/rooms/availability?check_in=${checkIn}&check_out=${checkOut}`),

  // Room Bookings
  listBookings: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/bookings?${q}`);
  },
  createBooking: (body) => post("/bookings", body),
  cancelBooking: (id) => put(`/bookings/${id}/cancel`),

  // F&B Reservations
  listFB: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/fb?${q}`);
  },
  createFB: (body) => post("/fb", body),
  cancelFB: (id) => put(`/fb/${id}/cancel`),

  // Credit Lines
  listCredit: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/credit?${q}`);
  },
  getPatronCredit: (patronId) => get(`/credit/${patronId}`),
  createCredit: (body) => post("/credit", body),

  // AI Actions
  listActions: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/actions?${q}`);
  },
  approveAction: (id, approvedBy) => put(`/actions/${id}/approve`, { approved_by: approvedBy }),
  dismissAction: (id) => put(`/actions/${id}/dismiss`),
  executeAction: (id) => put(`/actions/${id}/execute`),

  // Live Events
  listEvents: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/events?${q}`);
  },

  // Copilot Data Context
  getCopilotContext: () => get("/copilot/context"),

  // Simulation Engine Control
  startSim: () => post("/sim/start"),
  stopSim: () => post("/sim/stop"),
  getSimStatus: () => get("/sim/status"),
  setSimSpeed: (speed) => post(`/sim/speed?speed=${speed}`),

  // SSE stream URL
  sseUrl: () => API + "/sim/stream",
};
